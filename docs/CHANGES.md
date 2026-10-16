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
never tested*. That was wrong and is fixed. The [Results](#results) and
[Reproducibility status](#reproducibility-status) sections now separate two
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
the repository owner and answered at publication — see section 9 and
`docs/UPSTREAM_DEPENDENCIES.md`.

## 9. Publication, and the consent record

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
