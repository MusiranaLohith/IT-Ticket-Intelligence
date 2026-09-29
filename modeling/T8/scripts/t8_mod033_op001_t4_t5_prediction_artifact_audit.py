from pathlib import Path
import json
import pandas as pd


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T8_ROOT = ROOT / "modeling/T8"

JOINT_OOF = T8_ROOT / "t8_mod029_joint_oof.csv"

OUTPUT = (
    T8_ROOT
    / "mod033"
    / "t8_mod033_op001_t4_t5_prediction_artifact_audit.json"
)

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# Candidate locations discovered from the existing project
# structure. We audit existence first; no artifact is assumed
# to exist.

T4_ROOT = ROOT / "modeling/T4"
T5_ROOT = ROOT / "modeling/T5"


def discover_files(root):
    if not root.exists():
        return []

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and (
            path.suffix.lower()
            in {
                ".csv",
                ".json",
                ".parquet",
                ".pkl",
                ".pickle",
                ".txt",
            }
        )
    )


print("=" * 100)
print(
    "T8 MOD-033 — OP-001: "
    "T4/T5 DEVELOPMENT PREDICTION ARTIFACT "
    "AVAILABILITY / PROVENANCE AUDIT"
)
print("=" * 100)


# ------------------------------------------------------------------
# [1] T8 DEVELOPMENT POPULATION
# ------------------------------------------------------------------

print("\n[1] T8 DEVELOPMENT POPULATION")

assert JOINT_OOF.exists()

joint = pd.read_csv(
    JOINT_OOF,
    usecols=[
        "ID",
        "prediction_block",
        "prediction_creation_time",
    ],
    dtype=str,
    keep_default_na=False,
)

assert len(joint) == 16518
assert joint["ID"].nunique() == 16518

joint_ids = set(
    joint["ID"].str.strip()
)

print("T8 OoF rows:", len(joint))
print("T8 unique IDs:", len(joint_ids))
print("Development population: PASS")


# ------------------------------------------------------------------
# [2] T4 FILE DISCOVERY
# ------------------------------------------------------------------

print("\n[2] T4 ARTIFACT DISCOVERY")

print("T4 root:", T4_ROOT)

t4_files = discover_files(T4_ROOT)

if not T4_ROOT.exists():

    print("T4 root exists: NO")

else:

    print("T4 root exists: YES")
    print("Candidate data/artifact files:", len(t4_files))

    for path in t4_files:
        print("  ", path.relative_to(ROOT))

print(
    "T4 artifact discovery:",
    "FILES FOUND" if t4_files else "NO CANDIDATE FILES FOUND",
)


# ------------------------------------------------------------------
# [3] T5 FILE DISCOVERY
# ------------------------------------------------------------------

print("\n[3] T5 ARTIFACT DISCOVERY")

print("T5 root:", T5_ROOT)

t5_files = discover_files(T5_ROOT)

if not T5_ROOT.exists():

    print("T5 root exists: NO")

else:

    print("T5 root exists: YES")
    print("Candidate data/artifact files:", len(t5_files))

    for path in t5_files:
        print("  ", path.relative_to(ROOT))

print(
    "T5 artifact discovery:",
    "FILES FOUND" if t5_files else "NO CANDIDATE FILES FOUND",
)


# ------------------------------------------------------------------
# [4] FILE CONTENT INSPECTION
# ------------------------------------------------------------------

def inspect_csv(path):
    try:
        df = pd.read_csv(
            path,
            nrows=5,
            keep_default_na=False,
        )

        return {
            "path": str(path),
            "type": "csv",
            "columns": df.columns.tolist(),
            "sample_rows": len(df),
            "error": None,
        }

    except Exception as exc:

        return {
            "path": str(path),
            "type": "csv",
            "columns": [],
            "sample_rows": 0,
            "error": repr(exc),
        }


print("\n[4] CANDIDATE CSV CONTENT INSPECTION")

csv_inspections = []

for path in t4_files + t5_files:

    if path.suffix.lower() == ".csv":

        inspection = inspect_csv(path)

        csv_inspections.append(
            inspection
        )

        print(
            "\n",
            path.relative_to(ROOT),
        )

        if inspection["error"]:

            print(
                "  Read error:",
                inspection["error"],
            )

        else:

            print(
                "  Columns:",
                inspection["columns"],
            )

            print(
                "  Sample rows:",
                inspection["sample_rows"],
            )


# ------------------------------------------------------------------
# [5] PREDICTION-ARTIFACT CANDIDATE CLASSIFICATION
# ------------------------------------------------------------------

print("\n[5] PREDICTION ARTIFACT CANDIDATE CLASSIFICATION")

T4_PREDICTION_TERMS = [
    "prediction",
    "predictions",
    "oof",
    "out_of_fold",
    "validation",
    "dev",
]

T5_PREDICTION_TERMS = [
    "prediction",
    "predictions",
    "oof",
    "out_of_fold",
    "validation",
    "dev",
]


def classify_candidates(files, terms):

    candidates = []

    for path in files:

        name = path.name.lower()

        if any(
            term in name
            for term in terms
        ):

            candidates.append(path)

    return candidates


t4_prediction_candidates = (
    classify_candidates(
        t4_files,
        T4_PREDICTION_TERMS,
    )
)

t5_prediction_candidates = (
    classify_candidates(
        t5_files,
        T5_PREDICTION_TERMS,
    )
)

print("\nT4 prediction-like filenames:")

for path in t4_prediction_candidates:
    print(
        "  ",
        path.relative_to(ROOT),
    )

print("\nT5 prediction-like filenames:")

