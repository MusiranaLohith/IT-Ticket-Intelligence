from pathlib import Path
import csv
import json
import re


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op003_authoritative_artifact_resolution.json"


# ------------------------------------------------------------------
# Search scope
# ------------------------------------------------------------------

TASKS = ["T1", "T3", "T6", "T7"]

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}


# ------------------------------------------------------------------
# Filename/path signals
# ------------------------------------------------------------------

POSITIVE_TERMS = [
    "prediction",
    "predictions",
    "probability",
    "probabilities",
    "proba",
    "oof",
    "out_of_fold",
    "output",
    "outputs",
    "evidence",
    "result",
    "results",
    "inference",
    "eval",
    "evaluation",
    "checkpoint",
    "survival",
    "ranking",
    "ranked",
    "retrieval",
    "candidate",
]

NEGATIVE_TERMS = [
    "script",
    "scripts",
    "source",
    "src",
    "readme",
    "log",
    "cache",
    "debug",
    "test_",
    "unit_test",
    "requirements",
    "pycache",
]


def is_excluded(path):
    return any(part in EXCLUDED_PARTS for part in path.parts)


def task_matches(path, task):
    """
    Match task identifiers conservatively.

    Examples accepted:
      T7/
      t7_
      t7-
      T7-
      t7_mod
      modeling/T7/...
    """
    text = str(path.relative_to(ROOT))

    pattern = rf"(?i)(^|[/_-]){re.escape(task)}($|[/_.-])"

    return bool(re.search(pattern, text))


def score_candidate(path):
    """
    Heuristic ranking only.
    This does NOT declare an artifact authoritative.
    """
    text = str(path.relative_to(ROOT)).lower()
    name = path.name.lower()

    score = 0
    reasons = []

    for term in POSITIVE_TERMS:
        if term in text:
            score += 2
            reasons.append(f"+{term}")

    for term in NEGATIVE_TERMS:
        if term in text:
            score -= 3
            reasons.append(f"-{term}")

    suffix = path.suffix.lower()

    if suffix in {".csv", ".json", ".npz", ".pkl", ".pickle", ".parquet"}:
        score += 3
        reasons.append("+artifact_format")

    if suffix in {".py", ".sh"}:
        score -= 5
        reasons.append("-executable_source")

    if "modeling" in text:
        score += 1
        reasons.append("+modeling")

    return score, reasons


def inspect_json(path):
    result = {
        "readable": False,
        "type": None,
        "keys": [],
        "interesting_keys": [],
    }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        result["readable"] = True
        result["type"] = type(data).__name__

        if isinstance(data, dict):
            result["keys"] = list(data.keys())[:100]

            interesting = [
                k for k in data.keys()
                if any(
                    term in str(k).lower()
                    for term in [
                        "prediction",
                        "prob",
                        "output",
                        "evidence",
                        "score",
                        "target",
                        "metric",
                        "feature",
                        "survival",
                        "rank",
                        "candidate",
                        "id",
                    ]
                )
            ]

            result["interesting_keys"] = interesting[:100]

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_csv_header(path):
    result = {
        "readable": False,
        "columns": [],
        "interesting_columns": [],
    }

    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as f:

            reader = csv.reader(f)
            header = next(reader)

        result["readable"] = True
        result["columns"] = header

        interesting = [
            c for c in header
            if any(
                term in c.lower()
                for term in [
                    "id",
                    "prediction",
                    "prob",
                    "score",
                    "rank",
                    "target",
                    "label",
                    "evidence",
                    "candidate",
                    "survival",
                    "time",
                    "event",
                    "status",
                    "query",
                    "assignee",
                    "priority",
                    "duplicate",
                ]
            )
        ]

        result["interesting_columns"] = interesting

    except Exception as exc:
        result["error"] = str(exc)

    return result


def inspect_artifact(path):
    score, reasons = score_candidate(path)

    result = {
        "path": str(path.relative_to(ROOT)),
        "filename": path.name,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "score": score,
        "score_reasons": reasons,
    }

    if path.suffix.lower() == ".json":
        result["content_inspection"] = inspect_json(path)

    elif path.suffix.lower() == ".csv":
        result["content_inspection"] = inspect_csv_header(path)

    else:
        result["content_inspection"] = {
            "readable": False,
            "inspection": "header inspection not applicable",
        }

    return result


