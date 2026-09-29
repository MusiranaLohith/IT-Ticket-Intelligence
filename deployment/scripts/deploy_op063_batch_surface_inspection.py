from pathlib import Path


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

STYLE = (
    ROOT
    / "deployment"
    / "frontend"
    / "style.css"
)


def show_block(
    text: str,
    marker: str,
    context: int = 900,
) -> None:

    position = text.find(marker)

    if position == -1:
        print(
            f"\nNOT FOUND: {marker}"
        )
        return

    start = max(
        0,
        position - context,
    )

    end = min(
        len(text),
        position + context,
    )

    print(
        "\n"
        + "=" * 72
    )

    print(
        f"MARKER: {marker}"
    )

    print(
        "=" * 72
    )

    print(
        text[start:end]
    )


def main():

    print("=" * 72)
    print("DEPLOY-OP-063 — BATCH SURFACE SELECTOR INSPECTION")
    print("=" * 72)

    if not STYLE.exists():

        raise RuntimeError(
            f"FAIL: style.css not found: {STYLE}"
        )

    css = STYLE.read_text(
        encoding="utf-8"
    )

    print("\n[1] CURRENT FILE")
    print("-" * 72)

    print(STYLE)

    print("\n[2] OP-062 RESTORE CHECK")
    print("-" * 72)

    print(
        "OP-062 marker present:",
        "DEPLOY-OP-062 — FULL-PAGE GLASS APPLICATION SURFACES"
        in css,
    )

    print(
        "OP-061 marker present:",
        "DEPLOY-OP-061"
        in css,
    )

    print("\n[3] BATCH STRUCTURE SELECTORS")
    print("-" * 72)

    selectors = [
        "#batch-input-panel",
        ".batch-input-layout",
        ".batch-file-area",
        "#batch-file",
        'input[type="file"]',
        ".form-group",
        ".batch-error-message",
        "#batch-validate-button",
    ]

    for selector in selectors:

        print(
            f"{selector:35}: "
            f"{'FOUND' if selector in css else 'MISSING'}"
        )

    print("\n[4] EXACT BATCH FILE AREA")
    print("-" * 72)

    show_block(
        css,
        ".batch-file-area",
        context=1400,
    )

    print("\n[5] EXACT BATCH INPUT PANEL")
    print("-" * 72)

    show_block(
        css,
        "#batch-input-panel",
        context=1800,
    )

    print("\n[6] FILE INPUT STYLING")
    print("-" * 72)

    show_block(
        css,
        'input[type="file"]',
        context=1600,
    )

    print("\n[7] OPERATION CONCLUSION")
    print("-" * 72)

    print(
        "READ-ONLY INSPECTION COMPLETE"
    )

    print(
        "FILES MODIFIED: FALSE"
    )

    print(
        "STATUS: PASS"
    )


if __name__ == "__main__":
    main()
