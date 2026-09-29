from pathlib import Path
import ast
import json


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODELING_ROOT = PROJECT_ROOT / "modeling"
FMP_ROOT = MODELING_ROOT / "FMP"
METRICS_DIR = FMP_ROOT / "metrics"

OUTPUT = METRICS_DIR / "h_op001_runtime_interface_inventory.json"


TASKS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


def safe_read_text(path):
    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace"
        )
    except Exception:
        return ""


def inspect_python_file(path):
    record = {
        "path": str(path),
        "functions": [],
        "classes": [],
        "main_guard": False,
        "syntax_valid": False,
    }

    source = safe_read_text(path)

    if not source:
        return record

    try:
        tree = ast.parse(source)
        record["syntax_valid"] = True
    except SyntaxError:
        return record

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            record["functions"].append(node.name)

        elif isinstance(node, ast.AsyncFunctionDef):
            record["functions"].append(node.name)

        elif isinstance(node, ast.ClassDef):
            record["classes"].append(node.name)

        elif isinstance(node, ast.If):
            try:
                condition = ast.unparse(node.test)

                if (
                    "__name__" in condition
                    and "__main__" in condition
                ):
                    record["main_guard"] = True

            except Exception:
                pass

    return record


def classify_python_file(path):
    name = path.name.lower()

    if "test" in name:
        return False

    if "__pycache__" in str(path):
        return False

    return True


def main():

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 72)
    print("H-OP-001 — RUNTIME INTERFACE INVENTORY")
    print("=" * 72)

    results = {}

    for task in TASKS:

        task_root = MODELING_ROOT / task

        if not task_root.exists():
            results[task] = {
                "task_root_exists": False,
                "python_files": [],
            }
            continue

        python_files = []

        for path in task_root.rglob("*.py"):

            if not classify_python_file(path):
                continue

            python_files.append(
                inspect_python_file(path)
            )

        results[task] = {
            "task_root_exists": True,
            "python_file_count": len(python_files),
            "python_files": python_files,
        }

    # --------------------------------------------------------------
    # Also inspect the FMP runtime/integration area.
    # --------------------------------------------------------------

    fmp_python_files = []

    if FMP_ROOT.exists():

        for path in FMP_ROOT.rglob("*.py"):

            if not classify_python_file(path):
                continue

            fmp_python_files.append(
                inspect_python_file(path)
            )

    # --------------------------------------------------------------
    # Identify likely runtime candidates.
    #
    # This is discovery only. We do NOT declare any file to be the
    # official runtime entrypoint automatically.
    # --------------------------------------------------------------

    runtime_keywords = (
        "runtime",
        "inference",
        "predict",
        "pipeline",
        "serve",
        "entry",
        "interface",
        "wrapper",
        "orchestr",
    )

    candidates = []

    for task, task_data in results.items():

        for record in task_data.get(
            "python_files",
            []
        ):

            filename = Path(
                record["path"]
            ).name.lower()

            score = sum(
                keyword in filename
                for keyword in runtime_keywords
            )

            if score > 0:

                candidates.append({
                    "task": task,
                    "path": record["path"],
                    "keyword_match_count": score,
                    "functions": record["functions"],
                    "classes": record["classes"],
                    "main_guard": record["main_guard"],
                })

    for record in fmp_python_files:

        filename = Path(
            record["path"]
        ).name.lower()

        score = sum(
            keyword in filename
            for keyword in runtime_keywords
        )

        if score > 0:

            candidates.append({
                "task": "FMP",
                "path": record["path"],
                "keyword_match_count": score,
                "functions": record["functions"],
                "classes": record["classes"],
                "main_guard": record["main_guard"],
            })

    # --------------------------------------------------------------
    # Existing final-phase evidence.
    # --------------------------------------------------------------

    freeze_manifest = (
        METRICS_DIR
        / "fmp07_op006_final_modeling_freeze_release_manifest.json"
    )

    fmp06_closure = (
        METRICS_DIR
        / "fmp06_final_phase_closure.json"
    )

    source_evidence = {
        "fmp07_final_freeze_manifest_exists":
            freeze_manifest.exists(),

        "fmp06_final_phase_closure_exists":
            fmp06_closure.exists(),
    }

    # --------------------------------------------------------------
    # Final inventory record.
    # --------------------------------------------------------------

    result = {
        "operation": "H-OP-001",
        "operation_name":
            "Runtime Interface Inventory",

        "status": "PASS",

        "purpose": (
            "Read-only inventory of existing T1-T7 Python runtime "
            "interfaces and FMP integration candidates before "
            "constructing a new-ticket runtime orchestrator."
        ),

        "tasks": results,

        "fmp_python_files": fmp_python_files,

        "runtime_candidates": candidates,

        "source_evidence": source_evidence,

        "controls": {
            "model_execution": False,
            "model_retraining": False,
            "model_selection": False,
            "artifact_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
        },

        "interpretation_boundary": (
            "Filename or source inspection does not by itself "
            "establish an official runtime entrypoint. Candidate "
            "files require manual/interface reconciliation before "
            "being used by the production demonstration pipeline."
        ),

        "next_operation":
            "H-OP-002 — reconcile actual T1-T7 callable interfaces "
            "and determine the minimal single-ticket runtime contract.",

        "output":
            str(OUTPUT),
    }

    with OUTPUT.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2
        )

    # --------------------------------------------------------------
    # Compact terminal output.
    # --------------------------------------------------------------

    print()

    for task in TASKS:

        task_data = results[task]

        print(
            f"{task}: "
            f"root={task_data.get('task_root_exists')} "
            f"python_files={task_data.get('python_file_count', 0)}"
        )

    print()

    print(
        f"FMP Python files: "
        f"{len(fmp_python_files)}"
    )

    print(
        f"Runtime candidates: "
        f"{len(candidates)}"
    )

    print(
        "Freeze manifest exists: "
        f"{source_evidence['fmp07_final_freeze_manifest_exists']}"
    )

    print(
        "FMP-06 closure exists: "
        f"{source_evidence['fmp06_final_phase_closure_exists']}"
    )

    print()

    print(
        f"OUTPUT: {OUTPUT}"
    )

    print(
        "STATUS: PASS"
    )


if __name__ == "__main__":
    main()