# ------------------------------------------------------------------
# Discover candidates
# ------------------------------------------------------------------

task_candidates = {}

all_files = [
    p for p in ROOT.rglob("*")
    if p.is_file() and not is_excluded(p)
]


for task in TASKS:

    matches = [
        p for p in all_files
        if task_matches(p, task)
    ]

    inspected = [
        inspect_artifact(p)
        for p in matches
    ]

    inspected.sort(
        key=lambda x: (
            -x["score"],
            -x["size_bytes"],
            x["path"],
        )
    )

    task_candidates[task] = {
        "candidate_count": len(inspected),
        "candidates": inspected,
    }


# ------------------------------------------------------------------
# Already established authoritative inputs
# ------------------------------------------------------------------

established = {
    "T2": {
        "task": "T2",
        "native_role": "Priority Prediction",
        "authoritative_prediction_evidence": [
            "T2 chronological OoF predictions generated under MOD-029",
            "T2 frozen model contract preserved",
        ],
        "important_note": (
            "The T2 test.csv inspected during OP-002 is a split/target "
            "artifact, not by itself the prediction interface."
        ),
    },

    "T4": {
        "task": "T4",
        "native_role": "Assignee Retrieval",
        "authoritative_prediction_evidence": [
            "modeling/T4/results/mod011_checkpoints/t4_mod011_retrieval.npz"
        ],
        "important_note": (
            "Checkpoint row order corresponds to t4_eval.csv row order."
        ),
    },

    "T5": {
        "task": "T5",
        "native_role": "Duplicate Prediction",
        "authoritative_prediction_evidence": [
            "modeling/T5/metrics/t5_mod007_calibrated_validation_predictions.npz",
            "modeling/T5/metrics/t5_mod011_final_closure.json",
        ],
        "important_note": (
            "p_sigmoid is the accepted calibrated probability output "
            "for the native T5 pipeline."
        ),
    },
}


# ------------------------------------------------------------------
# Resolution rules
# ------------------------------------------------------------------

resolution_rules = {
    "authoritative_definition": (
        "An artifact is not declared authoritative solely by filename. "
        "It must be traceable to the frozen task contract and its "
        "generation/evaluation provenance."
    ),
    "prediction_preference": (
        "Prefer actual inference/OoF prediction or evidence artifacts "
        "over training data, targets, scripts, logs, and documentation."
    ),
    "boundary": "Creation",
    "post_creation_information": False,
    "semantic_conversion": False,
    "synthetic_fusion_output": False,
}


# ------------------------------------------------------------------
# Report
# ------------------------------------------------------------------

report = {
    "operation": "T8 / MOD-036 / OP-003",
    "status": "PASS",
    "purpose": (
        "Resolve candidate T1/T3/T6/T7 artifacts for the T8 "
        "Decision Engine input interface without declaring "
        "authority from filename alone."
    ),
    "established_native_inputs": established,
    "candidate_resolution": task_candidates,
    "resolution_rules": resolution_rules,
}


OUT.write_text(
    json.dumps(report, indent=2)
)


# ------------------------------------------------------------------
# Terminal summary
# ------------------------------------------------------------------

print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-003")
print("=" * 80)

print()
print("Candidate artifact resolution")
print("-" * 80)

for task in TASKS:

    info = task_candidates[task]

    print(
        f"{task}: "
        f"{info['candidate_count']} candidate artifacts"
    )

    print("  Top candidates:")

    for candidate in info["candidates"][:10]:

        print(
            f"    [{candidate['score']:>3}] "
            f"{candidate['path']}"
        )

        inspection = candidate.get(
            "content_inspection",
            {}
        )

        interesting = inspection.get(
            "interesting_columns",
            []
        )

        if interesting:
            print(
                f"         fields: {interesting[:15]}"
            )

        interesting_keys = inspection.get(
            "interesting_keys",
            []
        )

        if interesting_keys:
            print(
                f"         keys: {interesting_keys[:15]}"
            )

print()
print("Already established native inputs")
print("-" * 80)

for task, info in established.items():

    print(f"{task}: {info['native_role']}")

    for artifact in info["authoritative_prediction_evidence"]:
        print(f"  - {artifact}")

print()
print("Resolution rule:")
print(
    "  Filename ranking is discovery assistance only; "
    "authority requires provenance and contract compatibility."
)

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)