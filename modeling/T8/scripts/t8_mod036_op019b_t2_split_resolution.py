from pathlib import Path
import csv
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = ROOT / "modeling/T2"
OUT_DIR = ROOT / "modeling/T8/mod036/op019b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op019b_t2_split_resolution.json"

csv.field_size_limit(10_000_000)


SPLITS = {
    "train": T2_ROOT / "splits/train.csv",
    "validation": T2_ROOT / "splits/validation.csv",
    "test": T2_ROOT / "splits/test.csv",
}

PROVENANCE_FILES = [
    T2_ROOT / "splits/t2_split_report.json",
    T2_ROOT / "analysis/t2_final_closure.json",
    T2_ROOT / "analysis/t2_final_model_selection.json",
    T2_ROOT / "contracts/t2_model_contract.json",
    T2_ROOT / "contracts/t2_contract.json",
]


def load_rows(path):
    with path.open(
        "r",
        encoding="utf-8",
        errors="replace",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def get_id(row):
    for key in ("id", "ID", "ticket_id", "bug_id"):
        value = row.get(key, "")
        if str(value).strip():
            return str(value).strip()
    return ""


def inspect_provenance(path):
    if not path.exists():
        return {
            "exists": False,
            "path": str(path.relative_to(ROOT)),
        }

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, dict):
            keys = list(data.keys())
        else:
            keys = []

        return {
            "exists": True,
            "path": str(path.relative_to(ROOT)),
            "type": type(data).__name__,
            "top_level_keys": keys,
            "text_excerpt": json.dumps(
                data,
                ensure_ascii=False,
            )[:12000],
        }

    except Exception as exc:
        return {
            "exists": True,
            "path": str(path.relative_to(ROOT)),
            "read_error": str(exc),
        }


