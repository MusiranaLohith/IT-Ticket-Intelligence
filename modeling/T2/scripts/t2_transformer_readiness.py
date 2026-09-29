from pathlib import Path
import csv
import json
import platform
import sys


# ============================================================
# T2-MOD-014
# Transformer Environment & Data Readiness Check
#
# Read-only readiness operation.
# No training.
# No model fine-tuning.
# No test-set loading.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

FEATURE_FILE = (
    T2_ROOT / "derived" / "t2_features.csv"
)

SPLIT_DIR = T2_ROOT / "splits"

TRAIN_FILE = SPLIT_DIR / "t2_train.csv"
VALIDATION_FILE = SPLIT_DIR / "t2_validation.csv"

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR / "t2_transformer_readiness.json"
)


EXPECTED_TRAIN_ROWS = 20648
EXPECTED_VALIDATION_ROWS = 4425
EXPECTED_TOTAL_ROWS = 29498

MODEL_IDENTIFIER = "distilbert-base-uncased"

EXPECTED_CLASSES = {
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
}


def count_csv_rows(path):
    """
    Count data rows without loading the complete file
    into memory.
    """

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.reader(f)

        header = next(reader)

        rows = sum(
            1
            for _ in reader
        )

    return header, rows


def inspect_split(path):
    """
    Read only the columns needed for readiness verification.
    """

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        fields = reader.fieldnames or []

        row_count = 0
        ids = set()
        priorities = set()
        missing_ids = 0
        missing_targets = 0

        for row in reader:
            row_count += 1

            ticket_id = (
                row.get("id", "").strip()
            )

            target = (
                row.get("target_priority", "").strip()
            )

            if not ticket_id:
                missing_ids += 1
            else:
                ids.add(ticket_id)

            if not target:
                missing_targets += 1
            else:
                priorities.add(target)

    return {
        "fields": fields,
        "rows": row_count,
        "unique_ids": len(ids),
        "missing_ids": missing_ids,
        "missing_targets": missing_targets,
        "classes": sorted(priorities),
        "ids": ids,
    }


def get_environment():
    result = {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "pytorch_installed": False,
        "pytorch_version": None,
        "cuda_available": False,
        "cuda_version": None,
        "gpu_count": 0,
        "gpu_name": None,
        "transformers_installed": False,
        "transformers_version": None,
        "tokenizer_loadable": False,
        "tokenizer_vocab_size": None,
        "tokenizer_error": None,
    }

    # --------------------------------------------------------
    # PyTorch
    # --------------------------------------------------------

    try:
        import torch

        result["pytorch_installed"] = True
        result["pytorch_version"] = torch.__version__

        result["cuda_available"] = bool(
            torch.cuda.is_available()
        )

        result["cuda_version"] = torch.version.cuda

        if result["cuda_available"]:
            result["gpu_count"] = (
                torch.cuda.device_count()
            )

            if result["gpu_count"] > 0:
                result["gpu_name"] = (
                    torch.cuda.get_device_name(0)
                )

    except Exception as exc:
        result["pytorch_error"] = str(exc)

    # --------------------------------------------------------
    # Hugging Face Transformers
    # --------------------------------------------------------

    try:
        import transformers

        result["transformers_installed"] = True
        result["transformers_version"] = (
            transformers.__version__
        )

        try:
            from transformers import (
                AutoTokenizer
            )

            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_IDENTIFIER
            )

            result["tokenizer_loadable"] = True
            result["tokenizer_vocab_size"] = (
                tokenizer.vocab_size
            )

        except Exception as exc:
            result["tokenizer_error"] = str(exc)

    except Exception as exc:
        result["transformers_error"] = str(exc)

    return result


