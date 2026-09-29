#!/usr/bin/env python3

from pathlib import Path
import csv
import sys

# ---------------------------------------------------------------------
# T8 MOD-005
# Completed-Task Prediction-Artifact Inventory
#
# READ-ONLY FILESYSTEM / METADATA AUDIT
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"

TARGET_TASKS = {
    "T2",
    "T3",
    "T4",
    "T5",
    "T7",
}

# Directories that are relevant to completed modeling artifacts.
SEARCH_ROOTS = [
    MODELING_ROOT,
]

# Avoid enormous/raw dataset trees if they happen to be reachable
# through symlinks or copied structures.
EXCLUDED_NAME_PARTS = {
    "raw",
    "archive",
    "archives",
    "dataset",
    "datasets",
    "mozilla_core",
    "Mozilla_CORE",
}

MAX_FILE_SIZE_FOR_HEADER_SCAN = 512 * 1024 * 1024


def task_mentions(path):
    """
    Detect likely task association from path/name only.
    This is discovery metadata, not evidence that the artifact belongs
    to the task.
    """
    text = str(path).lower()

    hits = []

    for task in sorted(TARGET_TASKS):
        if task.lower() in text:
            hits.append(task)

    return hits


def should_skip(path):
    parts = {
        part.lower()
        for part in path.parts
    }

    excluded = {
        name.lower()
        for name in EXCLUDED_NAME_PARTS
    }

    return bool(parts & excluded)


def human_size(size):
    units = ["B", "KB", "MB", "GB", "TB"]

    value = float(size)

    for unit in units:
        if value < 1024:
            return f"{value:.2f} {unit}"

        value /= 1024

    return f"{value:.2f} PB"


def inspect_csv_header(path):
    """
    Read only the CSV header and first small amount of metadata.
    No complete CSV scan is performed here.
    """

    try:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
            errors="replace",
        ) as handle:

            reader = csv.reader(handle)

            header = next(reader, None)

            if header is None:
                return {
                    "status": "EMPTY",
                    "columns": 0,
                    "header": [],
                }

            return {
                "status": "HEADER_READ",
                "columns": len(header),
                "header": header,
            }

    except Exception as exc:
        return {
            "status": "HEADER_READ_ERROR",
            "columns": None,
            "header": [],
            "error": repr(exc),
        }


print("=" * 78)
print("T8 MOD-005 — COMPLETED-TASK PREDICTION-ARTIFACT INVENTORY")
print("=" * 78)

print("\nREAD-ONLY CONTRACT")
print("- Filesystem discovery only")
print("- No artifact modification")
print("- No model loading")
print("- No model training")
print("- No prediction generation")
print("- No evidence fusion")
print("- No target construction")
print("- No score construction")
print("- No raw dataset scanning")
print("- CSV inspection limited to headers")


# ---------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------

print("\n[1] PROJECT WORKSPACE")
print("-" * 78)

print(f"project root: {PROJECT_ROOT}")
print(f"modeling root: {MODELING_ROOT}")

if not PROJECT_ROOT.exists():
    print("\nSTATUS: FAIL")
    print("Project root does not exist.")
    sys.exit(1)

if not MODELING_ROOT.exists():
    print("\nSTATUS: FAIL")
    print("Modeling root does not exist.")
    sys.exit(1)

print("project root: PRESENT")
print("modeling root: PRESENT")


# ---------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[2] CANDIDATE ARTIFACT DISCOVERY")
print("=" * 78)

files = []

for search_root in SEARCH_ROOTS:

    for path in search_root.rglob("*"):

        if not path.is_file():
            continue

        if should_skip(path):
            continue

        files.append(path)


files = sorted(
    set(files),
    key=lambda p: str(p).lower()
)

print(f"files discovered under modeling root: {len(files)}")


# ---------------------------------------------------------------------
# Relevant artifact candidates
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[3] TASK-ASSOCIATED FILE CANDIDATES")
print("=" * 78)

task_candidates = {
    task: []
    for task in sorted(TARGET_TASKS)
}

for path in files:

    mentions = task_mentions(path)

    for task in mentions:
        task_candidates[task].append(path)


