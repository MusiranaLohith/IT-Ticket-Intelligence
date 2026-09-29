from pathlib import Path
from hashlib import sha256
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

APP_BACKUP = (
    FRONTEND
    / "app.js.before-deploy-op056"
)

STYLE_BACKUP = (
    FRONTEND
    / "style.css.before-deploy-op056"
)

MARKER = "DEPLOY-OP-056 — FIXED VIEWPORT HOME + WORKSPACE NAVIGATION"


def sha256(path):
    return sha256_bytes(path.read_bytes())


def sha256_bytes(data):
    return __import__("hashlib").sha256(data).hexdigest()


def backup_or_verify(source, backup):
    if backup.exists():
        if backup.read_bytes() != source.read_bytes():
            raise RuntimeError(
                f"FAIL: existing backup differs from current source: {backup}"
            )

        print(f"BACKUP REUSED AND VERIFIED: {backup}")
        return

    shutil.copy2(source, backup)

    print(f"BACKUP CREATED: {backup}")


def require_once(text, marker, name):
    count = text.count(marker)

    if count != 1:
        raise RuntimeError(
            f"FAIL: expected exactly one {name}, found {count}"
        )


def main():
    print("=" * 72)
    print(MARKER)
    print("=" * 72)

    # =========================================================
    # SOURCE CONTRACT
    # =========================================================

    for path in (APP, STYLE):
        if not path.exists():
            raise SystemExit(
                f"BLOCKED: required frontend file missing: {path}"
            )

    app_before = APP.read_text(encoding="utf-8")
    style_before = STYLE.read_text(encoding="utf-8")

    hashes_before = {
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    required_app_markers = [
        "function showProjectLanding",
        "function showWorkspaceHome",
        "function showAnalysisWorkspace",
        'id',
        "viewResearchButton",
        "project-research-strip",
        "workspaceHomeButton",
    ]

    for marker in required_app_markers:
        present = marker in app_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required app.js marker missing: {marker}"
            )

    required_style_markers = [
        ".project-landing",
        ".project-landing-inner",
        ".workspace-home",
        ".workspace-home-inner",
    ]

    for marker in required_style_markers:
        present = marker in style_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required style.css marker missing: {marker}"
            )

    if MARKER in app_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-056 already present in app.js."
        )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-056 already present in style.css."
        )

    # =========================================================
    # BACKUPS
    # =========================================================

    print("\n[2] BACKUPS")
    print("-" * 72)

    backup_or_verify(APP, APP_BACKUP)
    backup_or_verify(STYLE, STYLE_BACKUP)

    # =========================================================
    # APP.JS
    # =========================================================

    app_after = app_before

    # ---------------------------------------------------------
    # Remove scrollIntoView() behaviour from VIEW RESEARCH.
    # Replace it with a non-scrolling visual focus.
    # ---------------------------------------------------------

    old_view_research = r'''    if (viewResearchButton) {
        viewResearchButton.addEventListener(
            "click",
            () => {
                const strip =
                    document.getElementById(
                        "project-research-strip"
                    );

                if (strip) {
                    strip.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });
                }
            }
        );
    }'''

    new_view_research = r'''    if (viewResearchButton) {
        viewResearchButton.addEventListener(
            "click",
            () => {
                const strip =
                    document.getElementById(
                        "project-research-strip"
                    );

                if (!strip) {
                    return;
                }

                strip.classList.remove(
                    "research-focus-pulse"
                );

                void strip.offsetWidth;

                strip.classList.add(
                    "research-focus-pulse"
                );

                window.setTimeout(() => {
                    strip.classList.remove(
                        "research-focus-pulse"
                    );
                }, 900);
            }
        );
    }'''

    require_once(
        app_after,
        old_view_research,
        "existing VIEW RESEARCH handler",
    )

    app_after = app_after.replace(
        old_view_research,
        new_view_research,
        1,
    )

    # ---------------------------------------------------------
    # Add viewport state classes.
    # ---------------------------------------------------------

    app_after = app_after.replace(
        'function showProjectLanding() {',
        '''/* ============================================================
   DEPLOY-OP-056 — FIXED VIEWPORT HOME + WORKSPACE NAVIGATION
   ------------------------------------------------------------
   Home and Research Workspace behave as fixed application views.
   Analysis Workspace retains normal document scrolling.
   ============================================================ */

function applyApplicationViewState(view) {
    document.body.classList.remove(
        "app-view-landing",
        "app-view-workspace",
        "app-view-analysis"
    );

    document.body.classList.add(view);
}


function showProjectLanding() {''',
        1,
    )

    # ---------------------------------------------------------
    # Landing view state.
    # ---------------------------------------------------------

    landing_old = '''    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });'''

    landing_new = '''    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");

    applyApplicationViewState(
        "app-view-landing"
    );'''

    require_once(
        app_after,
        landing_old,
        "showProjectLanding viewport block",
    )

    app_after = app_after.replace(
        landing_old,
        landing_new,
        1,
    )

    # ---------------------------------------------------------
    # Workspace view state.
    # ---------------------------------------------------------

    workspace_old = '''    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });'''

    workspace_new = '''    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");

    applyApplicationViewState(
        "app-view-workspace"
    );'''

    require_once(
        app_after,
        workspace_old,
        "showWorkspaceHome viewport block",
    )

    app_after = app_after.replace(
        workspace_old,
        workspace_new,
        1,
    )

    # ---------------------------------------------------------
    # Analysis state.
    # ---------------------------------------------------------

    analysis_old = '''    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });'''

    analysis_new = '''    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");

    applyApplicationViewState(
        "app-view-analysis"
    );

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });'''

    require_once(
        app_after,
        analysis_old,
        "showAnalysisWorkspace viewport block",
    )

    app_after = app_after.replace(
        analysis_old,
        analysis_new,
        1,
    )

    # ---------------------------------------------------------
    # Final JS marker.
    # ---------------------------------------------------------

    app_after += r'''

/* ============================================================
   END DEPLOY-OP-056
   ============================================================ */
'''

    # =========================================================
    # STYLE.CSS
    # =========================================================

    fixed_view_css = r'''

/* ============================================================
   DEPLOY-OP-056 — FIXED VIEWPORT HOME + WORKSPACE NAVIGATION
   ------------------------------------------------------------
   Home and Research Workspace are application-level views.
   They occupy the viewport below the fixed top navigation.
   Analysis Workspace keeps normal document scrolling.
   ============================================================ */

html,
body {
    min-height: 100%;
}


/* ------------------------------------------------------------
   HOME VIEW
   ------------------------------------------------------------ */

body.app-view-landing {
    overflow: hidden !important;
}

body.app-view-landing .project-landing {
    height: calc(100dvh - 80px);
    min-height: calc(100dvh - 80px);
    max-height: calc(100dvh - 80px);

    overflow: hidden;

    box-sizing: border-box;
}


/* ------------------------------------------------------------
   RESEARCH WORKSPACE VIEW
   ------------------------------------------------------------ */

body.app-view-workspace {
    overflow: hidden !important;
}

body.app-view-workspace .workspace-home {
    height: calc(100dvh - 80px);
    min-height: calc(100dvh - 80px);
    max-height: calc(100dvh - 80px);

    overflow: hidden;

    box-sizing: border-box;
}

body.app-view-workspace .workspace-home-inner {
    height: 100%;
    max-height: 100%;

    box-sizing: border-box;

    display: flex;
    flex-direction: column;
}

body.app-view-workspace .workspace-heading {
    flex: 0 0 auto;
}

body.app-view-workspace .workspace-entry-grid {
    flex: 0 0 auto;
}

body.app-view-workspace .workspace-entry {
    min-height: 0;
}

body.app-view-workspace .workspace-entry-shared-action {
    flex: 0 0 auto;
}

body.app-view-workspace .workspace-information-grid {
    flex: 0 0 auto;

    margin-top: auto;
}


/* ------------------------------------------------------------
   VIEW RESEARCH NON-SCROLLING FEEDBACK
   ------------------------------------------------------------ */

.research-focus-pulse {
    animation: deployOp056ResearchFocus 900ms ease-out;
}

@keyframes deployOp056ResearchFocus {
    0% {
        box-shadow:
            0 0 0 0 rgba(37, 99, 235, 0.00);
    }

    30% {
        box-shadow:
            0 0 0 5px rgba(37, 99, 235, 0.20),
            0 18px 45px rgba(15, 23, 42, 0.12);
    }

    100% {
        box-shadow:
            0 0 0 0 rgba(37, 99, 235, 0.00);
    }
}


/* ------------------------------------------------------------
   ANALYSIS VIEW
   ------------------------------------------------------------ */

body.app-view-analysis {
    overflow-x: hidden;
    overflow-y: auto;
}


/* ------------------------------------------------------------
   RESPONSIVE VIEWPORT HANDLING
   ------------------------------------------------------------ */

@media (max-width: 900px) {

    body.app-view-landing .project-landing,
    body.app-view-workspace .workspace-home {
        height: calc(100dvh - 80px);
        min-height: calc(100dvh - 80px);
        max-height: calc(100dvh - 80px);
    }
}


@media (max-width: 620px) {

    body.app-view-landing .project-landing,
    body.app-view-workspace .workspace-home {
        height: calc(100dvh - 70px);
        min-height: calc(100dvh - 70px);
        max-height: calc(100dvh - 70px);
    }

    body.app-view-workspace .workspace-home-inner {
        overflow: hidden;
    }
}


/* ============================================================
   END DEPLOY-OP-056
   ============================================================ */
'''

    style_after = style_before + fixed_view_css

    # =========================================================
    # WRITE
    # =========================================================

    print("\n[3] WRITING FRONTEND CHANGES")
    print("-" * 72)

    APP.write_text(
        app_after,
        encoding="utf-8",
    )

    STYLE.write_text(
        style_after,
        encoding="utf-8",
    )

    print(f"UPDATED: {APP}")
    print(f"UPDATED: {STYLE}")

    # =========================================================
    # POST-WRITE VALIDATION
    # =========================================================

    final_app = APP.read_text(encoding="utf-8")
    final_style = STYLE.read_text(encoding="utf-8")

    checks = {
        "OP056_MARKER_APP":
            MARKER in final_app,

        "OP056_MARKER_STYLE":
            MARKER in final_style,

        "VIEW_RESEARCH_SCROLL_REMOVED":
            "strip.scrollIntoView" not in final_app,

        "VIEW_RESEARCH_HANDLER_PRESENT":
            "research-focus-pulse" in final_app,

        "VIEWPORT_STATE_FUNCTION":
            "function applyApplicationViewState" in final_app,

        "LANDING_VIEW_STATE":
            '"app-view-landing"' in final_app,

        "WORKSPACE_VIEW_STATE":
            '"app-view-workspace"' in final_app,

        "ANALYSIS_VIEW_STATE":
            '"app-view-analysis"' in final_app,

        "LANDING_FIXED_VIEW":
            "body.app-view-landing .project-landing"
            in final_style,

        "WORKSPACE_FIXED_VIEW":
            "body.app-view-workspace .workspace-home"
            in final_style,

        "LANDING_OVERFLOW_LOCK":
            "body.app-view-landing {\n    overflow: hidden"
            in final_style,

        "WORKSPACE_OVERFLOW_LOCK":
            "body.app-view-workspace {\n    overflow: hidden"
            in final_style,

        "ANALYSIS_SCROLL_PRESERVED":
            "body.app-view-analysis {\n    overflow-x: hidden;\n    overflow-y: auto;"
            in final_style,

        "RESEARCH_FOCUS_PRESENT":
            ".research-focus-pulse" in final_style,

        "BACK_TO_HOME_PRESERVED":
            "workspaceHomeButton" in final_app,

        "SHOW_ANALYSIS_PRESERVED":
            "function showAnalysisWorkspace" in final_app,

        "TICKET_PIPELINE_NOT_FRONTEND":
            "TicketPipeline" not in final_app,

        "SKLEARN_NOT_FRONTEND":
            "sklearn" not in final_app.lower(),

        "PREDICT_BATCH_NOT_FRONTEND":
            "predict_batch(" not in final_app,
    }

    print("\n[4] VALIDATION")
    print("-" * 72)

    for name, passed in checks.items():
        print(
            f"{name:42}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):
        print("\nVALIDATION FAILED — RESTORING FILES")

        shutil.copy2(APP_BACKUP, APP)
        shutil.copy2(STYLE_BACKUP, STYLE)

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    # =========================================================
    # HASH VALIDATION
    # =========================================================

    hashes_after = {
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    # =========================================================
    # EVIDENCE
    # =========================================================

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence = {
        "operation": "DEPLOY-OP-056",
        "title": "Fixed Viewport Home and Workspace Navigation",
        "status": "PASS",
        "scope": [
            "fixed home viewport",
            "fixed research workspace viewport",
            "remove VIEW RESEARCH scrollIntoView behaviour",
            "non-scrolling research focus feedback",
            "analysis workspace scrolling preserved",
        ],
        "modified_files": [
            str(APP),
            str(STYLE),
        ],
        "backups": [
            str(APP_BACKUP),
            str(STYLE_BACKUP),
        ],
        "untouched": [
            "deployment/frontend/index.html",
            "deployment/backend/app.py",
            "modeling/FMP/deployment/runtime/ticket_pipeline.py",
            "modeling/FMP/deployment/runtime/ticket_explanation.py",
            "frozen modeling artifacts",
            "T1–T11 runtime semantics",
            "single-ticket analysis logic",
            "batch analysis logic",
        ],
        "checks": checks,
        "hashes_before": hashes_before,
        "hashes_after": hashes_after,
    }

    evidence_path = (
        METRICS
        / "deploy_op056_fixed_viewport_navigation.json"
    )

    evidence_path.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n[5] EVIDENCE")
    print("-" * 72)
    print(f"EVIDENCE_WRITTEN: {evidence_path}")

    print("\n" + "=" * 72)
    print("DEPLOY-OP-056")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
