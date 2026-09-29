from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
METRICS = ROOT / "modeling" / "FMP" / "metrics"


FILES = {
    "T1_T7": METRICS / "fmp06_op019r1_final_t1_t7_runtime_binding_reconciliation.json",
    "T5_T10": METRICS / "fmp06_op022r2_t5_t10_authoritative_boundary_reconciliation.json",
    "T10": METRICS / "fmp06_op022r3_t10_direct_policy_boundary_extraction.json",
}


INTERESTING_KEY_TERMS = (
    "status",
    "determination",
    "policy",
    "boundary",
    "automation",
    "human_review",
    "confidence",
    "risk",
    "threshold",
    "synthetic",
    "runtime",
)


INTERESTING_VALUE_TERMS = (
    "PASS",
    "COMPLETE",
    "CLOSED",
    "REQUIRES_REVIEW",
    "NOT_ESTABLISHED",
    "NOT_EMPIRICALLY_ESTABLISHED",
    "NOT_CREATED",
    "FALSE",
    "TRUE",
)


def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{path}.{key}"

            key_match = any(
                term in str(key).lower()
                for term in INTERESTING_KEY_TERMS
            )

            if isinstance(value, (str, int, float, bool)) or value is None:
                value_text = str(value)

                value_match = any(
                    term in value_text.upper()
                    for term in INTERESTING_VALUE_TERMS
                )

                if key_match or value_match:
                    print(f"  {current} = {value}")

            walk(value, current)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            walk(value, f"{path}[{index}]")


def main():
    print("=" * 72)
    print("FMP-06 OP-022R5 — AUTHORITATIVE RECONCILIATION STRUCTURE INSPECTION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    for name, path in FILES.items():
        print("\n" + "-" * 72)
        print(f"[{name}]")
        print(f"File: {path}")

        if not path.exists():
            print("  STATUS = MISSING")
            continue

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"  Top-level type: {type(data).__name__}")

        if isinstance(data, dict):
            print(f"  Top-level keys: {list(data.keys())}")

        print("\n  Relevant JSON paths:")
        walk(data)

    print("\n" + "=" * 72)
    print("OP-022R5 INSPECTION COMPLETE")
    print("=" * 72)
    print("No interpretation performed.")
    print("No threshold selected.")
    print("No threshold optimized.")
    print("No training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")


if __name__ == "__main__":
    main()