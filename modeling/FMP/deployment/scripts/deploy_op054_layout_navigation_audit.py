from pathlib import Path
import hashlib
import json
import re


BASE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = BASE / "deployment/frontend"
METRICS = BASE / "modeling/FMP/metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

EVIDENCE = METRICS / "deploy_op054_layout_navigation_audit.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section(text, title):
    print(f"\n[{title}]")
    print("-" * 66)
    print(text)


def find_context(text, pattern, radius=220):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

    if not match:
        return None

    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)

    return text[start:end]


def main():
    print("=" * 66)
    print("DEPLOY-OP-054 — LAYOUT + NAVIGATION AUDIT")
    print("=" * 66)

    required = [INDEX, APP, STYLE]

    missing = [
        str(path)
        for path in required
        if not path.exists()
    ]

    if missing:
        print("\nSTATUS: BLOCKED")
        print("Missing frontend files:")

        for path in missing:
            print(f"  {path}")

        raise SystemExit(1)

    index_text = INDEX.read_text(encoding="utf-8")
    app_text = APP.read_text(encoding="utf-8")
    style_text = STYLE.read_text(encoding="utf-8")

    hashes_before = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    print("\nFRONTEND")
    print("-" * 66)
    print(f"INDEX: {INDEX}")
    print(f"APP:   {APP}")
    print(f"STYLE: {STYLE}")

    print("\nSOURCE HASHES")
    print("-" * 66)

    for name, value in hashes_before.items():
        print(f"{name}: {value}")

    # ---------------------------------------------------------
    # 1. LANDING STRUCTURE
    # ---------------------------------------------------------

    landing_present = (
        'id="project-landing"' in index_text
        and 'class="project-view project-landing"' in index_text
    )

    landing_inner_present = (
        'class="project-landing-inner"' in index_text
    )

    workspace_present = (
        'id="workspace-home"' in index_text
        and 'class="project-view workspace-home"' in index_text
    )

    print("\nLANDING / WORKSPACE STRUCTURE")
    print("-" * 66)
    print(f"PROJECT_LANDING:       {'FOUND' if landing_present else 'MISSING'}")
    print(f"LANDING_INNER:         {'FOUND' if landing_inner_present else 'MISSING'}")
    print(f"WORKSPACE_HOME:        {'FOUND' if workspace_present else 'MISSING'}")

    # ---------------------------------------------------------
    # 2. LANDING WIDTH / BACKGROUND RULES
    # ---------------------------------------------------------

    project_view_match = re.search(
        r"\.project-view\s*\{.*?\}",
        style_text,
        re.IGNORECASE | re.DOTALL,
    )

    project_landing_match = re.search(
        r"\.project-landing\s*\{.*?\}",
        style_text,
        re.IGNORECASE | re.DOTALL,
    )

    project_view_block = (
        project_view_match.group(0)
        if project_view_match
        else None
    )

    project_landing_block = (
        project_landing_match.group(0)
        if project_landing_match
        else None
    )

    print("\nLANDING WIDTH / BACKGROUND AUDIT")
    print("-" * 66)

    if project_view_block:
        print("PROJECT_VIEW_RULE: FOUND")
        print(project_view_block)
    else:
        print("PROJECT_VIEW_RULE: MISSING")

    if project_landing_block:
        print("\nPROJECT_LANDING_RULE: FOUND")
        print(project_landing_block)
    else:
        print("\nPROJECT_LANDING_RULE: MISSING")

    print("\nFULL-WIDTH INDICATORS")
    print("-" * 66)

    width_indicators = {
        "width_100vw": "width: 100vw" in project_landing_block
        if project_landing_block else False,

        "max_width_none": "max-width: none" in project_landing_block
        if project_landing_block else False,

        "viewport_margin": (
            "50vw" in project_landing_block
            if project_landing_block
            else False
        ),

        "overflow_hidden": (
            "overflow: hidden" in project_landing_block
            if project_landing_block
            else False
        ),
    }

    for name, present in width_indicators.items():
        print(
            f"{name.upper():24} "
            f"{'PRESENT' if present else 'ABSENT'}"
        )

    # ---------------------------------------------------------
    # 3. WORKSPACE KICKER / HEADER
    # ---------------------------------------------------------

    kicker_candidates = [
        "workspace-kicker",
        "workspace-label",
        "workspace-eyebrow",
        "workspace-heading",
        "IT TICKET INTELLIGENCE",
    ]

    print("\nWORKSPACE HEADER / KICKER")
    print("-" * 66)

    kicker_results = {}

    for candidate in kicker_candidates:
        present = candidate.lower() in index_text.lower()
        kicker_results[candidate] = present

        print(
            f"{candidate:28} "
            f"{'FOUND' if present else 'NOT FOUND'}"
        )

    kicker_css = {}

    for selector in [
        ".workspace-kicker",
        ".workspace-label",
        ".workspace-eyebrow",
        ".workspace-heading",
        ".workspace-home",
    ]:
        match = re.search(
            re.escape(selector) + r"\s*\{.*?\}",
            style_text,
            re.IGNORECASE | re.DOTALL,
        )

        kicker_css[selector] = (
            match.group(0)
            if match
            else None
        )

    print("\nWORKSPACE CSS RULES")

    for selector, block in kicker_css.items():
        if block:
            print(f"\n{selector}")
            print(block)

    # ---------------------------------------------------------
    # 4. NAVIGATION CONTROLS
    # ---------------------------------------------------------

    navigation_ids = [
        "enter-system-button",
        "view-research-button",
        "open-analysis-workspace-button",
        "analysis-home-button",
        "project-overview-button",
        "reset-dashboard-button",
    ]

    print("\nNAVIGATION CONTROLS")
    print("-" * 66)

    navigation_results = {}

    for element_id in navigation_ids:
        html_count = len(
            re.findall(
                rf'id="{re.escape(element_id)}"',
                index_text,
            )
        )

        js_count = len(
            re.findall(
                rf'getElementById\(\s*["\']{re.escape(element_id)}["\']\s*\)',
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

    # ---------------------------------------------------------
    # 5. WORKSPACE HOME BLOCK
    # ---------------------------------------------------------

    workspace_match = re.search(
        r'<section[^>]+id="workspace-home".*?</section>',
        index_text,
        re.IGNORECASE | re.DOTALL,
    )

    workspace_block = (
        workspace_match.group(0)
        if workspace_match
        else ""
    )

    print("\nWORKSPACE HOME NAVIGATION")
    print("-" * 66)

    workspace_nav_candidates = [
        "project-overview-button",
        "analysis-home-button",
        "back-to-home",
        "home",
    ]

    workspace_nav_results = {}

    for candidate in workspace_nav_candidates:
        present = candidate.lower() in workspace_block.lower()

        workspace_nav_results[candidate] = present

        print(
            f"{candidate:28} "
            f"{'FOUND' if present else 'NOT FOUND'}"
        )

    # ---------------------------------------------------------
    # 6. APP NAVIGATION IMPLEMENTATION
    # ---------------------------------------------------------

    function_candidates = [
        "showProjectLanding",
        "showWorkspaceHome",
        "showAnalysisWorkspace",
        "initializeProjectNavigation",
    ]

    print("\nNAVIGATION FUNCTIONS")
    print("-" * 66)

    function_results = {}

    for function_name in function_candidates:
        present = (
            f"function {function_name}" in app_text
            or f"const {function_name}" in app_text
            or f"{function_name} =" in app_text
        )

        function_results[function_name] = present

        print(
            f"{function_name:30} "
            f"{'FOUND' if present else 'MISSING'}"
        )

    # ---------------------------------------------------------
    # 7. EXACT RELEVANT CONTEXT
    # ---------------------------------------------------------

    print("\nPROJECT LANDING CONTEXT")
    print("-" * 66)

    landing_context = find_context(
        index_text,
        r'id="project-landing"',
    )

    if landing_context:
        print(landing_context)

    print("\nWORKSPACE CONTEXT")
    print("-" * 66)

    workspace_context = find_context(
        index_text,
        r'id="workspace-home"',
    )

    if workspace_context:
        print(workspace_context)

    print("\nSHOW PROJECT LANDING CONTEXT")
    print("-" * 66)

    project_landing_function = find_context(
        app_text,
        r'function showProjectLanding',
        radius=650,
    )

    if project_landing_function:
        print(project_landing_function)

    # ---------------------------------------------------------
    # 8. READ-ONLY GUARANTEE
    # ---------------------------------------------------------

    hashes_after = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    unchanged = hashes_before == hashes_after

    print("\nREAD-ONLY VALIDATION")
    print("-" * 66)

    for name in hashes_before:
        print(
            f"{name:12} "
            f"{'UNCHANGED' if hashes_before[name] == hashes_after[name] else 'MODIFIED'}"
        )

    print(
        f"\nFILES_MODIFIED: "
        f"{'FALSE' if unchanged else 'TRUE'}"
    )

    evidence = {
        "operation": "DEPLOY-OP-054",
        "title": "Layout and Navigation Audit",
        "status": "PASS" if unchanged else "FAIL",
        "scope": "Read-only frontend audit",
        "landing": {
            "present": landing_present,
            "inner_present": landing_inner_present,
            "project_view_rule": project_view_block,
            "project_landing_rule": project_landing_block,
            "full_width_indicators": width_indicators,
        },
        "workspace": {
            "present": workspace_present,
            "kicker_candidates": kicker_results,
            "css_rules": kicker_css,
            "navigation_candidates": workspace_nav_results,
        },
        "navigation": navigation_results,
        "functions": function_results,
        "hashes_before": hashes_before,
        "hashes_after": hashes_after,
        "files_modified": not unchanged,
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

    print(
        f"\nSTATUS: "
        f"{'PASS' if unchanged else 'FAIL'}"
    )


if __name__ == "__main__":
    main()
