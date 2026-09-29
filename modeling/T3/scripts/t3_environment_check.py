from pathlib import Path
import importlib.util
import os
import platform
import shutil
import sys


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"


def package_status(package_name):
    return importlib.util.find_spec(package_name) is not None


def main():
    print("T3_MOD_020_START")

    print(f"PYTHON_VERSION={platform.python_version()}")
    print(f"PYTHON_EXECUTABLE={sys.executable}")
    print(f"PLATFORM={platform.platform()}")
    print(f"CPU_COUNT={os.cpu_count()}")

    # RAM
    meminfo = Path("/proc/meminfo")

    if meminfo.exists():
        memory = {}

        for line in meminfo.read_text().splitlines():
            parts = line.split()

            if len(parts) >= 2:
                key = parts[0].rstrip(":")
                value_kb = int(parts[1])
                memory[key] = value_kb

        total_gb = memory.get("MemTotal", 0) / (1024 ** 2)
        available_gb = memory.get("MemAvailable", 0) / (1024 ** 2)

        print(f"RAM_TOTAL_GB={total_gb:.2f}")
        print(f"RAM_AVAILABLE_GB={available_gb:.2f}")
    else:
        print("RAM_CHECK=UNAVAILABLE")

    # Disk
    disk = shutil.disk_usage(PROJECT_ROOT)

    free_gb = disk.free / (1024 ** 3)
    total_disk_gb = disk.total / (1024 ** 3)

    print(f"PROJECT_DISK_TOTAL_GB={total_disk_gb:.2f}")
    print(f"PROJECT_DISK_FREE_GB={free_gb:.2f}")

    # Required advanced stack
    packages = {
        "torch": "PyTorch",
        "transformers": "Transformers",
        "tokenizers": "Tokenizers",
        "datasets": "Datasets",
    }

    print("PACKAGE_STATUS")

    installed = {}

    for package, display_name in packages.items():
        present = package_status(package)
        installed[package] = present
        print(f"{display_name}={present}")

    # CUDA check without requiring PyTorch
    nvidia_smi = shutil.which("nvidia-smi")

    if nvidia_smi:
        print("NVIDIA_SMI_AVAILABLE=True")
        print(f"NVIDIA_SMI_PATH={nvidia_smi}")
    else:
        print("NVIDIA_SMI_AVAILABLE=False")

    # Conservative feasibility assessment.
    required_packages_present = all(installed.values())

    if required_packages_present:
        feasibility = "READY_FOR_RUNTIME_VERIFICATION"
    else:
        feasibility = "INSTALLATION_REQUIRED"

    print(f"REQUIRED_PACKAGES_PRESENT={required_packages_present}")
    print(f"ADVANCED_ENVIRONMENT_STATUS={feasibility}")

    print("INSTALLATION_STARTED=False")
    print("TRAINING_STARTED=False")
    print("TEST_USED=False")
    print("RAW_MOZILLA_ACCESSED=False")
    print("DATASET_MODIFIED=False")
    print("STATUS=ENVIRONMENT_FEASIBILITY_CHECK_COMPLETE")
    print("T3_MOD_020_COMPLETE")


if __name__ == "__main__":
    main()