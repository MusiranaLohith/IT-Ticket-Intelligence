from pathlib import Path
import re


BASE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = BASE / "deployment/frontend"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"


def show_matches(label, text, pattern, limit=20):
    print(f"\n{label}")
    print("-" * 62)

    matches = list(
        re.finditer(
            pattern,
            text,
            re.IGNORECASE | re.DOTALL,
        )
    )

    print(f"MATCHES: {len(matches)}")

    for index, match in enumerate(matches[:limit], start=1):
        start = max(0, match.start() - 300)
        end = min(len(text), match.end() + 500)

        print(f"\n--- MATCH {index} ---")
        print(text[start:end])

    return len(matches)


def main():
    print("=" * 62)
    print("DEPLOY-OP-052B — LANDING IMPLEMENTATION INSPECTION")
    print("=" * 62)

    required = [INDEX, APP, STYLE]

    for path in required:
        if not path.exists():
            print(f"\nSTATUS: BLOCKED")
            print(f"Missing: {path}")
            raise SystemExit(1)

    index_text = INDEX.read_text(encoding="utf-8")
    app_text = APP.read_text(encoding="utf-8")
    style_text = STYLE.read_text(encoding="utf-8")

    print("\n[1] ENTER SYSTEM IMPLEMENTATION")
    print("-" * 62)

    show_matches(
        "ENTER SYSTEM — HTML",
        index_text,
        r'.{0,250}enter-system-button.{0,700}',
    )

    show_matches(
        "ENTER SYSTEM — JAVASCRIPT",
        app_text,
        r'.{0,500}enter-system.{0,1000}',
    )

    print("\n[2] VIEW RESEARCH IMPLEMENTATION")
    print("-" * 62)

    show_matches(
        "VIEW RESEARCH — HTML",
        index_text,
        r'.{0,250}view-research-button.{0,700}',
    )

    show_matches(
        "VIEW RESEARCH — JAVASCRIPT",
        app_text,
        r'.{0,500}view-research.{0,1000}',
    )

    print("\n[3] LANDING BUTTON CLASS IMPLEMENTATION")
    print("-" * 62)

    show_matches(
        "project-primary-action",
        style_text,
        r'.{0,100}project-primary-action.{0,1200}',
    )

    show_matches(
        "project-secondary-action",
        style_text,
        r'.{0,100}project-secondary-action.{0,1200}',
    )

    print("\n[4] PROJECT ACTIONS CSS")
    print("-" * 62)

    show_matches(
        "project-actions",
        style_text,
        r'.{0,100}project-actions.{0,1800}',
    )

    print("\n[5] LANDING VISUAL CSS")
    print("-" * 62)

    for selector in [
        "project-landing",
        "project-landing-inner",
        "project-kicker",
        "project-motto",
        "project-introduction",
        "project-research-strip",
        "project-feature",
        "project-feature-index",
    ]:
        show_matches(
            selector,
            style_text,
            rf'.{{0,100}}\.[\w-]*{re.escape(selector)}[\w-]*\s*\{{.{{0,1800}}',
            limit=5,
        )

    print("\n[6] LANDING MEDIA QUERIES")
    print("-" * 62)

    media_blocks = re.findall(
        r'@media[^{]*\{(?:[^{}]|\{[^{}]*\})*\}',
        style_text,
        re.IGNORECASE | re.DOTALL,
    )

    landing_media = [
        block
        for block in media_blocks
        if "project-" in block
    ]

    print(f"LANDING MEDIA BLOCKS: {len(landing_media)}")

    for index, block in enumerate(
        landing_media,
        start=1,
    ):
        print(f"\n--- MEDIA BLOCK {index} ---")
        print(block[:4000])

    print("\n[7] RESULT")
    print("-" * 62)

    print("READ-ONLY INSPECTION COMPLETE")
    print(f"INDEX: {INDEX}")
    print(f"APP:   {APP}")
    print(f"STYLE: {STYLE}")
    print("FILES MODIFIED: FALSE")
    print("STATUS: PASS")


if __name__ == "__main__":
    main()
