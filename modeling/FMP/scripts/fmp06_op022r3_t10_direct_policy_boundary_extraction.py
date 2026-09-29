from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T10_EVIDENCE = (
    ROOT / "modeling/FMP/metrics/"
    "fmp05_op008_empirical_policy_boundary_audit.json"
)

OUT = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op022r3_t10_direct_policy_boundary_extraction.json"
)


KEYWORDS = (
    "threshold",
    "automation",
    "human_review",
    "human-review",
    "synthetic",
    "universal",
    "risk",
    "confidence",
)


def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{path}.{key}"

            key_text = str(key).lower()

            if any(
                keyword in key_text
                for keyword in KEYWORDS
            ):
                print(f"  {current} = {value}")

            yield from walk(value, current)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk(
                value,
                f"{path}[{index}]"
            )


def main():
    print("=" * 72)
    print(
        "FMP-06 OP-022R3 — T10 DIRECT "
        "POLICY-BOUNDARY EXTRACTION"
    )
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading exact T10 evidence...")

    if not T10_EVIDENCE.exists():
        raise RuntimeError(
            f"T10 evidence missing: {T10_EVIDENCE}"
        )

    with T10_EVIDENCE.open(
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    print("  T10 evidence: PRESENT")
    print(
        f"  Top-level type: "
        f"{type(data).__name__}"
    )

    if isinstance(data, dict):
        print(
            f"  Top-level keys: "
            f"{list(data.keys())}"
        )

    print("\n[2] Relevant policy-boundary fields...")

    matches = {}

    for _ in walk(data):
        pass

    def collect(obj, path="$"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current = f"{path}.{key}"

                if any(
                    keyword in str(key).lower()
                    for keyword in KEYWORDS
                ):
                    matches[current] = value

                collect(value, current)

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                collect(
                    value,
                    f"{path}[{index}]"
                )

    collect(data)

    if not matches:
        print("  NO matching structured keys found")
    else:
        for path, value in matches.items():
            print(f"  {path} = {value}")

    print("\n[3] Searching values for explicit policy-boundary statements...")

    value_matches = {}

    def collect_values(obj, path="$"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current = f"{path}.{key}"

                if isinstance(value, (str, int, float, bool)):
                    text = str(value).lower()

                    if any(
                        phrase in text
                        for phrase in (
                            "not established",
                            "not validated",
                            "not created",
                            "no empirical",
                            "no universal",
                            "synthetic",
                            "threshold",
                        )
                    ):
                        value_matches[current] = value

                collect_values(value, current)

        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                collect_values(
                    value,
                    f"{path}[{index}]"
                )

    collect_values(data)

    if not value_matches:
        print("  NO explicit boundary statements found")
    else:
        for path, value in value_matches.items():
            print(f"  {path} = {value}")

    print("\n[4] Direct evidence conclusion...")

    print(
        "  This operation does NOT infer a threshold."
    )

    print(
        "  This operation does NOT create a threshold."
    )

    print(
        "  This operation only reports the exact "
        "T10 evidence representation."
    )

    result = {
        "operation":
            "FMP-06 OP-022R3",

        "status":
            "PASS",

        "read_only":
            True,

        "training_performed":
            False,

        "fitting_performed":
            False,

        "prediction_performed":
            False,

        "evaluation_performed":
            False,

        "locked_test_used":
            False,

        "artifact_modified":
            False,

        "source":
            str(T10_EVIDENCE),

        "relevant_structured_fields":
            matches,

        "explicit_boundary_statements":
            value_matches,

        "interpretation":
            (
                "Direct extraction of the authoritative T10 "
                "policy-boundary evidence. No threshold, risk "
                "score, confidence score, or synthetic target "
                "is inferred or created."
            ),
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUT.open(
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            default=str
        )

    print("\n" + "=" * 72)
    print("OP-022R3 EXTRACTION COMPLETE")
    print("=" * 72)

    print(f"Output: {OUT}")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()