for task in sorted(TARGET_TASKS):

    print(f"\n{task}")

    candidates = task_candidates[task]

    if not candidates:
        print("  <NO PATH-NAME MATCHES FOUND>")
        continue

    for path in candidates:

        try:
            stat = path.stat()
            size = human_size(stat.st_size)
        except OSError:
            size = "<STAT_ERROR>"

        print(
            f"  {path}"
        )
        print(
            f"    size: {size}"
        )


# ---------------------------------------------------------------------
# Prediction-related filenames
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[4] PREDICTION-LIKE ARTIFACT CANDIDATES")
print("=" * 78)

prediction_keywords = {
    "prediction",
    "predictions",
    "pred",
    "inference",
    "output",
    "outputs",
    "score",
    "scores",
    "probability",
    "probabilities",
    "proba",
    "survival",
}

prediction_candidates = []

for path in files:

    text = path.name.lower()

    if any(
        keyword in text
        for keyword in prediction_keywords
    ):
        prediction_candidates.append(path)


if not prediction_candidates:
    print("<NO PREDICTION-LIKE FILENAMES FOUND>")
else:

    for path in prediction_candidates:

        try:
            stat = path.stat()
            size = human_size(stat.st_size)
        except OSError:
            size = "<STAT_ERROR>"

        print(path)
        print(f"  size: {size}")


# ---------------------------------------------------------------------
# CSV headers for candidates
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[5] CSV HEADER INSPECTION")
print("=" * 78)

csv_candidates = []

for path in files:

    if path.suffix.lower() != ".csv":
        continue

    mentions = task_mentions(path)

    filename_text = path.name.lower()

    prediction_like = any(
        keyword in filename_text
        for keyword in prediction_keywords
    )

    if mentions or prediction_like:
        csv_candidates.append(path)


print(
    f"candidate CSVs selected for header inspection: "
    f"{len(csv_candidates)}"
)


for path in csv_candidates:

    try:
        size_bytes = path.stat().st_size
    except OSError:
        size_bytes = -1

    print("\n" + "-" * 78)
    print(f"path: {path}")

    if size_bytes >= 0:
        print(
            f"size: {human_size(size_bytes)}"
        )

    if size_bytes > MAX_FILE_SIZE_FOR_HEADER_SCAN:

        print(
            "header scan: SKIPPED "
            f"(file exceeds {human_size(MAX_FILE_SIZE_FOR_HEADER_SCAN)})"
        )

        continue

    result = inspect_csv_header(path)

    print(
        f"header status: {result['status']}"
    )

    if result["columns"] is not None:
        print(
            f"column count: {result['columns']}"
        )

    if result["header"]:
        print("header:")
        print(
            "  " + ", ".join(result["header"])
        )

    if "error" in result:
        print(
            f"error: {result['error']}"
        )


# ---------------------------------------------------------------------
# Important interpretation boundary
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[6] INTERPRETATION BOUNDARY")
print("=" * 78)

print(
    "Path-name matching identifies CANDIDATE artifacts only."
)

print(
    "A filename containing T2/T3/T4/T5/T7 does not by itself "
    "establish task provenance."
)

print(
    "A filename containing prediction/score/output does not by "
    "itself establish that the file contains predictions."
)

print(
    "CSV headers are inspected only to establish possible schema."
)

print(
    "No prediction artifact is accepted as authoritative by this "
    "operation alone."
)

print(
    "No join is performed."
)

print(
    "No prediction population is selected."
)

print(
    "No model is loaded."
)


# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------

print("\n" + "=" * 78)
print("[7] MOD-005 EXECUTION SUMMARY")
print("=" * 78)

print(
    f"Files discovered under modeling root: {len(files)}"
)

for task in sorted(TARGET_TASKS):

    print(
        f"{task} path-name candidates: "
        f"{len(task_candidates[task])}"
    )

print(
    f"Prediction-like filename candidates: "
    f"{len(prediction_candidates)}"
)

print(
    f"Candidate CSVs inspected for headers: "
    f"{len(csv_candidates)}"
)

print("\nNOT performed:")
print("- model loading")
print("- prediction generation")
print("- target construction")
print("- score construction")
print("- probability conversion")
print("- evidence fusion")
print("- evaluation-population selection")
print("- artifact modification")
print("- raw dataset scanning")

print("\nSTATUS: MOD-005 EXECUTION COMPLETE")