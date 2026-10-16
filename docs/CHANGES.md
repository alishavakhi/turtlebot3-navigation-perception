# Changes made during preparation

This repository was prepared from the private original
`alishavakhi/ws_29_assignments`. The original repository is **unmodified**.

This file records **every** change, so that nothing here is a silent edit. The
guiding rule was: preserve the engineering work, change only what is necessary,
and document the justification.

---

## 1. Bug fix — Kalman launch file pointed at the wrong package

**File:** `src/group29_assignment_1_kalman/launch/assignment1.launch.py`
**Change:** the three `Node(package=...)` entries changed from
`'group29_assignment_1'` to `'group29_assignment_1_kalman'`.

**Why:** the package `group29_assignment_1_kalman` installs its own
`april_tag_node.py`, `navigation_node.py` and `table_detector.py`, but its launch
file started the executables from the *baseline* package. Launching it therefore
ran the baseline estimator, and the Kalman-filtered nodes in this package were
unreachable through their own launch file. This is the only change to executable
behaviour in this repository.

**Deliberately not changed:** the launch file still takes the shared
AprilTag/rectify composable container and the rviz config from
`group29_assignment_1` (`get_package_share_directory('group29_assignment_1')`).
That is a genuine shared-infrastructure dependency — `camera_group29.launch.yml`
exists only in the baseline package — so **both packages must be built** to run
Implementation A. The dependency is now declared in
`group29_assignment_1_kalman/package.xml`.

**Not tested.** No ROS 2 installation was available during preparation, so this fix
was verified by inspection only. See the README's *Reproducibility status*.

---

## 2. Privacy — university email addresses removed from manifests

**Files:** `src/group29_assignment_1/package.xml`,
`src/group29_assignment_1_kalman/package.xml`

**Before:** `<maintainer email="<university address>">ali</maintainer>`

**After:** `<maintainer email="45035448+alishavakhi@users.noreply.github.com">Ali Shavakhi</maintainer>`

**Why:** the maintainer field exposed a personal university address in a
public artifact. `package.xml` requires an email attribute, so it was replaced
with the author's own GitHub noreply address — which still attributes the package
correctly and is already public by nature.

Note that both authors' addresses also appear in the title line of the
accompanying report PDF, which is included unmodified. See *Publication blockers*
below.

---

## 3. Dependency declarations corrected

**Files:** both `package.xml` files

Added dependencies that the code imports but the original manifests omitted:

| Added | Needed by |
|---|---|
| `visualization_msgs` | `table_detector.py` publishes `Marker` cylinders |
| `python3-numpy` | `corridor_controller_node.py` (LiDAR maths); `april_tag_node.py` in the Kalman package |
| `rclcpp_components` | the composable container in `camera_group29.launch.yml` |
| `apriltag_ros` | the AprilTag node in `camera_group29.launch.yml` |
| `image_proc` | the rectify node in `camera_group29.launch.yml` |
| `group29_assignment_1` | declared as a runtime dependency of the Kalman package — it supplies the shared camera launch |

**Why:** without these, a clean machine cannot reproduce the runtime even after a
successful build. The set was derived by reading every import in every node.

Descriptions were also replaced: `"Group 29 assignments package"` (identical in
both packages, and vague) became a description of what each package actually
does.

---

## 4. File reorganisation

| Original location | New location | Why |
|---|---|---|
| `Assignment1.pdf` (repo root) | `docs/reports/Group29_Assignment1_Report.pdf` | reports belong under `docs/`, and the file now says what it is |
| `frames_2026-01-11_11.43.28.pdf` / `.gv` (repo root) | `docs/figures/tf_tree_baseline_run.pdf` / `.gv` | figures belong under `docs/`, named for what they show |
| — | `docs/figures/tf_tree_baseline_run.png` | **added**: PNG rendering of the above, because GitHub renders PNG inline and PDF does not |

No source file was moved, renamed or deleted. Both `frames_*` files were removed
from the repository root only, having been relocated.

---

## 5. Added files