def main():
    print("T2_MOD_014_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    environment = get_environment()

    # --------------------------------------------------------
    # File existence
    # --------------------------------------------------------

    required_files = {
        "feature_materialization": FEATURE_FILE,
        "train_split": TRAIN_FILE,
        "validation_split": VALIDATION_FILE,
    }

    file_status = {}

    for name, path in required_files.items():
        file_status[name] = {
            "path": str(path),
            "exists": path.exists(),
        }

    # --------------------------------------------------------
    # Materialized feature file
    # --------------------------------------------------------

    feature_info = {
        "exists": FEATURE_FILE.exists(),
        "rows": None,
        "fields": None,
    }

    if FEATURE_FILE.exists():
        header, rows = count_csv_rows(
            FEATURE_FILE
        )

        feature_info["fields"] = header
        feature_info["rows"] = rows

    # --------------------------------------------------------
    # Frozen train/validation partitions
    # --------------------------------------------------------

    train_info = None
    validation_info = None

    if TRAIN_FILE.exists():
        train_info = inspect_split(
            TRAIN_FILE
        )

    if VALIDATION_FILE.exists():
        validation_info = inspect_split(
            VALIDATION_FILE
        )

    # --------------------------------------------------------
    # Split integrity
    # --------------------------------------------------------

    split_integrity = {
        "train_rows_correct": False,
        "validation_rows_correct": False,
        "combined_rows_correct": False,
        "train_validation_id_overlap": None,
        "all_expected_classes_present": False,
    }

    if train_info and validation_info:
        split_integrity[
            "train_rows_correct"
        ] = (
            train_info["rows"]
            == EXPECTED_TRAIN_ROWS
        )

        split_integrity[
            "validation_rows_correct"
        ] = (
            validation_info["rows"]
            == EXPECTED_VALIDATION_ROWS
        )

        split_integrity[
            "combined_rows_correct"
        ] = (
            train_info["rows"]
            + validation_info["rows"]
            == EXPECTED_TOTAL_ROWS
        )

        overlap = (
            train_info["ids"]
            & validation_info["ids"]
        )

        split_integrity[
            "train_validation_id_overlap"
        ] = len(overlap)

        observed_classes = (
            set(train_info["classes"])
            | set(validation_info["classes"])
        )

        split_integrity[
            "all_expected_classes_present"
        ] = (
            observed_classes
            == EXPECTED_CLASSES
        )

    # --------------------------------------------------------
    # Overall readiness
    # --------------------------------------------------------

    readiness_checks = {
        "pytorch_available": (
            environment["pytorch_installed"]
        ),
        "transformers_available": (
            environment["transformers_installed"]
        ),
        "distilbert_tokenizer_loadable": (
            environment["tokenizer_loadable"]
        ),
        "feature_file_available": (
            feature_info["exists"]
        ),
        "feature_row_count_correct": (
            feature_info["rows"]
            == EXPECTED_TOTAL_ROWS
        ),
        "train_split_available": (
            train_info is not None
        ),
        "validation_split_available": (
            validation_info is not None
        ),
        "train_size_correct": (
            split_integrity[
                "train_rows_correct"
            ]
        ),
        "validation_size_correct": (
            split_integrity[
                "validation_rows_correct"
            ]
        ),
        "train_validation_combined_size_correct": (
            split_integrity[
                "combined_rows_correct"
            ]
        ),
        "train_validation_id_overlap_zero": (
            split_integrity[
                "train_validation_id_overlap"
            ] == 0
            if split_integrity[
                "train_validation_id_overlap"
            ] is not None
            else False
        ),
        "all_expected_classes_present": (
            split_integrity[
                "all_expected_classes_present"
            ]
        ),
    }

    overall_ready = all(
        readiness_checks.values()
    )

    report = {
        "operation": "T2-MOD-014",
        "operation_name": (
            "Transformer Environment "
            "and Data Readiness Check"
        ),
        "task": "T2",
        "dataset": "Mozilla CORE",
        "model_candidate": MODEL_IDENTIFIER,

        "environment": environment,

        "required_files": file_status,

        "feature_materialization": feature_info,

        "train_split": (
            {
                key: value
                for key, value in train_info.items()
                if key != "ids"
            }
            if train_info
            else None
        ),

        "validation_split": (
            {
                key: value
                for key, value in validation_info.items()
                if key != "ids"
            }
            if validation_info
            else None
        ),

        "split_integrity": split_integrity,

        "readiness_checks": readiness_checks,

        "test_access": {
            "test_file_loaded": False,
            "test_file_path_checked": False,
            "reason": (
                "The test partition remains locked "
                "during advanced-model preparation."
            ),
        },

        "training": {
            "started": False,
            "fine_tuning_started": False,
        },

        "overall_ready": overall_ready,

        "status": (
            "READY_FOR_CONTROLLED_TRANSFORMER_TRAINING"
            if overall_ready
            else "NOT_READY"
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

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    print(
        "PYTHON_VERSION="
        f"{environment['python_version']}"
    )

    print(
        "PYTORCH_INSTALLED="
        f"{environment['pytorch_installed']}"
    )

    print(
        "PYTORCH_VERSION="
        f"{environment['pytorch_version']}"
    )

    print(
        "CUDA_AVAILABLE="
        f"{environment['cuda_available']}"
    )

    print(
        "GPU_COUNT="
        f"{environment['gpu_count']}"
    )

    print(
        "GPU_NAME="
        f"{environment['gpu_name']}"
    )

    print(
        "TRANSFORMERS_INSTALLED="
        f"{environment['transformers_installed']}"
    )

    print(
        "TRANSFORMERS_VERSION="
        f"{environment['transformers_version']}"
    )

    print(
        "TOKENIZER_LOADABLE="
        f"{environment['tokenizer_loadable']}"
    )

    print(
        "FEATURE_ROWS="
        f"{feature_info['rows']}"
    )

    print(
        "TRAIN_ROWS="
        f"{train_info['rows'] if train_info else None}"
    )

    print(
        "VALIDATION_ROWS="
        f"{validation_info['rows'] if validation_info else None}"
    )

    print(
        "TRAIN_VALIDATION_ID_OVERLAP="
        f"{split_integrity['train_validation_id_overlap']}"
    )

    print(
        "ALL_EXPECTED_CLASSES_PRESENT="
        f"{split_integrity['all_expected_classes_present']}"
    )

    print(
        "TEST_LOADED=False"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "OVERALL_READY="
        f"{overall_ready}"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "STATUS="
        + (
            "READY_FOR_CONTROLLED_TRANSFORMER_TRAINING"
            if overall_ready
            else "NOT_READY"
        )
    )

    print("T2_MOD_014_COMPLETE")


if __name__ == "__main__":
    main()