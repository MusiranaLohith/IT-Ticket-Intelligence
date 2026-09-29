from pathlib import Path
import json
import joblib


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8 = ROOT / "modeling/T8"

OUT_DIR = T8 / "mod036"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT = OUT_DIR / "t8_mod036_op008_t1_t3_artifact_structure.json"


# ------------------------------------------------------------------
# T3 serialized artifact structure
# ------------------------------------------------------------------

T3_MODEL = (
    ROOT
    / "modeling/T3/models/"
    / "t3_class_weighted_tfidf_logreg.joblib"
)


def describe_value(value, depth=0, max_depth=3):
    if depth > max_depth:
        return {
            "type": type(value).__name__,
            "truncated": True,
        }

    result = {
        "type": type(value).__name__,
    }

    if isinstance(value, dict):
        result["keys"] = list(value.keys())[:100]

        children = {}

        for key, child in list(value.items())[:100]:
            children[str(key)] = describe_value(
                child,
                depth + 1,
                max_depth,
            )

        result["children"] = children

    elif isinstance(value, (list, tuple)):
        result["length"] = len(value)

        if value:
            result["first_items"] = [
                describe_value(
                    item,
                    depth + 1,
                    max_depth,
                )
                for item in value[:10]
            ]

    else:
        try:
            text = str(value)

            if len(text) > 500:
                text = text[:500] + "...<truncated>"

            result["value_preview"] = text

        except Exception:
            result["value_preview"] = "<unprintable>"

    return result


t3_result = {
    "path": str(T3_MODEL),
    "exists": T3_MODEL.exists(),
}


if T3_MODEL.exists():

    try:
        t3_object = joblib.load(T3_MODEL)

        t3_result["status"] = "LOADED"
        t3_result["structure"] = describe_value(
            t3_object
        )

    except Exception as exc:

        t3_result["status"] = "LOAD_ERROR"
        t3_result["error"] = str(exc)

else:

    t3_result["status"] = "MISSING"


# ------------------------------------------------------------------
# T1 report references
# ------------------------------------------------------------------

T1_REPORTS = [
    ROOT / "modeling/T1/baselines/t1_it_support_baseline_report.json",
    ROOT / "modeling/T1/baselines/t1_it_support_svm_report.json",
    ROOT / "modeling/T1/baselines/t1_it_support_char_svm_report.json",
    ROOT / "modeling/T1/baselines/t1_vscode_baseline_report.json",
]


def load_json(path):

    if not path.exists():
        return {
            "status": "MISSING",
            "path": str(path),
        }

    try:
        return {
            "status": "FOUND",
            "path": str(path),
            "data": json.loads(
                path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            ),
        }

    except Exception as exc:

        return {
            "status": "ERROR",
            "path": str(path),
            "error": str(exc),
        }


t1_reports = []

for path in T1_REPORTS:

    loaded = load_json(path)

    if loaded["status"] != "FOUND":
        t1_reports.append(loaded)
        continue

    data = loaded["data"]

    references = {}

    if isinstance(data, dict):

        for key in [
            "model_path",
            "analysis_path",
            "probability_output",
            "artifacts",
            "model",
            "status",
            "task",
        ]:

            if key in data:
                references[key] = data[key]

    t1_reports.append({
        "path": str(path),
        "status": "FOUND",
        "references": references,
    })


# ------------------------------------------------------------------
# T1 artifact directory inventory
# ------------------------------------------------------------------

T1_DIRECTORIES = [
    ROOT / "modeling/T1",
    ROOT / "modeling/baselines",
]


def inventory_directory(directory):

    result = {
        "directory": str(directory),
        "exists": directory.exists(),
        "files": [],
    }

    if not directory.exists():
        return result

    for path in sorted(directory.rglob("*")):

        if not path.is_file():
            continue

        if any(
            part in {
                ".git",
                ".venv",
                "__pycache__",
            }
            for part in path.parts
        ):
            continue

        result["files"].append({
            "path": str(path.relative_to(ROOT)),
            "suffix": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
        })

    return result


t1_inventory = [
    inventory_directory(directory)
    for directory in T1_DIRECTORIES
]


# ------------------------------------------------------------------
# Locate report-referenced paths
# ------------------------------------------------------------------

referenced_paths = []


for report in t1_reports:

    if report.get("status") != "FOUND":
        continue

    references = report.get(
        "references",
        {},
    )

    def walk(value, field_path):

        if isinstance(value, dict):

            for key, child in value.items():
                walk(
                    child,
                    f"{field_path}.{key}",
                )

        elif isinstance(value, list):

            for index, child in enumerate(value):
                walk(
                    child,
                    f"{field_path}[{index}]",
                )

        elif isinstance(value, str):

            candidate = Path(value)

            possibilities = [
                candidate,
                ROOT / value,
            ]

            for possible in possibilities:

                if possible.exists():

                    referenced_paths.append({
                        "source_report": report["path"],
                        "field": field_path,
                        "reference": value,
                        "resolved_path": str(
                            possible.resolve()
                        ),
                        "is_file": possible.is_file(),
                    })

                    break

    walk(
        references,
        "references",
    )


# ------------------------------------------------------------------
# Report
# ------------------------------------------------------------------

report = {
    "operation": "T8 / MOD-036 / OP-008",
    "status": "PASS",
    "purpose": (
        "Inspect T3 serialized model structure and reconcile "
        "T1 report-referenced model artifacts with the actual "
        "project filesystem."
    ),
    "t3_model_structure": t3_result,
    "t1_report_references": t1_reports,
    "t1_artifact_directories": t1_inventory,
    "resolved_t1_references": referenced_paths,
    "controls": {
        "training_performed": False,
        "prediction_generation_performed": False,
        "model_modified": False,
        "dataset_modified": False,
        "creation_boundary_preserved": True,
    },
}


OUT.write_text(
    json.dumps(
        report,
        indent=2,
    )
)


# ------------------------------------------------------------------
# Terminal output
# ------------------------------------------------------------------

print("=" * 80)
print("T8 DECISION ENGINE — MOD-036 OP-008")
print("=" * 80)

print()
print("T3 serialized model structure")
print("-" * 80)

print(f"Path: {t3_result['path']}")
print(f"Exists: {t3_result['exists']}")
print(f"Status: {t3_result['status']}")

if "structure" in t3_result:

    structure = t3_result["structure"]

    print(
        f"Type: {structure.get('type')}"
    )

    if "keys" in structure:
        print(
            f"Keys: {structure['keys']}"
        )

    children = structure.get(
        "children",
        {},
    )

    for key, value in children.items():

        print(
            f"  {key}: "
            f"{value.get('type')}"
        )

print()
print("T1 report references")
print("-" * 80)

for report_item in t1_reports:

    print(
        f"{report_item['path']}: "
        f"{report_item['status']}"
    )

    if report_item["status"] == "FOUND":

        for key, value in report_item.get(
            "references",
            {}
        ).items():

            print(
                f"  {key}: "
                f"{str(value)[:500]}"
            )

print()
print("Resolved T1 references")
print("-" * 80)

if referenced_paths:

    for item in referenced_paths:

        print(
            f"{item['source_report']}"
        )

        print(
            f"  {item['field']} "
            f"→ {item['resolved_path']}"
        )

else:

    print("None resolved.")

print()
print("T1 artifact inventory")
print("-" * 80)

for inventory in t1_inventory:

    print(
        f"{inventory['directory']}: "
        f"{len(inventory['files'])} files"
    )

    for item in inventory["files"]:
        print(
            f"  {item['path']} "
            f"({item['size_bytes']} bytes)"
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