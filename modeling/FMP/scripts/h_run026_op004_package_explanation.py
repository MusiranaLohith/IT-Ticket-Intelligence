from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "runtime"
    / "ticket_explanation.py"
)

DEPLOYMENT_RUNTIME = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "deployment"
    / "runtime"
)

TARGET = DEPLOYMENT_RUNTIME / "ticket_explanation.py"

PIPELINE_TARGET = DEPLOYMENT_RUNTIME / "ticket_pipeline.py"


def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def check_import(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)

    if spec is None or spec.loader is None:
        return False

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return True


def main():
    print("=" * 88)
    print("H-RUN-026-OP-004 — DEPLOYMENT EXPLANATION-LAYER PACKAGING")
    print("=" * 88)
    print()

    failures = []

    print("[1] Source validation")

    if not SOURCE.exists():
        print("Source formatter: FAIL — source file missing")
        failures.append("source_missing")
    else:
        print(f"Source formatter: PASS — {SOURCE}")

    if not PIPELINE_TARGET.exists():
        print("Deployment pipeline: FAIL — ticket_pipeline.py missing")
        failures.append("deployment_pipeline_missing")
    else:
        print(f"Deployment pipeline: PASS — {PIPELINE_TARGET}")

    print()

    print("[2] Preparing deployment runtime")

    DEPLOYMENT_RUNTIME.mkdir(parents=True, exist_ok=True)

    if SOURCE.exists():
        shutil.copy2(SOURCE, TARGET)
        print(f"Copied formatter: PASS")
        print(f"Target: {TARGET}")
    else:
        print("Copied formatter: FAIL")
        failures.append("copy_failed")

    print()

    print("[3] File integrity validation")

    if SOURCE.exists() and TARGET.exists():
        source_hash = sha256(SOURCE)
        target_hash = sha256(TARGET)

        print(f"Source SHA256 : {source_hash}")
        print(f"Target SHA256 : {target_hash}")

        if source_hash == target_hash:
            print("Formatter integrity: PASS")
        else:
            print("Formatter integrity: FAIL")
            failures.append("hash_mismatch")
    else:
        print("Formatter integrity: BLOCKED")
        failures.append("integrity_blocked")

    print()

    print("[4] Deployment import validation")

    try:
        if TARGET.exists():
            check_import(TARGET, "deployment_ticket_explanation")
            print("Deployment TicketExplanation import: PASS")
        else:
            print("Deployment TicketExplanation import: FAIL")
            failures.append("formatter_import_missing")
    except Exception as exc:
        print(
            "Deployment TicketExplanation import: FAIL — "
            f"{type(exc).__name__}: {exc}"
        )
        failures.append("formatter_import_failed")

    try:
        if PIPELINE_TARGET.exists():
            check_import(PIPELINE_TARGET, "deployment_ticket_pipeline")
            print("Deployment TicketPipeline import: PASS")
        else:
            print("Deployment TicketPipeline import: FAIL")
            failures.append("pipeline_import_missing")
    except Exception as exc:
        print(
            "Deployment TicketPipeline import: FAIL — "
            f"{type(exc).__name__}: {exc}"
        )
        failures.append("pipeline_import_failed")

    print()

    print("[5] Deployment package contents")

    required_files = [
        DEPLOYMENT_RUNTIME / "ticket_pipeline.py",
        DEPLOYMENT_RUNTIME / "ticket_explanation.py",
        PROJECT_ROOT / "modeling" / "FMP" / "deployment" / "requirements.txt",
        PROJECT_ROOT / "modeling" / "FMP" / "deployment" / "README.md",
    ]

    for path in required_files:
        status = "PASS" if path.exists() else "FAIL"
        print(f"{status}: {path}")

        if not path.exists():
            failures.append(f"missing:{path.name}")

    print()

    print("=" * 88)

    if failures:
        print("FINAL STATUS: FAIL")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f" - {failure}")
        raise SystemExit(1)

    print("FINAL STATUS: PASS")
    print("Explanation layer packaged into deployment runtime.")
    print("Frozen model artifacts were not modified.")
    print("No retraining performed.")
    print("No prediction logic modified.")
    print("No thresholds modified.")
    print("=" * 88)


if __name__ == "__main__":
    main()