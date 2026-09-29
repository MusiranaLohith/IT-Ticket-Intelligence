from pathlib import Path
import hashlib
import json
import shutil
import subprocess


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"

APP = FRONTEND / "app.js"
INDEX = FRONTEND / "index.html"
STYLE = FRONTEND / "style.css"

BACKUP = (
    FRONTEND
    / "app.js.before-deploy-op071"
)

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

EVIDENCE = (
    METRICS
    / "deploy_op071_navigation_state_isolation.json"
)


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def replace_once(
    source,
    old,
    new,
    label,
):
    count = source.count(old)

    if count != 1:
        raise RuntimeError(
            f"FAIL: expected exactly one "
            f"match for {label}, found {count}."
        )

    return source.replace(
        old,
        new,
        1,
    )


def main():

    print("=" * 72)
    print(
        "DEPLOY-OP-071 — NAVIGATION STATE ISOLATION"
    )
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in [
        APP,
        INDEX,
        STYLE,
    ]:

        if not path.exists():
            raise RuntimeError(
                f"BLOCKED: missing source: {path}"
            )

        print(
            f"FOUND: {path}"
        )

    app_before = APP.read_text(
        encoding="utf-8"
    )

    index_before = INDEX.read_text(
        encoding="utf-8"
    )

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    hashes_before = {
        "app.js": sha256(APP),
        "index.html": sha256(INDEX),
        "style.css": sha256(STYLE),
    }

    # =========================================================
    # 2. PRECONDITIONS
    # =========================================================

    print("\n[2] PRECONDITIONS")
    print("-" * 72)

    required_markers = [
        "function showProjectLanding()",
        "function showWorkspaceHome()",
        "function showAnalysisWorkspace(",
        "function showResearchOverview()",
        "function applyApplicationViewState(view)",
        '"app-view-landing"',
        '"app-view-workspace"',
        '"app-view-analysis"',
        '"app-view-research"',
        '"research-overview"',
        '"analysis-workspace"',
    ]

    for marker in required_markers:

        if marker not in app_before:
            raise RuntimeError(
                "FAIL: required navigation marker "
                f"missing: {marker}"
            )

        print(
            f"{marker:<45} PASS"
        )

    # =========================================================
    # 3. BACKUP
    # =========================================================

    print("\n[3] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        if sha256(BACKUP) != sha256(APP):

            raise RuntimeError(
                "FAIL: existing OP-071 backup "
                "does not match current app.js."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            APP,
            BACKUP,
        )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 4. APPLY VIEW-STATE FIX
    # =========================================================

    print("\n[4] VIEW-STATE FIX")
    print("-" * 72)

    app_after = app_before

    def extract_function(text, name):

        marker = f"function {name}("

        start_index = text.find(marker)

        if start_index == -1:
            raise RuntimeError(
                f"FAIL: function not found: {name}"
            )

        brace_start = text.find(
            "{",
            start_index
        )

        if brace_start == -1:
            raise RuntimeError(
                f"FAIL: function body not found: {name}"
            )

        depth = 0

        for index in range(
            brace_start,
            len(text)
        ):

            if text[index] == "{":
                depth += 1

            elif text[index] == "}":
                depth -= 1

                if depth == 0:
                    return (
                        start_index,
                        index + 1,
                        text[
                            start_index:index + 1
                        ],
                    )

        raise RuntimeError(
            f"FAIL: unmatched braces in function: {name}"
        )


    def replace_function(
        text,
        name,
        transform,
    ):

        start_index, end_index, function = (
            extract_function(
                text,
                name,
            )
        )

        updated = transform(
            function
        )

        if updated == function:
            raise RuntimeError(
                f"FAIL: no change produced for {name}"
            )

        return (
            text[:start_index]
            + updated
            + text[end_index:]
        )


    # ---------------------------------------------------------
    # 4A. applyApplicationViewState()
    # ---------------------------------------------------------

    def update_view_state(function):

        old = '''function applyApplicationViewState(view) {
    document.body.classList.remove(
        "app-view-landing",
        "app-view-workspace",
        "app-view-analysis"
    );

    document.body.classList.add(view);
}'''

        new = '''function applyApplicationViewState(view) {
    document.body.classList.remove(
        "app-view-landing",
        "app-view-workspace",
        "app-view-analysis",
        "app-view-research"
    );

    document.body.classList.add(view);
}'''

        if function != old:
            raise RuntimeError(
                "FAIL: unexpected "
                "applyApplicationViewState() "
                "contract."
            )

        return new


    app_after = replace_function(
        app_after,
        "applyApplicationViewState",
        update_view_state,
    )

    print(
        "RESEARCH VIEW STATE ADDED TO STATE RESET: PASS"
    )


    # ---------------------------------------------------------
    # 4B. showProjectLanding()
    # ---------------------------------------------------------

    def update_landing(function):

        old_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );'''

        new_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );'''

        if function.count(old_reference) != 1:
            raise RuntimeError(
                "FAIL: showProjectLanding() analysis "
                "reference contract mismatch."
            )

        function = function.replace(
            old_reference,
            new_reference,
            1,
        )

        old_guard = '''    if (!landing || !home || !analysis) {
        return;
    }'''

        new_guard = '''    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }'''

        if function.count(old_guard) != 1:
            raise RuntimeError(
                "FAIL: showProjectLanding() guard "
                "contract mismatch."
            )

        function = function.replace(
            old_guard,
            new_guard,
            1,
        )

        old_visibility = '''    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");'''

        new_visibility = '''    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");
    research.classList.add("hidden");'''

        if function.count(old_visibility) != 1:
            raise RuntimeError(
                "FAIL: showProjectLanding() visibility "
                "contract mismatch."
            )

        function = function.replace(
            old_visibility,
            new_visibility,
            1,
        )

        return function


    app_after = replace_function(
        app_after,
        "showProjectLanding",
        update_landing,
    )

    print(
        "PROJECT LANDING ISOLATION: PASS"
    )


    # ---------------------------------------------------------
    # 4C. showWorkspaceHome()
    # ---------------------------------------------------------

    def update_workspace(function):

        old_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );'''

        new_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );'''

        if function.count(old_reference) != 1:
            raise RuntimeError(
                "FAIL: showWorkspaceHome() analysis "
                "reference contract mismatch."
            )

        function = function.replace(
            old_reference,
            new_reference,
            1,
        )

        old_guard = '''    if (!landing || !home || !analysis) {
        return;
    }'''

        new_guard = '''    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }'''

        if function.count(old_guard) != 1:
            raise RuntimeError(
                "FAIL: showWorkspaceHome() guard "
                "contract mismatch."
            )

        function = function.replace(
            old_guard,
            new_guard,
            1,
        )

        old_visibility = '''    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");'''

        new_visibility = '''    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");
    research.classList.add("hidden");'''

        if function.count(old_visibility) != 1:
            raise RuntimeError(
                "FAIL: showWorkspaceHome() visibility "
                "contract mismatch."
            )

        function = function.replace(
            old_visibility,
            new_visibility,
            1,
        )

        return function


    app_after = replace_function(
        app_after,
        "showWorkspaceHome",
        update_workspace,
    )

    print(
        "WORKSPACE HOME ISOLATION: PASS"
    )


    # ---------------------------------------------------------
    # 4D. showAnalysisWorkspace()
    # ---------------------------------------------------------

    def update_analysis(function):

        old_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );'''

        new_reference = '''    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );'''

        if function.count(old_reference) != 1:
            raise RuntimeError(
                "FAIL: showAnalysisWorkspace() analysis "
                "reference contract mismatch."
            )

        function = function.replace(
            old_reference,
            new_reference,
            1,
        )

        old_guard = '''    if (!landing || !home || !analysis) {
        return;
    }'''

        new_guard = '''    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }'''

        if function.count(old_guard) != 1:
            raise RuntimeError(
                "FAIL: showAnalysisWorkspace() guard "
                "contract mismatch."
            )

        function = function.replace(
            old_guard,
            new_guard,
            1,
        )

        old_visibility = '''    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");'''

        new_visibility = '''    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");
    research.classList.add("hidden");'''

        if function.count(old_visibility) != 1:
            raise RuntimeError(
                "FAIL: showAnalysisWorkspace() visibility "
                "contract mismatch."
            )

        function = function.replace(
            old_visibility,
            new_visibility,
            1,
        )

        return function


    app_after = replace_function(
        app_after,
        "showAnalysisWorkspace",
        update_analysis,
    )

    print(
        "ANALYSIS WORKSPACE ISOLATION: PASS"
    )

    # =========================================================
    # 5. FINAL SAFETY CHECKS BEFORE WRITE
    # =========================================================

    print("\n[5] PRE-WRITE SAFETY")
    print("-" * 72)

    safety_checks = {
        "RESEARCH_STATE_RESET":
            '"app-view-research"'
            in app_after,

        "ANALYSIS_HIDES_RESEARCH":
            (
                'research.classList.add("hidden")'
                in app_after
            ),

        "RESEARCH_FUNCTION_PRESERVED":
            "function showResearchOverview()"
            in app_after,

        "SINGLE_API_PRESERVED":
            "/tickets/analyze"
            in app_after,

        "BATCH_API_PRESERVED":
            "/tickets/analyze-batch"
            in app_after,

        "BATCH_SELECTION_PRESERVED":
            "selectBatchTicket"
            in app_after,

        "DETAIL_RENDERER_PRESERVED":
            "renderAnalysisResponse"
            in app_after,

        "TICKET_PIPELINE_ABSENT":
            "TicketPipeline"
            not in app_after,

        "SKLEARN_ABSENT":
            "sklearn"
            not in app_after,

        "PREDICT_BATCH_ABSENT":
            "predict_batch("
            not in app_after,
    }

    for name, passed in safety_checks.items():

        print(
            f"{name:<38}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(safety_checks.values()):

        raise RuntimeError(
            "FAIL: pre-write safety validation failed."
        )

    # =========================================================
    # 6. WRITE ONLY APP.JS
    # =========================================================

    APP.write_text(
        app_after,
        encoding="utf-8"
    )

    print("\n[6] SOURCE WRITE")
    print("-" * 72)

    print(
        "APP.JS UPDATED:                   TRUE"
    )

    print(
        "INDEX.HTML MODIFIED:              FALSE"
    )

    print(
        "STYLE.CSS MODIFIED:               FALSE"
    )

    # =========================================================
    # 7. JAVASCRIPT SYNTAX
    # =========================================================

    print("\n[7] JAVASCRIPT SYNTAX")
    print("-" * 72)

    syntax_result = subprocess.run(
        [
            "node",
            "--check",
            str(APP),
        ],
        capture_output=True,
        text=True,
    )

    if syntax_result.returncode != 0:

        print(
            syntax_result.stdout
        )

        print(
            syntax_result.stderr
        )

        shutil.copy2(
            BACKUP,
            APP,
        )

        raise RuntimeError(
            "FAIL: node --check failed. "
            "app.js automatically restored."
        )

    print(
        "NODE --CHECK:                    PASS"
    )

    # =========================================================
    # 8. POST-WRITE CONTRACT
    # =========================================================

    print("\n[8] POST-WRITE CONTRACT")
    print("-" * 72)

    final_app = APP.read_text(
        encoding="utf-8"
    )

    final_checks = {

        "STATE_RESET_INCLUDES_RESEARCH":
            (
                '"app-view-research"'
                in final_app
            ),

        "ANALYSIS_HIDES_RESEARCH":
            (
                'research.classList.add("hidden")'
                in final_app
            ),

        "LANDING_STATE_APPLIED":
            (
                '"app-view-landing"'
                in final_app
            ),

        "WORKSPACE_STATE_APPLIED":
            (
                '"app-view-workspace"'
                in final_app
            ),

        "ANALYSIS_STATE_APPLIED":
            (
                '"app-view-analysis"'
                in final_app
            ),

        "RESEARCH_STATE_APPLIED":
            (
                '"app-view-research"'
                in final_app
            ),

        "SINGLE_API_PRESERVED":
            "/tickets/analyze"
            in final_app,

        "BATCH_API_PRESERVED":
            "/tickets/analyze-batch"
            in final_app,

        "BATCH_SELECTION_PRESERVED":
            "selectBatchTicket"
            in final_app,

        "DETAIL_RENDERER_PRESERVED":
            "renderAnalysisResponse"
            in final_app,

        "TICKET_PIPELINE_ABSENT":
            "TicketPipeline"
            not in final_app,

        "SKLEARN_ABSENT":
            "sklearn"
            not in final_app,

        "PREDICT_BATCH_ABSENT":
            "predict_batch("
            not in final_app,

        "INDEX_UNCHANGED":
            sha256(INDEX)
            == hashes_before["index.html"],

        "STYLE_UNCHANGED":
            sha256(STYLE)
            == hashes_before["style.css"],
    }

    for name, passed in final_checks.items():

        print(
            f"{name:<38}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(final_checks.values()):

        shutil.copy2(
            BACKUP,
            APP,
        )

        raise RuntimeError(
            "FAIL: final validation failed. "
            "app.js automatically restored."
        )

    # =========================================================
    # 9. EVIDENCE
    # =========================================================

    hashes_after = {
        "app.js": sha256(APP),
        "index.html": sha256(INDEX),
        "style.css": sha256(STYLE),
    }

    evidence = {
        "operation":
            "DEPLOY-OP-071",

        "title":
            "Navigation State Isolation",

        "status":
            "PASS",

        "purpose":
            (
                "Make landing, workspace, analysis and "
                "research views mutually exclusive."
            ),

        "modified_files": [
            str(APP),
        ],

        "unmodified_files": [
            str(INDEX),
            str(STYLE),
        ],

        "backup":
            str(BACKUP),

        "checks":
            final_checks,

        "hashes_before":
            hashes_before,

        "hashes_after":
            hashes_after,

        "frozen_runtime_modified":
            False,

        "backend_modified":
            False,

        "model_artifacts_modified":
            False,
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

    print("\n[9] EVIDENCE")
    print("-" * 72)

    print(
        f"EVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 72)
    print(
        "DEPLOY-OP-071"
    )
    print(
        "STATUS: PASS"
    )
    print(
        "NAVIGATION STATE ISOLATION COMPLETE"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