def target_distribution(rows):
    target_column = "target_priority"

    counts = {}

    for row in rows:
        value = str(
            row.get(target_column, "")
        ).strip()

        counts[value] = counts.get(value, 0) + 1

    return counts


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-019B")
    print("T2 Native Development Split Resolution")
    print("=" * 80)

    loaded = {}
    ids = {}
    distributions = {}
    columns = {}

    # -------------------------------------------------------------
    # Load split artifacts
    # -------------------------------------------------------------

    for split_name, path in SPLITS.items():

        if not path.exists():
            raise FileNotFoundError(path)

        rows = load_rows(path)

        loaded[split_name] = rows

        ids[split_name] = {
            get_id(row)
            for row in rows
            if get_id(row)
        }

        columns[split_name] = (
            list(rows[0].keys())
            if rows
            else []
        )

        distributions[split_name] = target_distribution(
            rows
        )

        print(
            f"\n{split_name.upper()}"
        )
        print("-" * 80)
        print(f"  rows: {len(rows)}")
        print(f"  unique IDs: {len(ids[split_name])}")
        print(
            f"  target distribution: "
            f"{distributions[split_name]}"
        )

    # -------------------------------------------------------------
    # Validate IDs
    # -------------------------------------------------------------

    duplicate_ids = {}

    for split_name, rows in loaded.items():

        raw_ids = [
            get_id(row)
            for row in rows
        ]

        duplicate_count = (
            len(raw_ids)
            - len(set(raw_ids))
        )

        duplicate_ids[split_name] = duplicate_count

    print("\nDuplicate-ID audit")
    print("-" * 80)

    for split_name, count in duplicate_ids.items():
        print(
            f"  {split_name}: {count}"
        )

    # -------------------------------------------------------------
    # Pairwise overlap
    # -------------------------------------------------------------

    overlaps = {}

    split_names = list(SPLITS.keys())

    print("\nPairwise split overlap")
    print("-" * 80)

    for i, left in enumerate(split_names):
        for right in split_names[i + 1:]:

            overlap = (
                ids[left]
                & ids[right]
            )

            key = f"{left}_x_{right}"

            overlaps[key] = len(overlap)

            print(
                f"  {left} ∩ {right}: "
                f"{len(overlap)}"
            )

    # -------------------------------------------------------------
    # Population totals
    # -------------------------------------------------------------

    union_ids = set().union(
        *ids.values()
    )

    sum_rows = sum(
        len(rows)
        for rows in loaded.values()
    )

    print("\nPopulation accounting")
    print("-" * 80)
    print(f"  sum of split rows: {sum_rows}")
    print(f"  union of unique IDs: {len(union_ids)}")

    # -------------------------------------------------------------
    # Required columns
    # -------------------------------------------------------------

    required_columns = {
        "id",
        "summary",
        "description",
        "target_priority",
    }

    column_audit = {}

    print("\nColumn audit")
    print("-" * 80)

    for split_name, split_columns in columns.items():

        lowered = {
            str(column).lower()
            for column in split_columns
        }

        missing = sorted(
            required_columns
            - lowered
        )

        column_audit[split_name] = {
            "columns": split_columns,
            "missing_required_columns": missing,
        }

        print(
            f"  {split_name}: "
            f"missing={missing}"
        )

    # -------------------------------------------------------------
    # Test isolation
    # -------------------------------------------------------------

    test_overlap_with_development = (
        ids["test"]
        & (
            ids["train"]
            | ids["validation"]
        )
    )

    print("\nLocked-test isolation")
    print("-" * 80)
    print(
        "  test ∩ (train ∪ validation): "
        f"{len(test_overlap_with_development)}"
    )

    # -------------------------------------------------------------
    # Development population
    # -------------------------------------------------------------

    development_ids = (
        ids["train"]
        | ids["validation"]
    )

    development_rows = (
        len(loaded["train"])
        + len(loaded["validation"])
    )

    print("\nT8 candidate development population")
    print("-" * 80)
    print(
        f"  train rows: {len(loaded['train'])}"
    )
    print(
        f"  validation rows: "
        f"{len(loaded['validation'])}"
    )
    print(
        f"  development rows: "
        f"{development_rows}"
    )
    print(
        f"  unique development IDs: "
        f"{len(development_ids)}"
    )

    # -------------------------------------------------------------
    # Provenance
    # -------------------------------------------------------------

    print("\nProvenance artifacts")
    print("-" * 80)

    provenance = {}

    for path in PROVENANCE_FILES:

        item = inspect_provenance(path)

        provenance[str(path.relative_to(ROOT))] = item

        print(
            f"  {path.relative_to(ROOT)}: "
            f"{'FOUND' if item.get('exists') else 'MISSING'}"
        )

    # -------------------------------------------------------------
    # Resolution
    # -------------------------------------------------------------

    resolution_checks = {
        "train_exists": SPLITS["train"].exists(),
        "validation_exists": SPLITS["validation"].exists(),
        "test_exists": SPLITS["test"].exists(),

        "train_duplicate_ids": (
            duplicate_ids["train"] == 0
        ),
        "validation_duplicate_ids": (
            duplicate_ids["validation"] == 0
        ),
        "test_duplicate_ids": (
            duplicate_ids["test"] == 0
        ),

        "train_validation_disjoint": (
            overlaps["train_x_validation"] == 0
        ),

        "train_test_disjoint": (
            overlaps["train_x_test"] == 0
        ),

        "validation_test_disjoint": (
            overlaps["validation_x_test"] == 0
        ),

        "required_columns_present": all(
            not item["missing_required_columns"]
            for item in column_audit.values()
        ),

        "locked_test_isolated": (
            len(test_overlap_with_development) == 0
        ),

        "native_priority_target_present": all(
            "target_priority" in columns[name]
            for name in split_names
        ),
    }

    resolution_pass = all(
        resolution_checks.values()
    )

    print("\nResolution checks")
    print("-" * 80)

    for key, value in resolution_checks.items():
        print(f"  {key}: {value}")

    print("\nResolution")
    print("-" * 80)

    if resolution_pass:
        print(
            "  T2 native development population "
            "resolved: TRAIN + VALIDATION"
        )
        print(
            "  T2 TEST remains locked and excluded "
            "from T8 development."
        )
        status = "RESOLVED"
    else:
        print(
            "  T2 development population resolution "
            "requires further investigation."
        )
        status = "UNRESOLVED"

    # -------------------------------------------------------------
    # Artifact
    # -------------------------------------------------------------

    result = {
        "operation": "MOD-036 OP-019B",
        "status": "PASS" if resolution_pass else "INVESTIGATION_REQUIRED",

        "resolution": {
            "status": status,
            "development_population": [
                "modeling/T2/splits/train.csv",
                "modeling/T2/splits/validation.csv",
            ],
            "locked_test": (
                "modeling/T2/splits/test.csv"
            ),
        },

        "split_sizes": {
            name: len(rows)
            for name, rows in loaded.items()
        },

        "unique_ids": {
            name: len(ids[name])
            for name in split_names
        },

        "target_distributions": distributions,

        "duplicate_ids": duplicate_ids,

        "pairwise_overlaps": overlaps,

        "population_accounting": {
            "sum_split_rows": sum_rows,
            "unique_union_ids": len(union_ids),
            "development_rows": development_rows,
            "development_unique_ids": len(
                development_ids
            ),
        },

        "column_audit": column_audit,

        "test_isolation": {
            "overlap_rows": len(
                test_overlap_with_development
            ),
            "isolated": (
                len(test_overlap_with_development)
                == 0
            ),
        },

        "resolution_checks": resolution_checks,

        "provenance": provenance,

        "controls": {
            "training_performed": False,
            "prediction_generation_performed": False,
            "model_selected": False,
            "dataset_modified": False,
            "locked_test_used_for_selection": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArtifact")
    print("-" * 80)
    print(f"  {OUTPUT}")

    print("\nStatus: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()