for path in t5_prediction_candidates:
    print(
        "  ",
        path.relative_to(ROOT),
    )


# ------------------------------------------------------------------
# [6] ID-ADDRESSABILITY INSPECTION
# ------------------------------------------------------------------

print("\n[6] ID-ADDRESSABILITY INSPECTION")

id_candidate_results = []


for task, candidates in [
    ("T4", t4_prediction_candidates),
    ("T5", t5_prediction_candidates),
]:

    print("\n", task)

    for path in candidates:

        result = {
            "task": task,
            "path": str(path),
            "readable": False,
            "has_ID": False,
            "row_count": None,
            "overlap_with_t8_oof": None,
            "columns": [],
            "error": None,
        }

        try:

            if path.suffix.lower() == ".csv":

                df = pd.read_csv(
                    path,
                    keep_default_na=False,
                )

                result["readable"] = True
                result["columns"] = (
                    df.columns.tolist()
                )

                if "ID" in df.columns:

                    result["has_ID"] = True

                    ids = set(
                        df["ID"]
                        .astype(str)
                        .str.strip()
                    )

                    result["row_count"] = len(df)

                    result[
                        "overlap_with_t8_oof"
                    ] = len(
                        ids & joint_ids
                    )

                    print(
                        f"  {path.relative_to(ROOT)}"
                    )

                    print(
                        "    rows:",
                        len(df),
                    )

                    print(
                        "    has ID: YES",
                    )

                    print(
                        "    overlap with T8 OoF:",
                        result[
                            "overlap_with_t8_oof"
                        ],
                    )

                else:

                    print(
                        f"  {path.relative_to(ROOT)}"
                    )

                    print(
                        "    rows:",
                        len(df),
                    )

                    print(
                        "    has ID: NO",
                    )

            else:

                print(
                    f"  {path.relative_to(ROOT)}"
                )

                print(
                    "    non-CSV artifact; "
                    "not treated as prediction table",
                )

        except Exception as exc:

            result["error"] = repr(exc)

            print(
                "    read error:",
                repr(exc),
            )

        id_candidate_results.append(
            result
        )


# ------------------------------------------------------------------
# [7] NATIVE SEMANTICS REMINDER
# ------------------------------------------------------------------

print("\n[7] NATIVE SEMANTICS")

print(
    "T4 native role: Assignee ranking / retrieval"
)

print(
    "T5 native role: Duplicate relationship prediction"
)

print(
    "T4 ranking must not be converted to probability "
    "without a validated mapping."
)

print(
    "T5 duplicate probability must not be treated "
    "as duplicate identity."
)

print(
    "No semantic reinterpretation performed: PASS"
)


# ------------------------------------------------------------------
# [8] DEVELOPMENT ELIGIBILITY PRELIMINARY STATUS
# ------------------------------------------------------------------

print("\n[8] DEVELOPMENT ELIGIBILITY PRELIMINARY STATUS")

t4_id_addressable = any(
    result["task"] == "T4"
    and result["readable"]
    and result["has_ID"]
    and result["overlap_with_t8_oof"]
    and result["overlap_with_t8_oof"] > 0
    for result in id_candidate_results
)

t5_id_addressable = any(
    result["task"] == "T5"
    and result["readable"]
    and result["has_ID"]
    and result["overlap_with_t8_oof"]
    and result["overlap_with_t8_oof"] > 0
    for result in id_candidate_results
)

print(
    "T4 ID-addressable development candidate:",
    t4_id_addressable,
)

print(
    "T5 ID-addressable development candidate:",
    t5_id_addressable,
)

print(
    "\nImportant:"
)

print(
    "File discovery alone does NOT establish "
    "fusion eligibility."
)

print(
    "Prediction provenance, split origin, "
    "prediction boundary, and semantic validity "
    "must be established before use."
)


# ------------------------------------------------------------------
# [9] SAVE
# ------------------------------------------------------------------

print("\n[9] SAVE AUDIT")

audit = {
    "module": "T8-MOD-033",
    "operation": "OP-001",
    "t8_development_population": len(joint),
    "t4_root_exists": T4_ROOT.exists(),
    "t5_root_exists": T5_ROOT.exists(),
    "t4_files": [
        str(path.relative_to(ROOT))
        for path in t4_files
    ],
    "t5_files": [
        str(path.relative_to(ROOT))
        for path in t5_files
    ],
    "csv_inspections": csv_inspections,
    "prediction_artifact_candidates": {
        "T4": [
            str(path.relative_to(ROOT))
            for path in t4_prediction_candidates
        ],
        "T5": [
            str(path.relative_to(ROOT))
            for path in t5_prediction_candidates
        ],
    },
    "id_candidate_results":
        id_candidate_results,
    "t4_id_addressable_candidate":
        t4_id_addressable,
    "t5_id_addressable_candidate":
        t5_id_addressable,
    "locked_evaluation_used": False,
    "fusion_model_trained": False,
}

with OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        audit,
        f,
        indent=2,
    )

print(
    "Audit written:",
    OUTPUT,
)


# ------------------------------------------------------------------
# [10] FINAL STATUS
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("MOD-033 OP-001 COMPLETE")
print("=" * 100)

print(
    "T4 artifact discovery: PASS"
)

print(
    "T5 artifact discovery: PASS"
)

print(
    "Candidate content inspection: PASS"
)

print(
    "ID-addressability inspection: PASS"
)

print(
    "Native semantic guard: PASS"
)

print(
    "Locked evaluation used: NO"
)

print(
    "Fusion model trained: NO"
)

print(
    "T4/T5 fusion eligibility: "
    "NOT YET ESTABLISHED"
)

print("=" * 100)