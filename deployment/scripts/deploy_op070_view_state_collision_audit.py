from pathlib import Path
import hashlib
import json
import re


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

EVIDENCE = (
    METRICS
    / "deploy_op070_view_state_collision_audit.json"
)


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def extract_function(text, name):
    marker = f"function {name}("

    start = text.find(marker)

    if start == -1:
        return None

    brace_start = text.find(
        "{",
        start
    )

    if brace_start == -1:
        return None

    depth = 0

    for index in range(
        brace_start,
        len(text)
    ):

        char = text[index]

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return text[
                    start:index + 1
                ]

    return None


def extract_css_rule(text, selector):
    pattern = (
        re.escape(selector)
        + r"\s*\{.*?\}"
    )

    match = re.search(
        pattern,
        text,
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
        "DEPLOY-OP-070 — VIEW-STATE COLLISION AUDIT"
    )
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in [
        INDEX,
        APP,
        STYLE,
    ]:

        if not path.exists():
            raise RuntimeError(
                f"BLOCKED: missing file: {path}"
            )

        print(
            f"FOUND: {path}"
        )

    index_text = INDEX.read_text(
        encoding="utf-8"
    )

    app_text = APP.read_text(
        encoding="utf-8"
    )

    style_text = STYLE.read_text(
        encoding="utf-8"
    )

    hashes_before = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    # =========================================================
    # 2. VIEW STRUCTURE
    # =========================================================

    print("\n[2] VIEW STRUCTURE")
    print("-" * 72)

    view_ids = [
        "project-landing",
        "workspace-home",
        "research-overview",
        "analysis-workspace",
    ]

    view_structure = {}

    for view_id in view_ids:

        count = len(
            re.findall(
                rf'id="{re.escape(view_id)}"',
                index_text,
            )
        )

        view_structure[view_id] = count

        print(
            f"{view_id:28} "
            f"HTML COUNT = {count}"
        )

    # =========================================================
    # 3. DOM ORDER
    # =========================================================

    print("\n[3] VIEW DOM ORDER")
    print("-" * 72)

    positions = {}

    for view_id in view_ids:

        marker = (
            f'id="{view_id}"'
        )

        position = index_text.find(
            marker
        )

        positions[view_id] = position

        print(
            f"{view_id:28} "
            f"POSITION = {position}"
        )

    dom_order = sorted(
        positions.items(),
        key=lambda item: item[1]
    )

    print("\nORDER:")

    for index, (
        view_id,
        position
    ) in enumerate(
        dom_order,
        start=1
    ):

        print(
            f"{index}. {view_id} "
            f"@ {position}"
        )

    # =========================================================
    # 4. NAVIGATION FUNCTIONS
    # =========================================================

    print("\n[4] NAVIGATION FUNCTIONS")
    print("-" * 72)

    function_names = [
        "showProjectLanding",
        "showWorkspaceHome",
        "showAnalysisWorkspace",
        "showResearchOverview",
        "applyApplicationViewState",
    ]

    functions = {}

    for name in function_names:

        function = extract_function(
            app_text,
            name
        )

        functions[name] = function

        print(
            f"{name:32} "
            f"{'FOUND' if function else 'MISSING'}"
        )

    # =========================================================
    # 5. VIEW HIDE / SHOW CONTRACT
    # =========================================================

    print("\n[5] VIEW HIDE / SHOW CONTRACT")
    print("-" * 72)

    navigation_contract = {}

    for name in [
        "showProjectLanding",
        "showWorkspaceHome",
        "showAnalysisWorkspace",
        "showResearchOverview",
    ]:

        function = functions[name]

        if not function:
            continue

        contract = {}

        for view_id in view_ids:

            hide_pattern = (
                rf'{re.escape(view_id)}'
                r'.*?classList\.add\("hidden"\)'
            )

            show_pattern = (
                rf'{re.escape(view_id)}'
                r'.*?classList\.remove\("hidden"\)'
            )

            contract[view_id] = {
                "hide_reference":
                    bool(
                        re.search(
                            hide_pattern,
                            function,
                            re.DOTALL,
                        )
                    ),
                "show_reference":
                    bool(
                        re.search(
                            show_pattern,
                            function,
                            re.DOTALL,
                        )
                    ),
            }

        navigation_contract[name] = contract

        print(f"\n{name}")

        for view_id, result in contract.items():

            hide = (
                "HIDE"
                if result["hide_reference"]
                else "-"
            )

            show = (
                "SHOW"
                if result["show_reference"]
                else "-"
            )

            print(
                f"  {view_id:26} "
                f"{hide:4} {show:4}"
            )

    # =========================================================
    # 6. APPLICATION VIEW STATE
    # =========================================================

    print("\n[6] APPLICATION VIEW STATE")
    print("-" * 72)

    apply_function = functions[
        "applyApplicationViewState"
    ]

    if apply_function:

        print(
            apply_function
        )

    else:

        print(
            "applyApplicationViewState "
            "FUNCTION NOT FOUND"
        )

    view_state_classes = [
        "app-view-landing",
        "app-view-workspace",
        "app-view-analysis",
        "app-view-research",
    ]

    view_state_presence = {}

    for value in view_state_classes:

        present = (
            f'"{value}"'
            in app_text
        )

        view_state_presence[value] = present

        print(
            f"{value:28} "
            f"{'PRESENT' if present else 'MISSING'}"
        )

    # =========================================================
    # 7. HIDDEN CSS CONTRACT
    # =========================================================

    print("\n[7] HIDDEN CSS CONTRACT")
    print("-" * 72)

    hidden_rule = extract_css_rule(
        style_text,
        ".hidden"
    )

    dashboard_rule = extract_css_rule(
        style_text,
        ".dashboard-shell"
    )

    project_view_rule = extract_css_rule(
        style_text,
        ".project-view"
    )

    research_rule = extract_css_rule(
        style_text,
        "body.app-view-research"
    )

    rules = {
        ".hidden":
            hidden_rule,
        ".dashboard-shell":
            dashboard_rule,
        ".project-view":
            project_view_rule,
        "body.app-view-research":
            research_rule,
    }

    for selector, rule in rules.items():

        print(f"\n{selector}")

        if rule:
            print(rule)
        else:
            print("NOT FOUND")

    hidden_important = bool(
        hidden_rule
        and "display: none !important"
        in hidden_rule
    )

    dashboard_display = (
        "display:"
        in dashboard_rule
        if dashboard_rule
        else False
    )

    dashboard_display_important = bool(
        dashboard_rule
        and "display:"
        in dashboard_rule
        and "!important"
        in dashboard_rule
    )

    # =========================================================
    # 8. ANALYSIS / RESEARCH CSS INTERACTION
    # =========================================================

    print(
        "\n[8] ANALYSIS / RESEARCH CSS INTERACTION"
    )
    print("-" * 72)

    interaction_selectors = [
        ".dashboard-shell",
        ".dashboard-shell.hidden",
        "main.dashboard-shell",
        ".analysis-workspace",
        ".research-overview",
        ".project-view",
        ".project-view.hidden",
        "body.app-view-research .dashboard-shell",
        "body.app-view-research #analysis-workspace",
    ]

    interaction_rules = {}

    for selector in interaction_selectors:

        rule = extract_css_rule(
            style_text,
            selector
        )

        interaction_rules[selector] = rule

        print(f"\n{selector}")

        if rule:
            print(rule)
        else:
            print("NOT FOUND")

    # =========================================================
    # 9. NAVIGATION FAILURE ANALYSIS
    # =========================================================

    print(
        "\n[9] NAVIGATION FAILURE ANALYSIS"
    )
    print("-" * 72)

    analysis_function = functions[
        "showAnalysisWorkspace"
    ]

    research_function = functions[
        "showResearchOverview"
    ]

    research_hidden_by_analysis = (
        bool(
            analysis_function
            and
            re.search(
                r'research-overview.*?'
                r'classList\.add\("hidden"\)',
                analysis_function,
                re.DOTALL,
            )
        )
    )

    analysis_hidden_by_research = (
        bool(
            research_function
            and
            re.search(
                r'analysis-workspace.*?'
                r'classList\.add\("hidden"\)',
                research_function,
                re.DOTALL,
            )
        )
    )

    print(
        "Research hides Analysis: "
        f"{'YES' if analysis_hidden_by_research else 'NO'}"
    )

    print(
        "Analysis hides Research: "
        f"{'YES' if research_hidden_by_analysis else 'NO'}"
    )

    # =========================================================
    # 10. READ-ONLY INTEGRITY
    # =========================================================

    print(
        "\n[10] READ-ONLY INTEGRITY"
    )
    print("-" * 72)

    hashes_after = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    unchanged = (
        hashes_before
        == hashes_after
    )

    print(
        "index.html unchanged: "
        f"{'PASS' if hashes_before['index.html'] == hashes_after['index.html'] else 'FAIL'}"
    )

    print(
        "app.js unchanged: "
        f"{'PASS' if hashes_before['app.js'] == hashes_after['app.js'] else 'FAIL'}"
    )

    print(
        "style.css unchanged: "
        f"{'PASS' if hashes_before['style.css'] == hashes_after['style.css'] else 'FAIL'}"
    )

    if not unchanged:
        raise RuntimeError(
            "FAIL: read-only audit detected "
            "an unexpected source modification."
        )

    # =========================================================
    # 11. EVIDENCE
    # =========================================================

    evidence = {
        "operation":
            "DEPLOY-OP-070",

        "title":
            "View-State Collision Audit",

        "status":
            "PASS",

        "mode":
            "read-only",

        "view_structure":
            view_structure,

        "dom_order":
            dom_order,

        "navigation_contract":
            navigation_contract,

        "view_state_presence":
            view_state_presence,

        "css_rules":
            rules,

        "interaction_rules":
            interaction_rules,

        "hidden_rule_has_display_none_important":
            hidden_important,

        "dashboard_has_display":
            dashboard_display,

        "dashboard_display_is_important":
            dashboard_display_important,

        "analysis_hides_research":
            research_hidden_by_analysis,

        "research_hides_analysis":
            analysis_hidden_by_research,

        "hashes_before":
            hashes_before,

        "hashes_after":
            hashes_after,

        "modified_files":
            [],
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True
    )

    EVIDENCE.write_text(
        json.dumps(
            evidence,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"\nEVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-070")
    print("STATUS: PASS")
    print("READ-ONLY AUDIT COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
