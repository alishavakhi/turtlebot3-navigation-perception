# Upstream simulation dependency — provenance and licensing

This project was developed and tested inside a Gazebo simulation environment
provided for the course. That environment is a **separate third-party
repository**, not part of this project. This document records exactly which
upstream components this project needs, where each came from, and — importantly —
**why the environment is not bundled here.**

---

## The upstream repository

```
Repository : https://github.com/PieroSimonet/ir_2526
Commit     : d19ae7613e50112f9bcd8bd995bb4572ef71b821
Date       : 2025-09-10 16:23:42 +0200
Author     : pierosimonet <simonetto.piero@gmail.com>
Branch     : main (the only branch)
```

A full local snapshot of that commit (209 files) was taken during preparation and
its per-file SHA-256 manifest recorded, so the exact environment this project ran
against is preserved even if the upstream repository disappears.

## Why the environment is not bundled in this repository

**The upstream repository has no licence.** GitHub reports `license: null`, there
is no `LICENSE` file at its root, and three of its five packages declare
`<license>TODO: License declaration</license>` in their `package.xml`. Under
default copyright, that means **all rights reserved** — the code may be read and
used, but not redistributed.

There is also a specific course instruction not to commit the instructor's code as
part of the coursework, which points the same way.

So the environment is **deliberately not vendored here.** Copying it would be a
licence violation, and the honest position is to document the dependency rather
than quietly absorb it.

## Component-by-component licence matrix

Licence status was determined from each file's *own* copyright header, from
package-level `package.xml` declarations, and from whether the package actually
ships the licence text it declares.

### Needed by this project — TurtleBot3 navigation

| Component | Upstream path | Licence | Bundled here? |
|---|---|---|---|
| Simulation launch | `ir_launch/launch/assignment_1.launch.py` | **Apache-2.0** (© 2023 Open Source Robotics Foundation) | No — see below |
| Robot spawner | `ir_launch/launch/spawn_tb3_launch.py` | **Apache-2.0** (© 2023 OSRF, © 2024 Open Navigation LLC) | No |
| Gazebo world | `ir_base/worlds/iaslab_camera_tables.sdf` | **NO LICENCE** | No |
| Occupancy map | `ir_base/maps/lab_map.pgm` / `.yaml` | **NO LICENCE** | No |
| Nav2 parameters | `ir_base/params/nav2_params.yaml` | **NO LICENCE** | No |
| ROS–Gazebo bridge config | `ir_base/params/turtlebot3_waffle_bridge.yaml` | **NO LICENCE** | No |
| TurtleBot 3 description | `ir_base/urdf/turtlebot3_waffle.urdf` | **NO LICENCE** | No |
| RGB camera description | `ir_base/urdf/camera.urdf` | **NO LICENCE** | No |
| AprilTag models + materials | `ir_base/models/artag/**` (21 files) | **NO LICENCE** | No |
| Package scaffolding | `ir_base/{package.xml,CMakeLists.txt}` | **NO LICENCE** | No |
| AprilTag detector | `apriltag_ros/**` (12 files) | **MIT** (ships `LICENSE`, declares MIT) | No — available upstream |

### Summary

|  | Files | Redistributable? |
|---|---|---|
| Apache-2.0 / BSD-3-Clause / MIT | 14 of 34 needed source files (plus `apriltag_ros`) | **Yes, with attribution** |
| **No licence at all** | **20 source files + 59 binary assets** (worlds, maps, models, meshes, URDFs) | **No** |

The permissive files are the *glue*, not the *environment*. The world, the map,
the robot and camera descriptions, the AprilTag models and the Nav2 tuning are all
unlicensed — and those are precisely what makes the simulation a simulation.

## Why a partial bundle was rejected

It would be lawful to copy only the Apache-2.0 launch files. It was deliberately
**not done**, for three reasons:

1. **It would not make the project runnable.** The launch file's first act is
   `get_package_share_directory('ir_base')` — with `ir_base` absent, it fails
   immediately. A reader would see a "self-contained" repository whose launch
   crashes.
2. **It would misrepresent the state.** A `third_party/` directory holding a
   fragment implies self-containment that does not exist.
3. **It would degrade the repository.** Twenty files of dead glue referencing
   absent packages is worse than a clear, documented dependency.

The useful, lawful subset is staged locally and can be added in one commit the
moment permission is granted — see below.

## What would make this project fully self-contained

Two options, in order of preference:

### Option A — written permission from the author

The smallest set that would achieve full self-containment for this project:

```
ir_launch/launch/assignment_1.launch.py        Apache-2.0  - already permitted
ir_launch/launch/spawn_tb3_launch.py           Apache-2.0  - already permitted
ir_base/worlds/iaslab_camera_tables.sdf        needs permission
ir_base/maps/lab_map.pgm                       needs permission
ir_base/maps/lab_map.yaml                      needs permission
ir_base/params/nav2_params.yaml                needs permission
ir_base/params/turtlebot3_waffle_bridge.yaml   needs permission
ir_base/urdf/turtlebot3_waffle.urdf            needs permission
ir_base/urdf/camera.urdf                       needs permission
ir_base/models/artag/**                        needs permission
ir_base/{package.xml,CMakeLists.txt}           needs permission
```

A short request to the author covering redistribution of the `ir_base` assets
under a permissive licence, with attribution, is all that is required. The
`ir_launch` and `apriltag_ros` components already carry permissive licences.

Attribution is not negotiable in return: the upstream author and the original
upstream projects (OSRF/Nav2, ROBOTIS/TurtleBot 3, AprilRobotics) would all be
credited in a `NOTICE` file, and the modifications made for the course would be
stated, as Apache-2.0 §4(b) requires.

### Option B — no permission available

Rebuild the environment from upstream open-source projects instead of using the
course's copy:

| Need | Legitimate upstream source |
|---|---|
| TurtleBot 3 model + meshes | `turtlebot3_description` (Apache-2.0, ROBOTIS) |
| Nav2 parameters | `nav2_bringup` defaults (Apache-2.0, Open Navigation LLC) |
| World | would have to be re-authored, since the course world is the author's own work |
| Map | regenerated by SLAM in the new world |
| AprilTag detector | `apriltag_ros` (MIT) or `dt_apriltags` (BSD) |

This yields a runnable project that owes nothing to the course repository, but the
world geometry and the tuning would differ, so the recorded demonstrations would
no longer correspond exactly to the published configuration. That trade-off is the
user's to make, not one to make silently.

## Running it today, with the dependency

Until one of the options above is resolved, the project runs against the upstream
environment exactly as it originally did:

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/PieroSimonet/ir_2526.git
cd ir_2526 && git checkout d19ae7613e50112f9bcd8bd995bb4572ef71b821
# then clone this repository alongside it and build the workspace
cd ~/ros2_ws && colcon build --symlink-install
```

Pinning the commit matters: the upstream repository may change or disappear, and
this project was verified against `d19ae761`.

## Attribution

The simulation environment, its world, map, robot and camera descriptions,
AprilTag models and Nav2 tuning are the work of its original author
(**Piero Simonetto**, University of Padova). Nothing in this repository claims
that work. Where the environment is used, it is used unmodified and credited.

The upstream launch files are themselves derived from:

- **Nav2 / Open Source Robotics Foundation** — Apache-2.0
- **Open Navigation LLC** — Apache-2.0
- **Stogl Robotics Consulting UG** — BSD-3-Clause
- **Universal Robots** — BSD-3-Clause