| File | Purpose |
|---|---|
| `README.md` | written for this repository |
| `LICENSE` (root) | Apache-2.0, copied from the package's own `LICENSE` — the licence already declared by the packages |
| `.gitignore` | expanded; notably adds `venv/`, `venv*/`, `.venv/` |
| `CONTRIBUTORS.md` | collaborator attribution and commit-share record |
| `docs/RUNNING.md` | documents the external launch dependency |
| `docs/AI_USAGE_DISCLOSURE.md` | AI usage disclosure, carried over from the report |
| `docs/CHANGES.md` | this file |

The per-package `LICENSE` files were **kept**. Duplicating the licence per package
is standard ROS practice and `ament_copyright` lints expect it.

---

## 6. History

This repository begins from a **clean history**. The original repository's history
carries an entire Python virtual environment (numpy/scipy `.so` files, ~50 MB)
committed in `88bcfed` and deleted in `b8739ae` — gone from the tree but permanent
in history. Publishing it as-is would ship ~50 MB of binaries to every clone.

The original repository, its full history and its three branches
(`main`, `table-ali`, `vahid_work`) are untouched.

---

## What was deliberately NOT changed

- **No algorithm was modified.** The baseline midpoint estimator, the Kalman
  filter, the corridor controller, the table detector, and every threshold and
  gain are exactly as found.
- **No threshold, gain or constant was retuned.**
- **No file was reformatted or re-styled.**
- **No log level was changed.** The AprilTag nodes still set their logger to
  `ERROR`, which suppresses their own `.info()` messages; this is documented as a
  limitation rather than silently fixed.
- **No known limitation was fixed** other than item 1 above. The `angle_min`
  assumption in the corridor controller, the blocking calls in the navigation
  node, and the hard-coded `"map"` frame in the baseline node are all left as they
  are and documented in the README's *Known limitations*.

## 7. Report PDF: personal email addresses redacted

**File:** `docs/reports/Group29_Assignment1_Report.pdf`

Both authors' university email addresses appeared on the report's title line in
three places, and were removed from all three:

| Location | Before | After |
|---|---|---|
| Visible text (page 1) | `Email: <both addresses>` | `Email: redacted-for-privacy` |
| PDF link annotation | `<first address>` | removed |
| PDF link annotation | `<second address>` | removed |

(The addresses themselves are not reproduced in this file, since this file is
part of the public repository — quoting them here would undo the redaction.)

This is a genuine **text-level** redaction, not a black box drawn over the
addresses: the characters were removed from the page content stream, so the
addresses are not recoverable by extracting text, decompressing the streams, or
reading the file's raw bytes.

Verified after redaction:

- `pdftotext` output contains no occurrence of either address,
- decompressing every stream in the file finds no occurrence,
- the file's raw bytes contain no occurrence (the streams are Flate-compressed),
- neither `mailto:` annotation survives,
- document metadata is clean,
- the report is still 3 pages and renders correctly (checked visually).

**Authors' names were deliberately preserved** — `Ali Shavakhi, Vaheid Labbaf`
remains on the title line. Redacting an address must not erase attribution.

The report's **repository link annotation was repointed** at this public
repository (`https://github.com/alishavakhi/turtlebot3-navigation-perception`).
It originally pointed at the private original `alishavakhi/ws_29_assignments`,
which would have returned 404 for a public reader. The demonstration-video link
annotation is untouched and still resolves.

## 8. Self-contained simulation investigation, and testing-documentation correction

**Investigated:** whether the simulation environment could be bundled so this
repository runs without cloning the course repository
(`github.com/PieroSimonet/ir_2526`).

**Outcome: it cannot lawfully be bundled.** The upstream repository carries
**no licence at all** — GitHub reports `license: null`, there is no `LICENSE`
file, and `ir_base`, `ir_launch` and `ir_desription` all declare
`<license>TODO: License declaration</license>`. Of the 34 files this project
needs, **20 source files and 59 binary assets are unlicensed** (the world, map,
AprilTag models, TurtleBot 3 and camera descriptions, Nav2 tuning). Only the
launch glue and `apriltag_ros` are permissively licensed, and those alone would
not make the project runnable.

