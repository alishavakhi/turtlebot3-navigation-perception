# Vendored simulation environment — `ir_2526`

The ROS 2 packages in this directory provide the Gazebo simulation environment
that this project was built and tested against. They are **not part of this
project** and were **not written by its author**. They are vendored here so the
project can be built and run without cloning an external repository.

---

## Provenance

```
Upstream repository : https://github.com/PieroSimonet/ir_2526
Upstream commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Commit date         : 2025-09-10 16:23:42 +0200
Commit author       : pierosimonet <simonetto.piero@gmail.com>
Default branch      : main (the only branch)
Vendored on         : 2026-10-16
```

Every file in this directory is **byte-identical** to the file at that commit.
Nothing has been edited, reformatted, re-licensed or had its headers altered.
This was verified after copying by hashing each file against the upstream
snapshot — see `docs/UPSTREAM_DEPENDENCIES.md` in the repository root.

## Licence status — please read

**These files are NOT covered by this repository's Apache-2.0 licence.** The
`LICENSE` file at the repository root applies only to the project's own code.

They are redistributed here **with the permission of the original author**,
granted on the basis that proper attribution is maintained. No licence text was
supplied with the original work — upstream declares
`<license>TODO: License declaration</license>` in three of its five packages and
carries no `LICENSE` file at all. So the correct description of their status is:

> Redistributed with the author's permission. Copyright remains with the original
> authors. All rights reserved other than the redistribution expressly permitted.

If you intend to reuse these files in your own work, ask the original authors —
do not assume they are open source.

## Authorship and attribution

| Component | Author | Copyright |
|---|---|---|
| `ir_launch` packages and launch files | Piero Simonetto | © Piero Simonetto |
| `ir_base` package, Gazebo worlds, maps, Nav2 parameters, TurtleBot 3 and camera URDFs | Piero Simonetto | © Piero Simonetto |
| `ir_base/models/artag/**` | **Nicola Castaman** `<nicola.castaman@dei.unipd.it>` | © Nicola Castaman |
| `ir_base/models/cafe_table/**` | **Nate Koenig** `<nate@osrfoundation.org>`, Open Robotics | © Nate Koenig / Open Robotics |
| Launch files derived from Nav2 | Open Source Robotics Foundation | Apache-2.0 |
| Launch files derived from Universal Robots bringup | Stogl Robotics Consulting UG | BSD-3-Clause |

The authorship of `artag` and `cafe_table` is recorded in each model's own
`model.config`, which is preserved unmodified. These two model directories are
the only material in this directory **not authored by Piero Simonetto**, and both
are required to load the simulation worlds.

## What is included

### This repository

```
third_party/ir_2526/
├── README.md            this file
├── NOTICE               formal attribution and licence statement
├── ir_launch/           simulation entry points
│   └── launch/          assignment_1.launch.py, spawn_tb3_launch.py
└── ir_base/             environment assets
    ├── worlds/          iaslab_camera_tables.sdf (the world this project runs in)
    ├── maps/            lab_map.pgm / .yaml
    ├── params/          nav2_params.yaml, turtlebot3_waffle_bridge.yaml
    ├── urdf/            turtlebot3_waffle.urdf, camera.urdf
    ├── models/artag/    AprilTag models and tag textures
    └── rviz/            rviz configuration
```

### Deliberately omitted

| Omitted | Reason |
|---|---|
| `ir_base/models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream — not part of the environment |
| `ir_base/models/docks`, `models/objects`, `models/walls` | **not referenced by either simulation world.** Omitting them limits how much third-party material is redistributed, since `models/walls/arena_walls` is credited to a further author (Elisa Tosello) and `objects`/`docks` carry no authorship at all |
| `apriltag_ros` | a pristine upstream copy of `apriltag_ros` 3.3.0 (MIT). It is available as the standard distribution package `ros-$ROS_DISTRO-apriltag-ros`, so bundling a duplicate would add nothing |
| `ir_launch/launch/assignment_2.launch.py`, `exercise_4.launch.py` | launch files for the other assignment and for a different exercise. They are **not used by this project** and `assignment_2.launch.py` references packages (`ir_desription`, `ir_movit_config`) that belong to the companion repository, so shipping it here would leave a launch file that cannot run |
| `ir_desription`, `ir_movit_config` | UR5-specific; they belong to the companion repository |

> **This is a subset of the upstream `ir_launch` package** — two of its four
> launch files are here. Every file present is byte-identical to upstream; none
> was edited. `ir_base` is complete apart from the model directories listed above.

## A dependency worth knowing about

`ir_launch/launch/assignment_1.launch.py` calls
`get_package_share_directory('ur_description')` unconditionally, even though this
is a TurtleBot 3 project — it uses that path to build the Gazebo resource path.

That means **`ros-$ROS_DISTRO-ur-description` must be installed**, or the
simulation launch fails immediately with a `PackageNotFoundError`. It is listed
in the repository's install instructions for that reason. The line is upstream's
own (unmodified); this is documented rather than patched, so the vendored file
stays byte-identical.

## Hidden dependency to install

| Package | Why |
|---|---|
| `ur-description` | required by `assignment_1.launch.py` even on the TurtleBot 3 project — see above |

Nothing was omitted that either world needs. The world files were inspected for
`model://` references and only `models/artag` and `models/cafe_table` are
required.

## Package names are unchanged

The packages keep their original names (`ir_launch`, `ir_base`) because the
launch files and the Gazebo world resolve them by name —
`get_package_share_directory('ir_base')`, `model://ir_base/models/...`. Renaming
any of them would break the environment. The same applies to
`ir_desription` (upstream spelling, a typo for "description") in the companion
repository.

## Building

`colcon` discovers packages recursively, so building from the repository root
picks these up automatically alongside the project's own packages:

```bash
colcon build --symlink-install
```

To build only the project's own code:

```bash
colcon build --symlink-install --packages-select group29_assignment_1
```
