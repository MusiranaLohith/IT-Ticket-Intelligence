from pathlib import Path
import json
import shutil
import subprocess
import sys


# ============================================================
# T2-MOD-017
# Transformer Environment Configuration
#
# Creates ONLY a dedicated T2 transformer virtual environment.
#
# Does NOT:
#   - install PyTorch
#   - install Transformers
#   - modify datasets
#   - load the test set
#   - train a model
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

ENV_DIR = (
    PROJECT_ROOT / ".t2-transformer-venv"
)

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "t2_transformer_env_configuration.json"
)


def find_python(executable_name):
    """
    Locate a system Python executable without modifying it.
    """

    path = shutil.which(executable_name)

    if path is None:
        return None

    return Path(path)


def get_python_version(python_path):
    """
    Return the version of a Python executable.
    """

    try:
        result = subprocess.run(
            [
                str(python_path),
                "--version",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        output = (
            result.stdout.strip()
            or result.stderr.strip()
        )

        return output

    except (
        subprocess.SubprocessError,
        OSError,
    ) as exc:
        return f"ERROR: {exc}"


def main():
    print("T2_MOD_017_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Confirm current project environment.
    # --------------------------------------------------------

    current_python = Path(
        sys.executable
    )

    current_version = get_python_version(
        current_python
    )

    # --------------------------------------------------------
    # Look for Python 3.12.
    # --------------------------------------------------------

    python_candidates = [
        "python3.12",
        "python3.11",
        "python3.10",
    ]

    available = []

    for executable in python_candidates:
        path = find_python(executable)

        if path is None:
            continue

        available.append(
            {
                "executable": str(path),
                "version": get_python_version(path),
            }
        )

    selected_python = None

    for item in available:
        if "Python 3.12." in item["version"]:
            selected_python = Path(
                item["executable"]
            )
            break

    # --------------------------------------------------------
    # If Python 3.12 isn't available, do not guess.
    # --------------------------------------------------------

    if selected_python is None:

        report = {
            "operation": "T2-MOD-017",
            "operation_name": (
                "Transformer Environment Configuration"
            ),
            "current_environment": {
                "python": str(current_python),
                "version": current_version,
            },
            "available_compatible_pythons": available,
            "selected_python": None,
            "environment_path": str(ENV_DIR),
            "environment_created": False,
            "packages_installed": False,
            "training_started": False,
            "test_loaded": False,
            "status": (
                "PYTHON_3_12_NOT_AVAILABLE"
            ),
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

        print(
            "CURRENT_PYTHON="
            f"{current_version}"
        )

        print(
            "PYTHON_3_12_AVAILABLE=False"
        )

        print(
            "ENVIRONMENT_CREATED=False"
        )

        print(
            "PACKAGES_INSTALLED=False"
        )

        print(
            "TRAINING_STARTED=False"
        )

        print(
            "TEST_LOADED=False"
        )

        print(
            "OUTPUT="
            f"{OUTPUT_FILE}"
        )

        print(
            "STATUS="
            "PYTHON_3_12_NOT_AVAILABLE"
        )

        print("T2_MOD_017_COMPLETE")

        return

    # --------------------------------------------------------
    # Create dedicated environment.
    # --------------------------------------------------------

    environment_created = False

    if ENV_DIR.exists():

        env_python = (
            ENV_DIR
            / "bin"
            / "python"
        )

        if env_python.exists():

            environment_created = True

        else:

            print(
                "ERROR_EXISTING_ENVIRONMENT="
                f"{ENV_DIR}"
            )

            report = {
                "operation": "T2-MOD-017",
                "status": (
                    "EXISTING_ENVIRONMENT_INVALID"
                ),
                "environment_path": str(
                    ENV_DIR
                ),
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

            return

    else:

        result = subprocess.run(
            [
                str(selected_python),
                "-m",
                "venv",
                str(ENV_DIR),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:

            print(
                "VENV_CREATION_FAILED"
            )

            print(
                result.stderr.strip()
            )

            report = {
                "operation": "T2-MOD-017",
                "status": (
                    "ENVIRONMENT_CREATION_FAILED"
                ),
                "selected_python": str(
                    selected_python
                ),
                "stderr": result.stderr,
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

            return

        environment_created = True

    # --------------------------------------------------------
    # Verify created environment.
    # --------------------------------------------------------

    env_python = (
        ENV_DIR
        / "bin"
        / "python"
    )

    env_version = None

    if env_python.exists():
        env_version = get_python_version(
            env_python
        )

    report = {
        "operation": "T2-MOD-017",
        "operation_name": (
            "Transformer Environment Configuration"
        ),

        "current_environment": {
            "python": str(current_python),
            "version": current_version,
        },

        "selected_python": {
            "executable": str(
                selected_python
            ),
            "version": get_python_version(
                selected_python
            ),
        },

        "transformer_environment": {
            "path": str(ENV_DIR),
            "python": str(env_python),
            "version": env_version,
            "created": environment_created,
        },

        "packages": {
            "torch_installed": False,
            "transformers_installed": False,
            "tokenizers_installed": False,
            "datasets_installed": False,
        },

        "training": {
            "started": False,
        },

        "test_access": {
            "loaded": False,
        },

        "dataset_modification": False,

        "status": (
            "ENVIRONMENT_CREATED"
            if environment_created
            else "ENVIRONMENT_NOT_CREATED"
        ),
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

    print(
        "CURRENT_PYTHON="
        f"{current_version}"
    )

    print(
        "SELECTED_PYTHON="
        f"{get_python_version(selected_python)}"
    )

    print(
        "TRANSFORMER_ENV="
        f"{ENV_DIR}"
    )

    print(
        "TRANSFORMER_ENV_PYTHON="
        f"{env_version}"
    )

    print(
        "ENVIRONMENT_CREATED="
        f"{environment_created}"
    )

    print(
        "PACKAGES_INSTALLED=False"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "TEST_LOADED=False"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "STATUS="
        "ENVIRONMENT_CREATED"
    )

    print("T2_MOD_017_COMPLETE")


if __name__ == "__main__":
    main()