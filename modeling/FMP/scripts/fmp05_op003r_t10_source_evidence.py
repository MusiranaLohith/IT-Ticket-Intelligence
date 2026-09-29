from pathlib import Path
import json
import re


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SOURCE_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "project_consolidation.py"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "fmp05_op003r_t10_source_evidence.json"
)


# Terms specifically relevant to the T10 decision-policy layer.
TARGET_TERMS = [
    "model_independent",
    "empirical_evidence",
    "human_review",
    "automation",
    "defer",
    "threshold",
    "unsupported_operational_threshold_claim",
    "universal",
    "autonomous",
    "policy",
]


def main():
    print("=" * 80)
    print("FMP-05 OP-003R — T10 SOURCE EVIDENCE EXTRACTION")
    print("=" * 80)

    print()
    print("[1] Source")
    print("-" * 80)

    print(f"Source file: {SOURCE_FILE}")
    print(f"Exists     : {SOURCE_FILE.exists()}")

    if not SOURCE_FILE.exists():
        raise RuntimeError(
            f"Expected source file does not exist: {SOURCE_FILE}"
        )

    text = SOURCE_FILE.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lines = text.splitlines()

    print(f"Source lines: {len(lines)}")

    print()
    print("[2] Searching for T10 evidence terms")
    print("-" * 80)

    matches = []

    for line_number, line in enumerate(lines, start=1):
        lowered = line.lower()

        matched_terms = [
            term
            for term in TARGET_TERMS
            if term.lower() in lowered
        ]

        if matched_terms:
            matches.append(
                {
                    "line": line_number,
                    "terms": matched_terms,
                    "text": line.strip(),
                }
            )

    print(f"Matching source lines: {len(matches)}")

    print()
    print("[3] Evidence counts")
    print("-" * 80)

    term_counts = {
        term: 0
        for term in TARGET_TERMS
    }

    for match in matches:
        for term in match["terms"]:
            term_counts[term] += 1

    for term, count in term_counts.items():
        print(f"{term}: {count}")

    print()
    print("[4] Relevant source excerpts")
    print("-" * 80)

    # Show every matching line, but keep the console manageable.
    display_limit = 250

    for index, match in enumerate(matches[:display_limit], start=1):
        print()
        print(
            f"[{index}] L{match['line']} "
            f"[{', '.join(match['terms'])}]"
        )
        print(match["text"])

    if len(matches) > display_limit:
        print()
        print(
            f"... {len(matches) - display_limit} "
            "additional matching lines stored in the output artifact."
        )

    print()
    print("[5] Explicit threshold-policy evidence")
    print("-" * 80)

    threshold_matches = [
        match
        for match in matches
        if (
            "threshold" in match["terms"]
            or "unsupported_operational_threshold_claim"
            in match["terms"]
        )
    ]

    print(
        f"Threshold-related source lines: "
        f"{len(threshold_matches)}"
    )

    for match in threshold_matches:
        print(
            f"L{match['line']} "
            f"[{', '.join(match['terms'])}] "
            f"{match['text']}"
        )

    print()
    print("[6] Human-review / defer evidence")
    print("-" * 80)

    review_defer_matches = [
        match
        for match in matches
        if (
            "human_review" in match["terms"]
            or "defer" in match["terms"]
        )
    ]

    print(
        f"Human-review/defer source lines: "
        f"{len(review_defer_matches)}"
    )

    for match in review_defer_matches:
        print(
            f"L{match['line']} "
            f"[{', '.join(match['terms'])}] "
            f"{match['text']}"
        )

    print()
    print("[7] Safeguards")
    print("-" * 80)

    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining performed: False")
    print("Calibration fitted: False")
    print("Threshold selected: False")
    print("Policy modified: False")
    print("Artifacts modified: False")

    result = {
        "operation": "FMP-05-OP-003R",
        "operation_type": (
            "READ_ONLY_T10_SOURCE_EVIDENCE_EXTRACTION"
        ),
        "status": "PASS",
        "source_file": str(SOURCE_FILE),
        "source_line_count": len(lines),
        "matching_source_line_count": len(matches),
        "term_counts": term_counts,
        "matches": matches,
        "threshold_matches": threshold_matches,
        "human_review_defer_matches": review_defer_matches,
        "read_only_safeguards": {
            "models_loaded": False,
            "predictions_generated": False,
            "retraining_performed": False,
            "calibration_fitted": False,
            "threshold_selected": False,
            "policy_modified": False,
            "artifacts_modified": False,
        },
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("[8] Output")
    print("-" * 80)

    print(f"Saved: {OUTPUT_FILE}")

    print()
    print("[9] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_T10_SOURCE_EVIDENCE_EXTRACTION"
    )

    print("STATUS: PASS")

    print("=" * 80)


if __name__ == "__main__":
    main()