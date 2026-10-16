# Running this pipeline

The launch files in this repository are **not self-contained**. They expect an
external ROS 2 package called **`ir_launch`**, which was provided by the course
and is not included here (it is also absent from the original repository — its
`src/ir_2526/` directory is listed in the original `.gitignore`).

This document records exactly what that external launch must provide, derived from
reading the nodes, so the pipeline can be reproduced against a standard
`turtlebot3_gazebo` + `nav2_bringup` environment.

---

## What the launch files call

`launch/assignment1.launch.py` in both packages does the following:

```python
ir_launch_pkg = get_package_share_directory('ir_launch')
sim_launch = os.path.join(ir_launch_pkg, 'launch', 'assignment_1.launch.py')

IncludeLaunchDescription(
    PythonLaunchDescriptionSource(sim_launch),
    launch_arguments={'rviz_config_file': rviz_config_path}.items()
)
```

So it requires:

- a package named `ir_launch` on the `AMENT_PREFIX_PATH`,
- a file `ir_launch/launch/assignment_1.launch.py`,
- that launch accepts an `rviz_config_file` argument (used to inject this
  repository's `cfg/assignment_view.rviz`).

## Interfaces `ir_launch` must supply

Every item below was derived from the nodes' subscriptions, service clients and
frame lookups. If the external launch does not provide them, the pipeline will
appear to start and then do nothing.

### Simulation

| Requirement | Why |
|---|---|
| Gazebo world with a TurtleBot 3 | the whole demonstration runs in simulation |
| A 360° LiDAR publishing `sensor_msgs/LaserScan` on `/scan` | corridor controller and table detector both subscribe to it |
| An RGB camera publishing `sensor_msgs/Image` on `/rgb_camera/image` and `sensor_msgs/CameraInfo` on `/rgb_camera/camera_info` | the `image_proc` rectify node is remapped from `image`/`camera_info` to these topics |

### Transforms the nodes look up

| Transform | Where it is used |
|---|---|
| `map` ← `base_scan` | `table_detector.py` transforms detected table centres into `map` |
| `map` ← `tag36h11:1`, `map` ← `tag36h11:10` | AprilTag node reads the tag poses from TF (the `target_frame` parameter defaults to `map`) |

Tag frames are produced by `apriltag_ros` via
`launch/camera_group29.launch.yml`, which is included by the main launch file and
depends on the camera topic names above and on the camera frame
`external_camera/link/rgb_camera`.

### Nav2

| Requirement | Why |
|---|---|
| `/lifecycle_manager_localization/manage_nodes` service, type `nav2_msgs/srv/ManageLifecycleNodes` | `navigation_node.py` calls `wait_for_service()` on it, then sends `STARTUP` / `PAUSE` / `RESUME` |
| `/lifecycle_manager_navigation/manage_nodes` service, same type | as above |
| `/navigate_to_pose` action, type `nav2_msgs/action/NavigateToPose` | the navigation goal |
| a node named `/bt_navigator` reachable via `ros2 lifecycle get /bt_navigator` | `navigation_node.py` shells out to this exact command in a loop and waits for `active` |

> Note: the `ManageLifecycleNodes` service is used directly here. Its availability
> and behaviour vary between Nav2 releases, which is one reason the ROS 2
> distribution matters (see the README's *Reproducibility status*).

### Launch argument

| Argument | Meaning |
|---|---|
| `rviz_config_file` | absolute path to the rviz layout to load |

---

## Reconstruction with standard upstream packages

**This has not been tested.** No ROS 2 installation was available during
preparation, so the following is a documented starting point rather than a
verified procedure.

The upstream packages that would satisfy the requirements above are:

- `turtlebot3_gazebo` — the simulation world and robot
- `nav2_bringup` — the navigation stack and both lifecycle managers
- `apriltag_ros` — tag detection and TF publication
- `image_proc` — camera rectification

A replacement `ir_launch` package would need to launch those and remap the camera
topics to `/rgb_camera/image` and `/rgb_camera/camera_info`. A minimal skeleton:

```
ir_launch/
├── package.xml
├── CMakeLists.txt          # ament_cmake, installing launch/
└── launch/
    └── assignment_1.launch.py
```

with `assignment_1.launch.py` including `turtlebot3_gazebo`'s
`turtlebot3_world.launch.py`, `nav2_bringup`'s `bringup_launch.py`, and passing
the `rviz_config_file` argument through.

**Caveats to expect:** the exact TurtleBot 3 camera topic names differ between
`turtlebot3_gazebo` model configurations (the original uses
`/rgb_camera/image`, which suggests a custom camera rather than the stock
TurtleBot 3 camera), and tag placement in the world must reproduce the geometry
the corridor controller expects (walls at ~0.55 m, a front clearance of ~0.45 m).

---

## What we could not verify

| Item | Status |
|---|---|
| `ir_launch` contents | not available — not in the original repository, and not provided |
| ROS 2 distribution | not declared anywhere |
| Whether the reconstruction above works | untested |
| Whether the corridor thresholds suit a stock world | unknown — the original world's geometry is not available |

The thresholds in `corridor_controller_node.py` (`CORRIDOR_THRESHOLD = 0.55 m`,
`FRONT_CLEARANCE = 0.45 m`) are tuned to the course's Gazebo world. Running this
pipeline in a different environment will require re-tuning them.
