from pathlib import Path
import json
import os
import platform
import subprocess
import sys


# ============================================================
# T2-MOD-015
# T2 Artifact & Environment Resolution
#
# Read-only operation.
# Does NOT install packages.
# Does NOT modify datasets.
# Does NOT load the test split.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR / "t2_artifact_env_resolution.json"
)

EXPECTED_TRAIN_ROWS = 20648
EXPECTED_VALIDATION_ROWS = 4425
EXPECTED_TEST_ROWS = 4425


def list_t2_files():
    """
    Recursively list files inside the T2 modeling directory.

    Only metadata/path information is collected.
    File contents are not read.
    """

    results = []

    if not T2_ROOT.exists():
        return results

    for path in sorted(T2_ROOT.rglob("*")):
        if path.is_file():
            try:
                size = path.stat().st_size
            except OSError:
                size = None

            results.append(
                {
                    "relative_path": str(
                        path.relative_to(T2_ROOT)
                    ),
                    "size_bytes": size,
                }
            )

    return results


def find_candidate_split_files(files):
    """
    Identify likely train/validation/test split artifacts
    from filenames only.
    """

    candidates = []

    for item in files:
        relative = item["relative_path"]
        name = Path(relative).name.lower()

        if (
            "train" in name
            or "validation" in name
            or "val" in name
            or "test" in name
            or "split" in name
        ):
            candidates.append(item)

    return candidates


def find_materialization_files(files):
    """
    Identify the already-known T2 materialization artifacts.
    """

    matches = []

    for item in files:
        relative = item["relative_path"]

        if (
            "t2_features.csv" in relative
            or "t2_materialize" in relative
        ):
            matches.append(item)

    return matches


def get_python_environment():
    """
    Record the active Python environment.
    """

    executable = Path(sys.executable)

    result = {
        "python_executable": str(executable),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "virtual_environment": os.environ.get(
            "VIRTUAL_ENV"
        ),
        "executable_exists": executable.exists(),
    }

    return result


def check_package(package_name):
    """
    Check whether a package is importable and record its version.

    No installation or modification occurs.
    """

    try:
        module = __import__(package_name)

        version = getattr(
            module,
            "__version__",
            None,
        )

        return {
            "installed": True,
            "version": version,
            "error": None,
        }

    except Exception as exc:
        return {
            "installed": False,
            "version": None,
            "error": str(exc),
        }


def check_gpu():
    """
    Read-only GPU visibility check.

    Uses nvidia-smi if available.
    Does not install or modify anything.
    """

    result = {
        "nvidia_smi_available": False,
        "gpu_detected": False,
        "nvidia_smi_output": None,
    }

    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if completed.returncode == 0:
            output = completed.stdout.strip()

            result[
                "nvidia_smi_available"
            ] = True

            result[
                "gpu_detected"
            ] = bool(output)

            result[
                "nvidia_smi_output"
            ] = output

    except (
        FileNotFoundError,
        subprocess.SubprocessError,
        OSError,
    ) as exc:
        result[
            "nvidia_smi_error"
        ] = str(exc)

    return result


