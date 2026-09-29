from __future__ import annotations

import re
from pathlib import Path


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

SEARCH_ROOTS = [
    ROOT / "modeling" / "T10",
    ROOT / "modeling" / "FMP",
    ROOT / "modeling",
    ROOT / "docs",
    ROOT / "documentation",
]

EXTENSIONS = {
    ".json",
    ".md",
    ".txt",
    ".csv",
    ".py",
}

TERMS = [
    "T10",
    "MODEL-INDEPENDENT",
    "EMPIRICAL EVIDENCE",
    "human_review",
    "human review",
    "review",
    "defer",
    "automation",
    "policy",
    "threshold",
]


def matches_name(path: Path) -> bool:
    name = path.name.lower()

    return any(
        term.lower().replace(" ", "_") in name
        or term.lower().replace(" ", "-") in name
        for term in TERMS
    )


def search_content(path: Path):
    try:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return []

    matches = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()

        matched_terms = [
            term
            for term in TERMS
            if term.lower() in lowered
        ]

        if matched_terms:
            matches.append(
                (
                    line_no,
                    matched_terms,
                    line.strip(),
                )
            )

    return matches


def main():
    print("=" * 80)
    print("FMP-05 OP-002 — LOCATE EXISTING T10 EVIDENCE")
    print("=" * 80)

    print("\n[1] Search roots")
    print("-" * 80)

    for root in SEARCH_ROOTS:
        print(f"{root} | exists={root.exists()}")

    print("\n[2] Candidate artifact discovery")
    print("-" * 80)

    candidates = set()

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in EXTENSIONS:
                continue

            if matches_name(path):
                candidates.add(path)

    candidates = sorted(candidates)

    print(f"Filename-matched artifacts: {len(candidates)}")

    for path in candidates:
        print(path)

    print("\n[3] Content evidence discovery")
    print("-" * 80)

    content_hits = {}

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in EXTENSIONS:
                continue

            hits = search_content(path)

            if hits:
                content_hits[path] = hits

    print(f"Artifacts containing target terms: {len(content_hits)}")

    for path in sorted(content_hits):
        print(f"\nFILE: {path}")

        # Limit displayed evidence per file so the output remains manageable.
        shown = content_hits[path][:12]

        for line_no, terms, line in shown:
            print(
                f"  L{line_no} "
                f"[{', '.join(terms)}] "
                f"{line[:300]}"
            )

        remaining = len(content_hits[path]) - len(shown)

        if remaining > 0:
            print(f"  ... {remaining} additional matching lines")

    print("\n[4] T10-specific evidence indicators")
    print("-" * 80)

    indicator_patterns = {
        "model_independent":
            re.compile(r"MODEL[-_ ]INDEPENDENT", re.I),

        "empirical_evidence":
            re.compile(r"EMPIRICAL\s+EVIDENCE", re.I),

        "human_review":
            re.compile(r"HUMAN[_ ]REVIEW", re.I),

        "automation":
            re.compile(r"AUTOMATION", re.I),

        "defer":
            re.compile(r"\bDEFER\b", re.I),

        "threshold":
            re.compile(r"\bTHRESHOLD\b", re.I),
    }

    indicator_counts = {
        key: 0
        for key in indicator_patterns
    }

    for path, hits in content_hits.items():
        for _, _, line in hits:
            for key, pattern in indicator_patterns.items():
                if pattern.search(line):
                    indicator_counts[key] += 1

    for key, count in indicator_counts.items():
        print(f"{key}: {count}")

    print("\n[5] Read-only safeguards")
    print("-" * 80)

    print("Models loaded: False")
    print("Predictions generated: False")
    print("Retraining performed: False")
    print("Calibration fitted: False")
    print("Threshold selected: False")
    print("Policy created: False")
    print("Artifacts modified: False")

    print("\n[6] Final summary")
    print("-" * 80)

    print(
        "Operation type: "
        "READ_ONLY_T10_EVIDENCE_DISCOVERY"
    )

    print("STATUS: PASS")


if __name__ == "__main__":
    main()