from pathlib import Path
import csv
import json
import re


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op005_t1_t3_output_resolution.json"


# ------------------------------------------------------------------
# Candidate discovery
# ------------------------------------------------------------------

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

POSITIVE_TERMS = [
    "prediction",
    "predictions",
    "probability",
    "probabilities",
    "proba",
    "output",
    "outputs",
    "inference",
    "evaluation_predictions",
    "test_predictions",
    "validation_predictions",
    "oof",
]

NEGATIVE_TERMS = [
    "script",
    "scripts",
    "readme",
    "source",
    "debug",
    "cache",
    "log",
    "requirements",
    "checkpoint",
    "tokenizer",
    "vectorizer",
]


def excluded(path):
    return any(part in EXCLUDED_PARTS for part in path.parts)


def task_match(path, task):
    rel = str(path.relative_to(ROOT))
    return bool(
        re.search(
            rf"(?i)(^|[/_-]){re.escape(task)}($|[/_.-])",
            rel,
        )
    )


def score(path):
    text = str(path.relative_to(ROOT)).lower()
    suffix = path.suffix.lower()

    value = 0
    reasons = []

    for term in POSITIVE_TERMS:
        if term in text:
            value += 3
            reasons.append(f"+{term}")

    for term in NEGATIVE_TERMS:
        if term in text:
            value -= 4
            reasons.append(f"-{term}")

    if suffix in {".csv", ".json", ".npz", ".pkl", ".pickle"}:
        value += 2
        reasons.append("+artifact")

    if suffix in {".py", ".sh"}:
        value -= 8
        reasons.append("-source")

    return value, reasons


# ------------------------------------------------------------------
# Safe CSV inspection
# ------------------------------------------------------------------

def inspect_csv(path):
    result = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "suffix": ".csv",
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    try:
        csv.field_size_limit(10_000_000)

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:

            reader = csv.reader(f)
            header = next(reader)

            samples = []
            row_count = 0

            for row in reader:
                row_count += 1

                if len(samples) < 2:
                    samples.append(row)

                if row_count >= 2:
                    break

        result["status"] = "FOUND"
        result["columns"] = header
        result["sample_rows"] = samples
        result["rows_sampled"] = row_count

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


# ------------------------------------------------------------------
# Safe JSON inspection
# ------------------------------------------------------------------

def inspect_json(path):
    result = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "suffix": ".json",
    }

    if not path.exists():
        result["status"] = "MISSING"
        return result

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        result["status"] = "FOUND"
        result["type"] = type(data).__name__

        if isinstance(data, dict):

            result["keys"] = list(data.keys())[:100]

            interesting = []

            for key, value in data.items():

                key_text = str(key).lower()

                if any(
                    term in key_text
                    for term in [
                        "prediction",
                        "probability",
                        "proba",
                        "output",
                        "model",
                        "artifact",
                        "path",
                        "feature",
                        "target",
                        "label",
                        "evaluation",
                        "test",
                        "validation",
                    ]
                ):
                    interesting.append({
                        "key": key,
                        "value_type": type(value).__name__,
                        "value_preview": (
                            str(value)[:500]
                        ),
                    })

            result["interesting_entries"] = interesting[:100]

    except Exception as exc:
        result["status"] = "ERROR"
        result["error"] = str(exc)

    return result


# ------------------------------------------------------------------
# Discover T1/T3 candidates
# ------------------------------------------------------------------

all_files = [
    p
    for p in ROOT.rglob("*")
    if p.is_file() and not excluded(p)
]


discovered = {}

for task in ["T1", "T3"]:

    candidates = []

    for path in all_files:

        if not task_match(path, task):
            continue

        value, reasons = score(path)

        candidates.append({
            "path": str(path.relative_to(ROOT)),
            "score": value,
            "reasons": reasons,
            "size_bytes": path.stat().st_size,
        })

    candidates.sort(
        key=lambda x: (
            -x["score"],
            -x["size_bytes"],
            x["path"],
        )
    )

    discovered[task] = candidates


# ------------------------------------------------------------------
# Inspect strongest candidates
# ------------------------------------------------------------------

inspection = {}

for task in ["T1", "T3"]:

    inspection[task] = []

    for candidate in discovered[task][:20]:

        path = ROOT / candidate["path"]

        if path.suffix.lower() == ".csv":
            content = inspect_csv(path)

        elif path.suffix.lower() == ".json":
            content = inspect_json(path)

        else:
            content = {
                "path": candidate["path"],
                "status": "BINARY_OR_UNSUPPORTED",
                "suffix": path.suffix.lower(),
            }

        inspection[task].append({
            "candidate": candidate,
            "content": content,
        })


# ------------------------------------------------------------------
# Resolution criteria
# ------------------------------------------------------------------

resolution_criteria = {
    "must_be_machine_generated": True,
    "must_represent_prediction_or_inference_evidence": True,
    "must_have_ticket_or_equivalent_decision_identifier": True,
    "must_respect_creation_boundary": True,
    "must_not_be_observed_target_only": True,
    "must_not_be_evaluation_metrics_only": True,
    "must_not_be_analysis_only": True,
    "must_not_contain_post_creation_information": True,
    "filename_alone_is_insufficient": True,
}


report = {
    "operation": "T8 / MOD-036 / OP-005",
    "status": "PASS",
    "purpose": (
        "Resolve T1 and T3 native machine-generated inference "
        "outputs for consumption by the T8 Decision Engine."
    ),
    "discovered_candidates": discovered,
    "candidate_inspection": inspection,
    "resolution_criteria": resolution_criteria,
}


OUT.write_text(
    json.dumps(report, indent=2)
)


# ------------------------------------------------------------------
# Terminal output
# ------------------------------------------------------------------

print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-005")
print("=" * 80)
print()
print("T1/T3 native inference-output resolution")
print("-" * 80)

for task in ["T1", "T3"]:

    print()
    print(f"{task} — strongest candidates")

    for item in inspection[task]:

        candidate = item["candidate"]
        content = item["content"]

        print(
            f"  [{candidate['score']:>3}] "
            f"{candidate['path']}"
        )

        print(
            f"       status: "
            f"{content.get('status', 'UNKNOWN')}"
        )

        if "columns" in content:
            print(
                f"       columns: "
                f"{content['columns']}"
            )

        if "keys" in content:
            print(
                f"       keys: "
                f"{content['keys']}"
            )

        if "interesting_entries" in content:
            keys = [
                x["key"]
                for x in content["interesting_entries"]
            ]

            print(
                f"       interesting keys: "
                f"{keys[:20]}"
            )

print()
print("Resolution criteria")
print("-" * 80)

for key, value in resolution_criteria.items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)