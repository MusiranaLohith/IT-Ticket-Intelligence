from pathlib import Path
import hashlib
import json
import re


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"

INDEX = FRONTEND / "index.html"
STYLE = FRONTEND / "style.css"
APP = FRONTEND / "app.js"

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

EVIDENCE = (
    METRICS
    / "deploy_op068_research_css_audit.json"
)


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def require_file(path):
    if not path.exists():
        raise RuntimeError(
            f"BLOCKED: missing required file: {path}"
        )


def extract_research_block(index_text):
    match = re.search(
        r'<section[^>]+id="research-overview".*?</section>',
        index_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        raise RuntimeError(
            "BLOCKED: research-overview section not found."
        )

    return match.group(0)


def extract_classes(html_block):
    classes = set()

    for match in re.finditer(
        r'class="([^"]+)"',
        html_block,
        re.IGNORECASE,
    ):
        for value in match.group(1).split():
            classes.add(value)

    return sorted(classes)


def selector_present(style_text, class_name):
    pattern = (
        rf'(?m)^\s*[^@{{}}]*\.{re.escape(class_name)}'
        rf'(?:[\s.#:[\]>+~]|$)'
    )

    return bool(
        re.search(
            pattern,
            style_text,
        )
    )


def extract_rule(style_text, selector):
    match = re.search(
        re.escape(selector)
        + r"\s*\{.*?\}",
        style_text,
        re.IGNORECASE | re.DOTALL,
    )

    return (
        match.group(0)
        if match
        else None
    )


def main():

    print("=" * 72)
    print(
        "DEPLOY-OP-068 — RESEARCH VIEW CSS AUDIT"
    )
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in [
        INDEX,
        STYLE,
        APP,
    ]:
        require_file(path)
        print(f"FOUND: {path}")

    index_text = INDEX.read_text(
        encoding="utf-8"
    )

    style_text = STYLE.read_text(
        encoding="utf-8"
    )

    app_text = APP.read_text(
        encoding="utf-8"
    )

    style_hash_before = sha256(STYLE)

    # =========================================================
    # 2. RESEARCH HTML STRUCTURE
    # =========================================================

    print("\n[2] RESEARCH HTML STRUCTURE")
    print("-" * 72)

    research_block = extract_research_block(
        index_text
    )

    print("research-overview: FOUND")

    classes = extract_classes(
        research_block
    )

    print("\nRESEARCH CLASSES")
    print("-" * 72)

    for class_name in classes:
        print(f".{class_name}")

    # =========================================================
    # 3. CSS COVERAGE
    # =========================================================

    print("\n[3] RESEARCH CSS COVERAGE")
    print("-" * 72)

    css_coverage = {}

    for class_name in classes:
        present = selector_present(
            style_text,
            class_name,
        )

        css_coverage[class_name] = present

        print(
            f".{class_name:42} "
            f"{'STYLED' if present else 'UNSTYLED'}"
        )

    research_specific_classes = [
        name
        for name in classes
        if name.startswith("research-")
    ]

    research_specific_coverage = {
        name: selector_present(
            style_text,
            name,
        )
        for name in research_specific_classes
    }

    # =========================================================
    # 4. KEY RESEARCH SELECTORS
    # =========================================================

    print("\n[4] KEY RESEARCH SELECTORS")
    print("-" * 72)

    key_selectors = [
        ".research-overview",
        ".research-overview-inner",
        ".research-overview-header",
        ".research-section",
        ".research-section-label",
        ".research-overview-footer",
        ".research-home-button",
        ".research-workflow-list",
        ".research-limitations-list",
    ]

    key_selector_results = {}

    for selector in key_selectors:
        present = selector in style_text

        key_selector_results[selector] = present

        print(
            f"{selector:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

    # =========================================================
    # 5. GLOBAL VIEW / VIEWPORT CSS
    # =========================================================

    print("\n[5] GLOBAL VIEW / VIEWPORT CSS")
    print("-" * 72)

    global_selectors = [
        ".project-view",
        ".hidden",
        "body",
        "body.app-view-landing",
        "body.app-view-workspace",
        "body.app-view-analysis",
        "body.app-view-research",
    ]

    global_rules = {}

    for selector in global_selectors:
        rule = extract_rule(
            style_text,
            selector,
        )

        global_rules[selector] = rule

        print(f"\n{selector}")

        if rule:
            print(rule)
        else:
            print("NOT FOUND")

    # =========================================================
    # 6. COLOUR / DESIGN SYSTEM AUDIT
    # =========================================================

    print("\n[6] COLOUR / DESIGN SYSTEM AUDIT")
    print("-" * 72)

    colour_tokens = {}

    colour_patterns = {
        "hex": r"#[0-9a-fA-F]{3,8}",
        "rgb": r"rgba?\([^)]*\)",
        "hsl": r"hsla?\([^)]*\)",
    }

    for name, pattern in colour_patterns.items():
        matches = sorted(
            set(
                re.findall(
                    pattern,
                    style_text,
                )
            )
        )

        colour_tokens[name] = matches

        print(
            f"{name.upper():8} "
            f"{len(matches)} unique values"
        )

        for value in matches[:20]:
            print(f"  {value}")

        if len(matches) > 20:
            print(
                f"  ... {len(matches) - 20} more"
            )

    semantic_colour_terms = {
        "green": [
            "green",
            "#16a34a",
            "#15803d",
            "#22c55e",
            "#10b981",
        ],
        "yellow_amber": [
            "yellow",
            "amber",
            "#f59e0b",
            "#d97706",
            "#eab308",
        ],
        "red": [
            "red",
            "#dc2626",
            "#b91c1c",
            "#ef4444",
        ],
        "blue": [
            "blue",
            "#2563eb",
            "#1d4ed8",
            "#3b82f6",
        ],
    }

    semantic_colour_presence = {}

    for name, values in semantic_colour_terms.items():

        found = [
            value
            for value in values
            if value.lower() in style_text.lower()
        ]

        semantic_colour_presence[name] = found

        print(
            f"{name:14} "
            f"{'PRESENT' if found else 'NOT PRESENT'}"
        )

    # =========================================================
    # 7. RESEARCH SEMANTIC HIGHLIGHTING
    # =========================================================

    print("\n[7] RESEARCH SEMANTIC HIGHLIGHTING")
    print("-" * 72)

    semantic_classes = [
        "research-result",
        "research-success",
        "research-warning",
        "research-caution",
        "research-limitation",
        "research-principle",
        "research-dataset",
        "research-task",
        "research-metric",
        "research-boundary",
    ]

    semantic_class_results = {}

    for class_name in semantic_classes:

        html_present = (
            f'class="{class_name}"'
            in research_block
            or f" {class_name}" in research_block
        )

        css_present = selector_present(
            style_text,
            class_name,
        )

        semantic_class_results[
            class_name
        ] = {
            "html_present": html_present,
            "css_present": css_present,
        }

        print(
            f".{class_name:28} "
            f"HTML={'YES' if html_present else 'NO'} "
            f"CSS={'YES' if css_present else 'NO'}"
        )

    # =========================================================
    # 8. BACK TO HOME CONTROLS
    # =========================================================

    print("\n[8] RESEARCH NAVIGATION CONTROLS")
    print("-" * 72)

    navigation_ids = [
        "research-home-button",
        "research-home-button-footer",
    ]

    navigation_results = {}

    for element_id in navigation_ids:

        html_count = len(
            re.findall(
                rf'id="{re.escape(element_id)}"',
                research_block,
            )
        )

        js_count = len(
            re.findall(
                rf'getElementById\(\s*["\']'
                rf'{re.escape(element_id)}'
                rf'["\']\s*\)',
                app_text,
            )
        )

        navigation_results[element_id] = {
            "html_count": html_count,
            "js_reference_count": js_count,
        }

        print(
            f"{element_id:36} "
            f"HTML={html_count} "
            f"APP.JS={js_count}"
        )

    # =========================================================
    # 9. RESPONSIVE CSS
    # =========================================================

    print("\n[9] RESPONSIVE CSS")
    print("-" * 72)

    media_blocks = re.findall(
        r"@media[^{]+\{.*?\n\}",
        style_text,
        re.IGNORECASE | re.DOTALL,
    )

    research_media = []

    for block in media_blocks:
        if "research-" in block:
            research_media.append(block)

    print(
        f"Research-specific @media blocks: "
        f"{len(research_media)}"
    )

    if research_media:
        for block in research_media:
            print("\n" + block)
    else:
        print(
            "No Research-specific responsive rules found."
        )

    # =========================================================
    # 10. RESEARCH VISUAL GAPS
    # =========================================================

    print("\n[10] VISUAL GAPS")
    print("-" * 72)

    gaps = {
        "research_container_styled": (
            ".research-overview"
            in style_text
        ),
        "research_inner_styled": (
            ".research-overview-inner"
            in style_text
        ),
        "research_header_styled": (
            ".research-overview-header"
            in style_text
        ),
        "research_sections_styled": (
            ".research-section"
            in style_text
        ),
        "research_labels_styled": (
            ".research-section-label"
            in style_text
        ),
        "semantic_success_styles": any(
            semantic_class_results[
                name
            ]["css_present"]
            for name in [
                "research-success",
                "research-result",
            ]
        ),
        "semantic_warning_styles": any(
            semantic_class_results[
                name
            ]["css_present"]
            for name in [
                "research-warning",
                "research-caution",
            ]
        ),
        "semantic_limitation_styles": (
            semantic_class_results[
                "research-limitation"
            ]["css_present"]
        ),
        "research_responsive_styles": (
            len(research_media) > 0
        ),
    }

    for name, present in gaps.items():
        print(
            f"{name:42} "
            f"{'PRESENT' if present else 'MISSING'}"
        )

    # =========================================================
    # 11. READ-ONLY INTEGRITY
    # =========================================================

    print("\n[11] READ-ONLY INTEGRITY")
    print("-" * 72)

    print(
        "index.html: READ ONLY"
    )
    print(
        "app.js:     READ ONLY"
    )
    print(
        "style.css:  READ ONLY"
    )

    style_hash_after = sha256(STYLE)

    style_unchanged = (
        style_hash_before
        == style_hash_after
    )

    print(
        f"STYLE HASH STABLE: "
        f"{'PASS' if style_unchanged else 'FAIL'}"
    )

    if not style_unchanged:
        raise RuntimeError(
            "FAIL: style.css changed during "
            "read-only audit."
        )

    # =========================================================
    # 12. EVIDENCE
    # =========================================================

    evidence = {
        "operation": "DEPLOY-OP-068",
        "title": "Research View CSS Audit",
        "status": "PASS",
        "mode": "read-only",
        "audited_files": [
            str(INDEX),
            str(APP),
            str(STYLE),
        ],
        "style_sha256": style_hash_after,
        "research_classes": classes,
        "css_coverage": css_coverage,
        "research_specific_css_coverage": (
            research_specific_coverage
        ),
        "key_selector_results": (
            key_selector_results
        ),
        "global_rules": global_rules,
        "colour_tokens": colour_tokens,
        "semantic_colour_presence": (
            semantic_colour_presence
        ),
        "semantic_class_results": (
            semantic_class_results
        ),
        "navigation_results": (
            navigation_results
        ),
        "research_media_block_count": (
            len(research_media)
        ),
        "visual_gaps": gaps,
        "modified_files": [],
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nEVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-068")
    print("STATUS: PASS")
    print("READ-ONLY AUDIT COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