A partial bundle of just the Apache-2.0 files was considered and **rejected**:
the launch file's first action resolves `ir_base`, so it would fail immediately,
producing a repository that looks self-contained but crashes. That is worse than
a documented dependency.

**Added:** `docs/UPSTREAM_DEPENDENCIES.md` — upstream repository and exact commit
SHA (`d19ae761`), the full component-by-component licence matrix, why nothing is
bundled, the two routes to self-containment (written permission, or rebuilding
from permissive upstream projects), how to run it today against a pinned commit,
and attribution to the original author.

A complete local snapshot (209 files) of the upstream commit, with a per-file
SHA-256 manifest, was taken and preserved outside this repository, so the exact
environment is recoverable even if upstream disappears.

**Corrected — testing documentation.** The previous version of this README said
`colcon build` and launching were "NOT TESTED", which misread as *the project was
never tested*. That was wrong and is fixed. The [Results](../README.md#results) and
[Reproducibility status](../README.md#reproducibility-status) sections now separate two
things explicitly:

| | |
|---|---|
| The original implementation in the original environment | **tested and working** — ran end to end in Gazebo, evidenced by the recorded demonstrations, the live transform tree and the report |
| A fresh build and run of *this* repository | **not performed** here — no ROS 2 on the preparation host |

No test result was invented; the change is in what the documentation claims, and
it now claims neither too little nor too much.

**Expanded:** the install and run sections now cover Ubuntu and ROS 2 versions,
the full system dependency list, `colcon` build steps, simulation startup, and a
step-by-step description of what a successful run looks like.

## 9. Simulation environment vendored — the repository is now self-contained

Following the author's permission, the simulation environment is now included in
this repository under `third_party/ir_2526/`. Cloning the external repository is
no longer required.

**Added** (70 files, byte-identical to upstream):

```
third_party/ir_2526/README.md   provenance, licence status, what's included
third_party/ir_2526/NOTICE      attribution for every author and upstream project
third_party/ir_2526/ir_launch/  assignment_1.launch.py, spawn_tb3_launch.py
third_party/ir_2526/ir_base/    worlds, maps, params, urdf, rviz, models
```

**Deliberately not copied:**

| Excluded | Why |
|---|---|
| `models/build`, `models/install`, `models/log` | colcon build artefacts accidentally committed upstream |
| `models/docks`, `models/objects`, `models/walls` | not referenced by the world; excluding them also limits third-party exposure, since `arena_walls` is credited to a further author |
| `apriltag_ros` | pristine upstream 3.3.0 (MIT), available as `ros-$ROS_DISTRO-apriltag-ros`; a duplicate would add nothing |

**Integrity:** all 70 files were hashed against the upstream snapshot after
copying and every one is identical. No header, copyright notice or licence
declaration was altered. Upstream package names are preserved because the launch
files and the world resolve them by name.

**Licence boundary:** the root `LICENSE` (Apache-2.0) now explicitly states that
it covers only `src/`, `docs/` and the READMEs, and **not** `third_party/`. No
licence was invented for the vendored material — its status is "redistributed
with the author's permission, copyright remains with the original authors".

**Open item:** two model directories inside the required set are credited to other
authors (`models/artag` — Nicola Castaman; `models/cafe_table` — Nate Koenig /
Open Robotics) and carry no stated licence. The author's permission covers his own
work; the scope question that raised was put to
the repository owner and answered at publication — and has since been resolved on its own terms, see section 11 and
`docs/UPSTREAM_DEPENDENCIES.md`.

## 10. Publication, and the consent record

**Published 2026-10-16.** Both consent gates that were open when the sections
above were written are now closed, and the repository is public.

1. **Collaborator consent.** `group29_assignment_1` includes commits by Vaheid
   Labbaf, and the accompanying report is co-authored by him. The repository
   owner confirmed on 2026-10-16 that Vaheid Labbaf agreed to publication of the
   shared projects. Attribution is kept accurate per path — see
   `../CONTRIBUTORS.md` and the *My contribution* section of the README; nothing
   by another author is presented as the owner's.
2. **Redistribution permission for the simulation environment.** The original
   author's permission to redistribute the environment files with attribution was
   confirmed on 2026-10-16, and the environment is vendored in section 8 above. A
   scope question was raised on the same day for the two directories inside it
   that are credited to other authors (`models/artag`, `models/cafe_table`); the
   owner authorised publication with those notices preserved unmodified. Their
   licence status remains documented, unresolved and unhidden in
   `UPSTREAM_DEPENDENCIES.md` and `../third_party/ir_2526/NOTICE`.

**Documentation corrected in the same pass**, after a verification run against
the live repository:

- *Known limitations* previously described the simulation environment as "not
  bundled" — true before section 8, false after it. Corrected.
- The reproducibility table listed "vendored code" as *verified absent*, which
  section 8 contradicts. Split into *secrets and personal data* (absent) and
  *vendored third-party code* (present, intentional, hashed).
- This section previously stated that collaborator consent had not been
  confirmed; it now records the consent that was obtained.

## 11. Final cleanup pass — licensing, links and consistency

A review pass over the published state. Three groups of change.

**1. Third-party asset licensing resolved.** The two asset groups previously listed
as an open question are now settled on their own terms rather than on the
environment author's permission over other people's work:

- **`models/artag/**`** — previously credited to Nicola Castaman with no licence.
  The 18 marker images are now rendered from the public AprilTag `tag36h11` family
  definition (AprilRobotics, BSD-2-Clause), and the model wrapper and material
  scripts rewritten. Every image decodes to its own tag id under the reference
  detector, and its module-level pattern is identical to the file it replaces.
- **`models/cafe_table/**`** — licence verified as **CC-BY-3.0** (© 2012 Nathan
  Koenig, `osrf/gazebo_models`). Redistribution is permitted with attribution, so
  the model is kept and attributed in `third_party/ir_2526/NOTICE`, with the licence
  text in `third_party/ir_2526/licenses/`.

Full detail is in [`UPSTREAM_DEPENDENCIES.md`](UPSTREAM_DEPENDENCIES.md).

**2. Documentation defects corrected.** Four real defects were present on the
published pages, all of them introduced by earlier passes:

| Defect | Fix |
|---|---|
| Two sections were both numbered `## 9` | renumbered — publication is now 10, this section 11 |
| The README contents list linked `#overview-and-objectives`, but the heading is `## Overview` | anchor corrected |
| Two references in this file linked `#results` and `#reproducibility-status`, which live in the README, not here | repointed at `../README.md#...` |
| Text said "see section 9" from inside section 9, and `UPSTREAM_DEPENDENCIES.md` said "see the open question at the end" after that heading had been renamed | both repointed |

**3. Presentation.** The contribution section now leads with this project's own
engineering work and points to [`../CONTRIBUTORS.md`](../CONTRIBUTORS.md) for the
full per-path attribution, which is unchanged and remains the authoritative record
for this repository.

No source file, vendored dependency, report or licence text was modified by this
pass.


## 12. Complete environment preservation, and the final audit items

**Context.** An independent audit (see the project records) checked the published
state against the intent and found the tree sound, licence coverage complete and
the documentation accurate. It also produced three items to close, and this release
implements all of them.

**1. The environment is now preserved COMPLETE.** The requirement is that neither
project depends on the upstream repository remaining available. `third_party/ir_2526/`
previously held only the packages each project ran, and the launch files for the
other project had been trimmed to avoid dangling references. That was a reasonable
choice for a per-project subset, but it is the wrong choice for *preservation*, and
completeness now wins.

Added: `ir_desription/`, `ir_movit_config/`, `apriltag_ros/`, the `objects` and
`docks` models, and the launch files previously trimmed.

| | Before | After |
|---|---|---|
| upstream files included | 32 / 91 (per project) | **133, identical in both** |
| packages | 2 / 4 | 5 (all of them) |

All 133 files are SHA-256 verified byte-identical to upstream `d19ae761`. Nothing
was renamed, reformatted or edited.

**Not included, and enumerated rather than hidden** — 74 of the 207 upstream files:

| Excluded | Files | Reason |
|---|---|---|
| `ir_base/models/artag/` | 36 | © Nicola Castaman, no licence. Replaced by markers regenerated from the public BSD-2-Clause `tag36h11` family definition |
| `ir_base/models/walls/arena_walls/` | 3 | © Elisa Tosello, no licence. Unreferenced by any world |
| `ir_base/models/{build,install,log}/` | 35 | colcon output committed upstream by accident; embeds the upstream author's local path |

The manifest is explicit that this **is not a byte-for-byte complete copy** of the
upstream repository, and it is nowhere described as one. All 207 files are preserved
privately with a per-file SHA-256 manifest.

**2. Robotiq / PickNik attribution added.** `ir_desription/urdf/robotiq_d.urdf`
reproduces the `robotiq_gripper` xacro macro from PickNik's `robotiq_description`
(BSD 3-Clause, © 2022 PickNik Robotics) and was not named in the `NOTICE`. Now
attributed, with the licence text committed at
`third_party/ir_2526/licenses/robotiq-BSD-3-Clause.txt`. `apriltag_ros` (MIT)
and the UR5 meshes (BSD-3-Clause) are likewise recorded explicitly.

**3. The ROS 2 distribution was identified.** It had been recorded as undetermined
through every previous pass rather than guessed. The audit found hard evidence: the
vendored `ir_desription/urdf/ur_gripper.urdf` — the file the UR5 launch paths load,
byte-identical to upstream — hard-codes 18 mesh paths as
`file:///opt/ros/jazzy/share/robotiq_description/...`. The environment was therefore
**ROS 2 Jazzy**. Because those paths are absolute, the UR5 project effectively
requires Jazzy. Recorded as inference from a named artefact, with confirmation by
the original operators still outstanding.

**4. A complete test plan added** at [`TEST_PLAN.md`](TEST_PLAN.md): environment,
build, launch, expected outputs, the four automation layers, and an explicit
statement of what has and has not been executed.

No algorithm, source file, report or licence text was modified by this release.

## Complete environment: the generated files added

**Requested.** Every remaining republishable file from the upstream repository is
now included: the 35 colcon artefacts under `ir_base/models/{build,install,log}/`.
They are the environment author's own generated output and so fall under the same
redistribution permission as the rest of his environment.

| | After the previous release | Now |
|---|---|---|
| upstream files included | 133 | **168 of 207** |
| files not published | 74 | **39** |

All 35 files, including the two relative symlinks (`log/latest`,
`log/latest_build`), are byte-identical to upstream and were verified by SHA-256
after copying: 35/35, 0 mismatches. Nothing was renamed, reformatted or modified.

No file was replaced or removed by this change.

**The 39 files that remain unpublished** are the only ones, and they are not
omitted silently:

| Excluded | Author | Files |
|---|---|---|
| `ir_base/models/artag/` | **Nicola Castaman** `<nicola.castaman@dei.unipd.it>` | 36 |
| `ir_base/models/walls/arena_walls/` | **Elisa Tosello** `<elisa.tosello@unipd.it>` | 3 |

These are authored by people other than the environment's author, carry no licence
of their own, and are **not covered by his permission** — a grant reaches the
grantor's copyright only. Publishing them would be redistribution of unlicensed
third-party material, so they are not included. The `artag` marker *images* used by
the simulation are present in this repository as regenerated files rendered from
the public BSD-2-Clause AprilTag `tag36h11` family definition, with identical tag
ids, geometry and file paths; `arena_walls` is referenced by no world and is
absent entirely.

If either author's permission is obtained, both groups drop into their existing
paths in a single commit. They are preserved in full, with per-file SHA-256 hashes,
in the private snapshot.
