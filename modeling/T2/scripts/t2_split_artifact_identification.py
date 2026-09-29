from pathlib import Path
import csv
import json


# ============================================================
# T2-MOD-016
# Frozen Split Artifact Identification
#
# Read-only.
# Does not modify datasets.
# Does not load the test data into memory as a dataset.
# Does not train anything.
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T2_ROOT = PROJECT_ROOT / "modeling" / "T2"

OUTPUT_DIR = T2_ROOT / "analysis"

OUTPUT_FILE = (
    OUTPUT_DIR / "t2_split_artifact_identification.json"
)

EXPECTED = {
    "train": 20648,
    "validation": 4425,
    "test": 4425,
}


def inspect_csv(path):
    """
    Inspect a CSV using streaming iteration.
    """

    result = {
        "path": str(path),
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "header": [],
        "row_count": 0,
        "has_id": False,
        "has_target_priority": False,
        "has_summary": False,
        "has_description": False,
        "first_id": None,
        "last_id": None,
    }

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        result["header"] = (
            reader.fieldnames or []
        )

        fields_lower = {
            field.lower()
            for field in result["header"]
        }

        result["has_id"] = (
            "id" in fields_lower
        )

        result["has_target_priority"] = (
            "target_priority" in fields_lower
        )

        result["has_summary"] = (
            "summary" in fields_lower
        )

        result["has_description"] = (
            "description" in fields_lower
        )

        for row in reader:
            result["row_count"] += 1

            ticket_id = (
                row.get("id", "").strip()
            )

            if result["first_id"] is None:
                result["first_id"] = ticket_id

            result["last_id"] = ticket_id

    return result


def main():
    print("T2_MOD_016_START")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates = []

    # --------------------------------------------------------
    # Locate split-related files.
    # --------------------------------------------------------

    for path in sorted(
        T2_ROOT.rglob("*")
    ):
        if not path.is_file():
            continue

        name = path.name.lower()

        if not name.endswith(".csv"):
            continue

        if not any(
            token in name
            for token in (
                "train",
                "validation",
                "val",
                "test",
                "split",
            )
        ):
            continue

        candidates.append(
            inspect_csv(path)
        )

    # --------------------------------------------------------
    # Determine size matches.
    # --------------------------------------------------------

    for item in candidates:

        item["matches_train_size"] = (
            item["row_count"]
            == EXPECTED["train"]
        )

        item["matches_validation_size"] = (
            item["row_count"]
            == EXPECTED["validation"]
        )

        item["matches_test_size"] = (
            item["row_count"]
            == EXPECTED["test"]
        )

        item["looks_like_t2_split"] = all(
            [
                item["has_id"],
                item["has_target_priority"],
                item["has_summary"],
                item["has_description"],
            ]
        )

    # --------------------------------------------------------
    # Group by expected partition size.
    # --------------------------------------------------------

    train_candidates = [
        item
        for item in candidates
        if item["matches_train_size"]
        and item["looks_like_t2_split"]
    ]

    validation_candidates = [
        item
        for item in candidates
        if item["matches_validation_size"]
        and item["looks_like_t2_split"]
    ]

    test_candidates = [
        item
        for item in candidates
        if item["matches_test_size"]
        and item["looks_like_t2_split"]
    ]

    report = {
        "operation": "T2-MOD-016",
        "operation_name": (
            "Frozen Split Artifact Identification"
        ),
        "task": "T2",
        "dataset": "Mozilla CORE",

        "expected_partition_sizes": EXPECTED,

        "candidate_count": len(candidates),

        "candidates": candidates,

        "size_matched_candidates": {
            "train": train_candidates,
            "validation": validation_candidates,
            "test": test_candidates,
        },

        "identification": {
            "train_unique_candidate": (
                len(train_candidates) == 1
            ),
            "validation_unique_candidate": (
                len(validation_candidates) == 1
            ),
            "test_unique_candidate": (
                len(test_candidates) == 1
            ),
        },

        "test_loaded": False,
        "training_started": False,

        "status": (
            "AUTHORITATIVE_SPLITS_IDENTIFIED"
            if (
                len(train_candidates) == 1
                and len(validation_candidates) == 1
                and len(test_candidates) == 1
            )
            else "AMBIGUITY_REMAINS",
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
    # Console output.
    # --------------------------------------------------------

    print(
        "CANDIDATE_COUNT="
        f"{len(candidates)}"
    )

    print(
        "TRAIN_SIZE_MATCHES="
        f"{len(train_candidates)}"
    )

    print(
        "VALIDATION_SIZE_MATCHES="
        f"{len(validation_candidates)}"
    )

    print(
        "TEST_SIZE_MATCHES="
        f"{len(test_candidates)}"
    )

    print()

    for index, item in enumerate(
        candidates,
        start=1,
    ):
        print(
            f"CANDIDATE_{index}"
        )
        print(
            f"PATH={item['path']}"
        )
        print(
            f"ROWS={item['row_count']}"
        )
        print(
            f"SIZE_BYTES={item['size_bytes']}"
        )
        print(
            "HAS_T2_FIELDS="
            f"{item['looks_like_t2_split']}"
        )
        print(
            "MATCH_TRAIN="
            f"{item['matches_train_size']}"
        )
        print(
            "MATCH_VALIDATION="
            f"{item['matches_validation_size']}"
        )
        print(
            "MATCH_TEST="
            f"{item['matches_test_size']}"
        )
        print()

    print(
        "TEST_LOADED=False"
    )

    print(
        "TRAINING_STARTED=False"
    )

    print(
        "OUTPUT="
        f"{OUTPUT_FILE}"
    )

    print(
        "STATUS="
        + (
            "AUTHORITATIVE_SPLITS_IDENTIFIED"
            if (
                len(train_candidates) == 1
                and len(validation_candidates) == 1
                and len(test_candidates) == 1
            )
            else "AMBIGUITY_REMAINS"
        )
    )

    print("T2_MOD_016_COMPLETE")


if __name__ == "__main__":
    main()