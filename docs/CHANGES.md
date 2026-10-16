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

## Publication blockers — remaining

Only one blocker is left, and it is not a technical one:

1. **Collaborator consent.** `group29_assignment_1` includes 5 commits by
   Vaheid Labbaf, and the accompanying report is co-authored by him. Consent to
   publish this repository has **not** been confirmed. It should not be made
   public until it is.
