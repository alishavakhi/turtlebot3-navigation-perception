# Simulation environment — provenance, permission and licensing

This project runs in a Gazebo simulation environment **written by someone else**.
It is vendored into this repository under
[`third_party/ir_2526/`](../third_party/ir_2526/) so the project can be built and
run without cloning an external repository. This document records where it came
from, what permission exists, and — importantly — what is **not** covered.

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

Every vendored file is **byte-identical** to that commit. Verified by hashing all
70 files against the upstream snapshot after copying — no header, copyright notice
or licence declaration was altered.

A complete snapshot of the upstream commit (209 files) with a per-file SHA-256
manifest is also held outside this repository, so the exact environment is
recoverable independently of both repositories.

## Permission

The environment is redistributed here **with the permission of the original
author, Piero Simonetto**, granted on the basis that attribution is maintained.

The upstream repository carries **no licence**: GitHub reports `license: null`,
there is no `LICENSE` file at its root, and `ir_base`, `ir_launch` and
`ir_desription` each declare `<license>TODO: License declaration</license>` in
their `package.xml`. No licence is asserted for the vendored material, and none
was invented. Its status is:

> Redistributed with the author's permission. Copyright remains with the original
> authors. All rights reserved other than the redistribution expressly permitted
> here.

The vendored files are therefore **not** covered by this repository's Apache-2.0
licence, which applies only to `src/`, `docs/` and the READMEs.

## What that permission does not necessarily cover

The permission is the professor's to give for **his own work**. The environment
also contains material authored by other people, and he is not necessarily the
rights holder for it. Two such items are **required** to load the world and are
therefore still included:

| Item | Author | Status |
|---|---|---|
| `ir_base/models/artag/**` — ARTag model and AprilTag textures (21 files) | **Nicola Castaman** `<nicola.castaman@dei.unipd.it>` | No licence stated in `model.config`. **Required by the world.** |
| `ir_base/models/cafe_table/**` — the table model | **Nate Koenig** `<nate@osrfoundation.org>`, Open Robotics | No licence stated in `model.config`. Originates from the Gazebo model collection, whose models are generally permissive or CC-BY, but this has not been confirmed for this copy. |
| `ir_launch/launch/assignment_1.launch.py` and `spawn_tb3_launch.py` | Open Source Robotics Foundation; Open Navigation LLC | **Apache-2.0** — redistribution permitted, notice intact in the files |
| Launch files derived from Universal Robots bringup | Stogl Robotics Consulting UG | **BSD-3-Clause** — redistribution permitted, notice intact |

Everything else under `third_party/ir_2526/` is Piero Simonetto's own work.

**The two model directories are the open item.** They should either be confirmed
as covered by the professor's permission, or the authors' agreement obtained, or
the models replaced — see the open question at the end.

## What is vendored, and what was left out

### Included

```
third_party/ir_2526/                                 70 files, 1.6 MB
├── ir_launch/          assignment_1.launch.py, spawn_tb3_launch.py
└── ir_base/            worlds/ maps/ params/ urdf/ rviz/ models/{artag,cafe_table}
```

| Component | Role |
|---|---|
| `ir_base/worlds/iaslab_camera_tables.sdf` | the world this project runs in |
| `ir_base/urdf/turtlebot3_waffle.urdf` | the robot, including its RGB camera link |
| `ir_base/urdf/camera.urdf` | the external camera description |
| `ir_base/params/nav2_params.yaml` | the Nav2 tuning this pipeline was verified against |
| `ir_base/params/turtlebot3_waffle_bridge.yaml` | ROS–Gazebo bridge topics |
| `ir_base/maps/lab_map.pgm` / `.yaml` | the occupancy map |
| `ir_base/models/artag/`, `models/cafe_table/` | the only models the world references |
| `ir_base/rviz/` | rviz configuration |
| `ir_launch/launch/` | the simulation entry points |

### Deliberately excluded

| Excluded | Why |
|---|---|
| `ir_base/models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream — not part of the environment |
| `ir_base/models/docks`, `models/objects`, `models/walls` | **not referenced by the world.** Excluding them also reduces third-party exposure: `models/walls/arena_walls` is credited to a further author (Elisa Tosello) and `objects`/`docks` carry no authorship at all |
| `ir_desription`, `ir_movit_config` | UR5-specific; they belong to the companion repository |
| `apriltag_ros` | a pristine copy of upstream `apriltag_ros` 3.3.0 (MIT), available as the distribution package `ros-$ROS_DISTRO-apriltag-ros`; bundling a duplicate adds nothing |

The world file was inspected for `model://` references: only `models/artag` and
`models/cafe_table` are required. Nothing omitted is needed to run the project.

## Package names are unchanged

`ir_launch` and `ir_base` keep their original names, because the launch files and
the Gazebo world resolve them by name —
`get_package_share_directory('ir_base')` and
`model://ir_base/models/artag/...`. Renaming either would break the environment,
so `colcon` builds them exactly as upstream intended.

## Still required from the system

Standard ROS 2 packages only, installed through `rosdep`/`apt`:

`navigation2`, `nav2-bringup`, `nav2-minimal-tb3-sim`, `turtlebot3`,
`turtlebot3-gazebo`, `apriltag-ros`, `image-proc`, `ros-gz`, `python3-numpy`.

## Third-party scope question — raised, and answered on publication

The professor's permission covers **his** work. Two directories inside the
required set — `models/artag` (Nicola Castaman) and `models/cafe_table`
(Nate Koenig / Open Robotics) — were authored by other people and carry no stated
licence of their own. This was put to the repository owner before publication; on
2026-10-16 publication was authorised on the basis that these files are part of
the environment being redistributed with the original author's permission, with
every authorship notice preserved verbatim.

Stated plainly, so nothing here reads as a licence it is not:

- these two directories carry **no licence text of their own**. None was invented
  for them, and they are not covered by this repository's Apache-2.0 licence;
- they are included unmodified, with their authors' own `model.config` credits
  exactly as upstream wrote them and recorded in `../third_party/ir_2526/NOTICE`;
- if the question is ever revisited, `models/artag` can be regenerated from the
  public AprilTag `36h11` family definition (AprilRobotics, BSD-2-Clause) as
  original work, and `models/cafe_table` replaced with an equivalent table model
  from a permissively licensed source. Either is a one-commit change.

Everything else in `third_party/` is either the professor's own work under his
permission, or permissively licensed with its notice intact.

## Attribution

The simulation environment — its world, map, RobotBot 3 and camera descriptions,
AprilTag models and Nav2 tuning — is the work of its original author,
**Piero Simonetto** (University of Padova). Nothing in this repository claims that
work, and it is used unmodified.

The upstream launch files are themselves derived from:

- **Nav2 / Open Source Robotics Foundation** — Apache-2.0
- **Open Navigation LLC** — Apache-2.0
- **Stogl Robotics Consulting UG** — BSD-3-Clause
- **Universal Robots** — BSD-3-Clause
- **AprilTag / AprilRobotics** — BSD-2-Clause (tag family definitions)