def main():
    print("T2_MOD_015_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Project files
    # --------------------------------------------------------

    files = list_t2_files()

    split_candidates = find_candidate_split_files(
        files
    )

    materialization_files = (
        find_materialization_files(files)
    )

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    python_environment = (
        get_python_environment()
    )

    package_checks = {
        "torch": check_package("torch"),
        "transformers": check_package(
            "transformers"
        ),
        "tokenizers": check_package(
            "tokenizers"
        ),
        "datasets": check_package(
            "datasets"
        ),
    }

    gpu = check_gpu()

    # --------------------------------------------------------
    # Known expected locations
    # --------------------------------------------------------

    expected_paths = {
        "feature_file": (
            T2_ROOT
            / "derived"
            / "t2_features.csv"
        ),
        "expected_train": (
            T2_ROOT
            / "splits"
            / "t2_train.csv"
        ),
        "expected_validation": (
            T2_ROOT
            / "splits"
            / "t2_validation.csv"
        ),
        "expected_test": (
            T2_ROOT
            / "splits"
            / "t2_test.csv"
        ),
    }

    expected_path_status = {}

    for name, path in expected_paths.items():
        expected_path_status[name] = {
            "path": str(path),
            "exists": path.exists(),
        }

    # --------------------------------------------------------
    # Resolution decision
    # --------------------------------------------------------

    actual_split_candidates_found = (
        len(split_candidates) > 0
    )

    feature_file_found = (
        expected_paths["feature_file"].exists()
    )

    environment_packages_ready = (
        package_checks["torch"]["installed"]
        and package_checks[
            "transformers"
        ]["installed"]
        and package_checks[
            "tokenizers"
        ]["installed"]
    )

    resolution_status = (
        "READY_FOR_ENVIRONMENT_CONFIGURATION"
        if (
            actual_split_candidates_found
            and feature_file_found
        )
        else
        "SPLIT_ARTIFACT_RESOLUTION_REQUIRED"
    )

    report = {
        "operation": "T2-MOD-015",
        "operation_name": (
            "T2 Artifact & Environment Resolution"
        ),
        "task": "T2",
        "dataset": "Mozilla CORE",

        "python_environment": (
            python_environment
        ),

        "packages": package_checks,

        "gpu": gpu,

        "expected_paths": expected_path_status,

        "t2_file_inventory": {
            "total_files": len(files),
            "split_candidates": split_candidates,
            "materialization_files": (
                materialization_files
            ),
        },

        "expected_partition_sizes": {
            "train": EXPECTED_TRAIN_ROWS,
            "validation": EXPECTED_VALIDATION_ROWS,
            "test": EXPECTED_TEST_ROWS,
        },

        "resolution": {
            "feature_materialization_found": (
                feature_file_found
            ),
            "split_candidates_found": (
                actual_split_candidates_found
            ),
            "environment_packages_ready": (
                environment_packages_ready
            ),
            "training_started": False,
            "test_loaded": False,
            "packages_installed": False,
        },

        "status": resolution_status,
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
        )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print(
        "PYTHON_EXECUTABLE="
        f"{python_environment['python_executable']}"
    )

    print(
        "PYTHON_VERSION="
        f"{python_environment['python_version']}"
    )

    print(
        "VIRTUAL_ENV="
        f"{python_environment['virtual_environment']}"
    )

    print(
        "FEATURE_FILE_EXISTS="
        f"{feature_file_found}"
    )

    print(
        "EXPECTED_TRAIN_EXISTS="
        f"{expected_path_status['expected_train']['exists']}"
    )

    print(
        "EXPECTED_VALIDATION_EXISTS="
        f"{expected_path_status['expected_validation']['exists']}"
    )

    print(
        "EXPECTED_TEST_EXISTS="
        f"{expected_path_status['expected_test']['exists']}"
    )

    print(
        "SPLIT_CANDIDATES_FOUND="
        f"{len(split_candidates)}"
    )

    print(
        "TORCH_INSTALLED="
        f"{package_checks['torch']['installed']}"
    )

    print(
        "TRANSFORMERS_INSTALLED="
        f"{package_checks['transformers']['installed']}"
    )

    print(
        "TOKENIZERS_INSTALLED="
        f"{package_checks['tokenizers']['installed']}"
    )

    print(
        "DATASETS_INSTALLED="
        f"{package_checks['datasets']['installed']}"
    )

    print(
        "NVIDIA_SMI_AVAILABLE="
        f"{gpu['nvidia_smi_available']}"
    )

    print(
        "GPU_DETECTED="
        f"{gpu['gpu_detected']}"
    )

    print(
        "PACKAGES_READY="
        f"{environment_packages_ready}"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "TEST_LOADED=False"
    )

    print(
        "PACKAGES_INSTALLED=False"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "STATUS="
        f"{resolution_status}"
    )

    print("T2_MOD_015_COMPLETE")


if __name__ == "__main__":
    main()