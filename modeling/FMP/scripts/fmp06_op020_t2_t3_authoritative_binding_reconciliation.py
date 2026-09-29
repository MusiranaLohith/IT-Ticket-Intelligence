from pathlib import Path
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OP011D = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op011d_frozen_t2_t3_artifact_binding.json"
)

T2_ARTIFACT = (
    ROOT / "modeling/T2/models/"
    "t2_class_weighted_tfidf_logreg.joblib"
)

T3_ARTIFACT = (
    ROOT / "modeling/T3/models/"
    "t3_class_weighted_tfidf_logreg.joblib"
)

OUT = (
    ROOT / "modeling/FMP/metrics/"
    "fmp06_op020_t2_t3_authoritative_binding_reconciliation.json"
)


def main():
    print("=" * 72)
    print("FMP-06 OP-020 — T2/T3 AUTHORITATIVE BINDING RECONCILIATION")
    print("=" * 72)

    print("Read-only inspection: YES")
    print("Training/fitting: NO")
    print("Prediction: NO")
    print("Evaluation metrics: NO")
    print("Locked test: NO")
    print("Artifact modification: NO")

    print("\n[1] Loading OP-011D authoritative binding evidence...")

    if not OP011D.exists():
        raise RuntimeError(
            f"OP-011D evidence missing: {OP011D}"
        )

    with OP011D.open("r", encoding="utf-8") as f:
        evidence = json.load(f)

    print("  OP-011D evidence: PRESENT")

    evidence_text = json.dumps(
        evidence,
        sort_keys=True
    )

    t2_name = T2_ARTIFACT.name
    t3_name = T3_ARTIFACT.name

    t2_reference_present = (
        t2_name in evidence_text
    )

    t3_reference_present = (
        t3_name in evidence_text
    )

    print(
        f"  T2 exact artifact reference: "
        f"{t2_reference_present}"
    )

    print(
        f"  T3 exact artifact reference: "
        f"{t3_reference_present}"
    )

    print("\n[2] Verifying exact frozen artifact paths...")

    t2_exists = T2_ARTIFACT.exists()
    t3_exists = T3_ARTIFACT.exists()

    print(
        f"  T2: "
        f"{'PRESENT' if t2_exists else 'MISSING'}"
    )

    print(
        f"  T3: "
        f"{'PRESENT' if t3_exists else 'MISSING'}"
    )

    print("\n[3] Verifying artifact readability...")

    t2_size = (
        T2_ARTIFACT.stat().st_size
        if t2_exists
        else None
    )

    t3_size = (
        T3_ARTIFACT.stat().st_size
        if t3_exists
        else None
    )

    t2_readable = (
        t2_exists
        and t2_size is not None
        and t2_size > 0
    )

    t3_readable = (
        t3_exists
        and t3_size is not None
        and t3_size > 0
    )

    print(
        f"  T2 non-empty artifact: {t2_readable}"
    )

    print(
        f"  T3 non-empty artifact: {t3_readable}"
    )

    t2_pass = (
        t2_reference_present
        and t2_readable
    )

    t3_pass = (
        t3_reference_present
        and t3_readable
    )

    overall_pass = (
        t2_pass
        and t3_pass
    )

    print("\n[4] Final T2/T3 reconciliation...")

    print(
        f"  T2 authoritative binding: "
        f"{'PASS' if t2_pass else 'FAIL'}"
    )

    print(
        f"  T3 authoritative binding: "
        f"{'PASS' if t3_pass else 'FAIL'}"
    )

    result = {
        "operation":
            "FMP-06 OP-020",

        "status":
            "PASS" if overall_pass else "FAIL",

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

        "source_evidence":
            str(OP011D),

        "t2": {
            "artifact":
                str(T2_ARTIFACT),
            "exact_reference_in_op011d":
                t2_reference_present,
            "exists":
                t2_exists,
            "size_bytes":
                t2_size,
            "readable_nonempty":
                t2_readable,
            "status":
                "PASS" if t2_pass else "FAIL",
        },

        "t3": {
            "artifact":
                str(T3_ARTIFACT),
            "exact_reference_in_op011d":
                t3_reference_present,
            "exists":
                t3_exists,
            "size_bytes":
                t3_size,
            "readable_nonempty":
                t3_readable,
            "status":
                "PASS" if t3_pass else "FAIL",
        },

        "interpretation":
            (
                "T2 and T3 are reconciled using the authoritative "
                "OP-011D exact artifact-binding evidence rather than "
                "assuming a particular closure-file path."
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
            indent=2
        )

    print("\n" + "=" * 72)
    print("OP-020 RECONCILIATION COMPLETE")
    print("=" * 72)

    print(f"Status: {result['status']}")
    print(f"Output: {OUT}")

    print("\nNo training performed.")
    print("No fitting performed.")
    print("No prediction performed.")
    print("No evaluation performed.")
    print("No locked test used.")
    print("No artifact modification performed.")

    print("=" * 72)


if __name__ == "__main__":
    main()