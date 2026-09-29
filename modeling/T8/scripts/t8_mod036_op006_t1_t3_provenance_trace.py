from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op006_t1_t3_provenance_trace.json"


SOURCE_FILES = {
    "T1_baseline_report":
        ROOT / "modeling/T1/baselines/t1_it_support_baseline_report.json",

    "T1_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_svm_report.json",

    "T1_char_svm_report":
        ROOT / "modeling/T1/baselines/t1_it_support_char_svm_report.json",

    "T3_model_contract":
        ROOT / "modeling/T3/contracts/t3_model_contract.json",

    "T3_final_metrics":
        ROOT / "modeling/T3/metrics/t3_final_test_metrics.json",

    "T3_final_closure":
        ROOT / "modeling/T3/analysis/t3_final_closure.json",
}


INTERESTING_TERMS = [
    "model_path",
    "model",
    "artifact",
    "prediction",
    "probability",
    "proba",
    "validated_artifact",
    "selected_model",
    "final_candidate",
    "features",
    "target",
    "prediction_boundary",
    "recommended_use",
    "system_role",
]


def load_json(path):
    if not path.exists():
        return {
            "status": "MISSING",
            "path": str(path),
        }

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        return {
            "status": "FOUND",
            "path": str(path),
            "data": data,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "path": str(path),
            "error": str(exc),
        }


def extract_recursive(obj, path="root", output=None):
    if output is None:
        output = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            key_text = str(key).lower()

            if any(
                term in key_text
                for term in INTERESTING_TERMS
            ):
                output.append({
                    "path": f"{path}.{key}",
                    "key": key,
                    "value_type": type(value).__name__,
                    "value": (
                        value
                        if isinstance(
                            value,
                            (str, int, float, bool, type(None))
                        )
                        else str(value)[:2000]
                    ),
                })

            extract_recursive(
                value,
                f"{path}.{key}",
                output,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj[:100]):

            extract_recursive(
                value,
                f"{path}[{index}]",
                output,
            )

    return output


results = {}

for name, path in SOURCE_FILES.items():

    loaded = load_json(path)

    if loaded["status"] != "FOUND":
        results[name] = loaded
        continue

    data = loaded["data"]

    results[name] = {
        "status": "FOUND",
        "path": str(path),
        "top_level_keys": (
            list(data.keys())
            if isinstance(data, dict)
            else []
        ),
        "interesting_entries": (
            extract_recursive(data)
        ),
    }


# ---------------------------------------------------------------
# Resolve referenced paths where possible
# ---------------------------------------------------------------

referenced_paths = []

for source_name, result in results.items():

    for item in result.get(
        "interesting_entries",
        []
    ):

        value = item.get("value")

        if not isinstance(value, str):
            continue

        candidate = Path(value)

        possible_paths = [
            candidate,
            ROOT / value,
        ]

        for possible in possible_paths:

            if possible.exists():

                referenced_paths.append({
                    "source": source_name,
                    "field": item["path"],
                    "reference": value,
                    "resolved_path": str(
                        possible.resolve()
                    ),
                    "exists": True,
                    "is_file": possible.is_file(),
                })

                break


report = {
    "operation": "T8 / MOD-036 / OP-006",
    "status": "PASS",
    "purpose": (
        "Trace authoritative T1/T3 model and prediction "
        "provenance from existing contract, closure, "
        "baseline, and metric artifacts."
    ),
    "source_files": results,
    "resolved_references": referenced_paths,
    "controls": {
        "no_model_training": True,
        "no_prediction_generation": True,
        "no_dataset_modification": True,
        "creation_boundary_preserved": True,
    },
}


OUT.write_text(
    json.dumps(
        report,
        indent=2,
    )
)


print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-006")
print("=" * 80)

print()
print("T1/T3 provenance trace")
print("-" * 80)

for source_name, result in results.items():

    print()
    print(source_name)
    print(f"  Status: {result['status']}")

    if result["status"] != "FOUND":
        continue

    print(
        f"  Top-level keys: "
        f"{result.get('top_level_keys', [])}"
    )

    entries = result.get(
        "interesting_entries",
        []
    )

    print(
        f"  Relevant provenance entries: "
        f"{len(entries)}"
    )

    for item in entries[:25]:

        print(
            f"    {item['path']} = "
            f"{str(item['value'])[:300]}"
        )

print()
print("Resolved referenced files")
print("-" * 80)

if not referenced_paths:
    print("  None resolved.")

else:

    for item in referenced_paths:

        print(
            f"  {item['source']} "
            f"→ {item['field']}"
        )

        print(
            f"    {item['resolved_path']}"
        )

print()
print("Controls")
print("-" * 80)

for key, value in report["controls"].items():
    print(f"{key}: {value}")

print()
print("Status: PASS")
print(f"Artifact: {OUT}")
print("=" * 80)