from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OP026_PATH = (
    PROJECT_ROOT
    / "modeling/T8/mod036/op026/"
      "t8_mod036_op026_decision_engine_validation.json"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "modeling/FMP/metrics/"
      "f_op009_op026_evidence_structure_inspection.json"
)

TARGET_NUMBERS = {
    10246,
    109649,
    9727,
    519,
    0,
    119895,
}

TARGET_TERMS = {
    "supported",
    "conflicting",
    "insufficient_evidence",
    "unavailable",
    "component",
    "evidence",
}


def inspect_value(
    value,
    path="root",
    results=None,
):
    if results is None:
        results = []

    if isinstance(value, dict):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )

            results.append(
                {
                    "path": child_path,
                    "key": str(key),
                    "value": child,
                    "type": type(child).__name__,
                }
            )

            inspect_value(
                child,
                child_path,
                results,
            )

    elif isinstance(value, list):

        for index, child in enumerate(value):

            child_path = (
                f"{path}[{index}]"
            )

            # Avoid dumping large row-level
            # arrays. Only inspect structure.
            if index < 20:

                results.append(
                    {
                        "path": child_path,
                        "key": str(index),
                        "value": child,
                        "type": type(child).__name__,
                    }
                )

                inspect_value(
                    child,
                    child_path,
                    results,
                )

            elif index == 20:

                results.append(
                    {
                        "path": (
                            f"{path}[20+]"
                        ),
                        "key": "20+",
                        "value": (
                            "<remaining list "
                            "elements omitted>"
                        ),
                        "type": "omitted",
                    }
                )

                break

    return results


def value_matches(
    value,
) -> bool:

    if isinstance(value, bool):
        return False

    if isinstance(value, int):
        return value in TARGET_NUMBERS

    if isinstance(value, str):

        lower = value.strip().lower()

        if lower in TARGET_TERMS:
            return True

        if lower.replace(",", "").isdigit():

            try:
                return (
                    int(
                        lower.replace(",", "")
                    )
                    in TARGET_NUMBERS
                )
            except ValueError:
                return False

    return False


def main():

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not OP026_PATH.exists():

        print("=" * 72)
        print(
            "F-OP-009 — OP-026 EVIDENCE "
            "STRUCTURE INSPECTION"
        )
        print("=" * 72)
        print(
            "RESULT: BLOCKED — OP-026 JSON "
            "not found"
        )
        print("=" * 72)

        return

    with OP026_PATH.open(
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    all_records = inspect_value(data)

    matches = []

    for record in all_records:

        if value_matches(
            record["value"]
        ):

            matches.append(
                {
                    "path": record["path"],
                    "key": record["key"],
                    "value": record["value"],
                    "type": record["type"],
                }
            )

    # Also capture records where the path/key
    # itself contains relevant evidence terms.
    semantic_matches = []

    for record in all_records:

        path_text = (
            record["path"]
            .lower()
        )

        key_text = (
            record["key"]
            .lower()
        )

        if any(
            term in path_text
            or term in key_text
            for term in TARGET_TERMS
        ):

            semantic_matches.append(
                {
                    "path": record["path"],
                    "key": record["key"],
                    "value": record["value"],
                    "type": record["type"],
                }
            )

    result = {
        "operation": "F-OP-009",
        "title": (
            "OP-026 Evidence-State "
            "Structure Inspection"
        ),
        "status": (
            "PASS"
            if matches or semantic_matches
            else "REQUIRES_REVIEW"
        ),
        "read_only": True,
        "models_executed": False,
        "model_modified": False,
        "retraining_performed": False,
        "threshold_selection_performed": False,
        "locked_test_reused_for_policy_selection": (
            False
        ),
        "op026_path": str(
            OP026_PATH
        ),
        "top_level_keys": (
            list(data.keys())
            if isinstance(data, dict)
            else []
        ),
        "target_number_matches": matches,
        "semantic_matches": semantic_matches,
        "expected_evidence_distribution": {
            "SUPPORTED": 10246,
            "CONFLICTING": 0,
            "INSUFFICIENT_EVIDENCE": 109649,
            "UNAVAILABLE": 0,
            "TOTAL": 119895,
        },
        "expected_component_distribution": {
            "1": 109649,
            "2": 9727,
            "3": 519,
            "4": 0,
            "TOTAL": 119895,
        },
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 72)
    print(
        "F-OP-009 — OP-026 EVIDENCE "
        "STRUCTURE INSPECTION"
    )
    print("=" * 72)

    print(
        f"OP-026 readable       : True"
    )

    print(
        "Top-level keys        :"
    )

    for key in result[
        "top_level_keys"
    ]:
        print(
            f"  - {key}"
        )

    print()
    print(
        "TARGET NUMBER / VALUE MATCHES"
    )
    print("-" * 72)

    if matches:

        for item in matches:

            print(
                f"{item['path']}"
                f" = {repr(item['value'])}"
            )

    else:

        print(
            "None"
        )

    print()
    print(
        "SEMANTIC STRUCTURE MATCHES"
    )
    print("-" * 72)

    if semantic_matches:

        # Keep terminal output compact.
        for item in semantic_matches[:80]:

            value = repr(
                item["value"]
            )

            if len(value) > 180:
                value = (
                    value[:177]
                    + "..."
                )

            print(
                f"{item['path']} = {value}"
            )

        if len(
            semantic_matches
        ) > 80:

            print(
                f"... "
                f"{len(semantic_matches) - 80} "
                "additional matches written "
                "to JSON"
            )

    else:

        print(
            "None"
        )

    print()
    print(
        "Expected evidence distribution:"
    )

    print(
        "  SUPPORTED             : 10246"
    )

    print(
        "  CONFLICTING           : 0"
    )

    print(
        "  INSUFFICIENT_EVIDENCE : 109649"
    )

    print(
        "  UNAVAILABLE           : 0"
    )

    print(
        "  TOTAL                 : 119895"
    )

    print()
    print(
        "Expected component distribution:"
    )

    print(
        "  1 component           : 109649"
    )

    print(
        "  2 components          : 9727"
    )

    print(
        "  3 components          : 519"
    )

    print(
        "  4 components          : 0"
    )

    print(
        "  TOTAL                 : 119895"
    )

    print()
    print(
        f"Output                 : "
        f"{OUTPUT_PATH}"
    )

    print("=" * 72)
    print(
        f"RESULT: {result['status']} — "
        "F-OP-009 complete"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()