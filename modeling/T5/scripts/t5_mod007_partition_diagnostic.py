from pathlib import Path
import csv
import hashlib
import sys

csv.field_size_limit(sys.maxsize)

SOURCE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T5/splits/t5_model_train.csv"
)

SEED = 42


def normalized_content_key(row):
    summary = (row["Summary"] or "").strip().lower()
    description = (row["Description"] or "").strip().lower()
    return summary + "\n" + description


def deterministic_group_value(group_key):
    payload = f"{SEED}|{group_key}".encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return int(digest[:16], 16) / float(16**16)


def main():
    groups = set()

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            groups.add(
                normalized_content_key(row)
            )

    values = [
        deterministic_group_value(group)
        for group in groups
    ]

    print("=" * 80)
    print("T5-MOD-007 PARTITION DIAGNOSTIC")
    print("=" * 80)

    print(f"Groups: {len(groups)}")
    print(f"Minimum hash value: {min(values):.12f}")
    print(f"Maximum hash value: {max(values):.12f}")

    for threshold in [
        0.01,
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.50,
    ]:
        count = sum(
            value < threshold
            for value in values
        )

        print(
            f"< {threshold:.2f}: "
            f"{count} groups "
            f"({count / len(values):.4%})"
        )


if __name__ == "__main__":
    main()