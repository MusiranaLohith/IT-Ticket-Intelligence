from pathlib import Path
import hashlib
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FRONTEND = ROOT / "deployment" / "frontend"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
CSS = FRONTEND / "style.css"

METRICS = ROOT / "modeling" / "FMP" / "metrics"
EVIDENCE = METRICS / "deploy_op047_information_architecture.json"

MARKER = "DEPLOY-OP-047"


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


for path in (INDEX, APP, CSS):
    if not path.exists():
        raise SystemExit(
            f"FAIL: required frontend file is missing: {path}"
        )


index_before = sha256(INDEX)
app_before = sha256(APP)
css_before = sha256(CSS)

index_text = INDEX.read_text(encoding="utf-8")
app_text = APP.read_text(encoding="utf-8")
css_text = CSS.read_text(encoding="utf-8")


# ============================================================
# SAFETY CONTRACT
# ============================================================

required_index_markers = [
    'class="topbar"',
    'id="single-ticket-panel"',
    'id="batch-input-panel"',
    'id="batch-results-panel"',
    'id="results-panel"',
    'id="evidence-content"',
    'id="pipeline-content"',
    'id="human-review-content"',
    'id="limitations-content"',
    'id="explanation-content"',
    'id="reset-dashboard-button"',
    'id="ticket-form"',
    'id="ticket_id"',
    'id="creation_time"',
    'id="creator"',
    'id="creator_detail"',
    'id="summary"',
    'id="description"',
    'id="batch-file"',
    'id="batch-validate-button"',
    'id="batch-results-table"',
    'id="batch-results-table-body"',
]

missing = [
    marker
    for marker in required_index_markers
    if marker not in index_text
]

if missing:
    raise SystemExit(
        "FAIL: current index.html does not match the known "
        "deployment structure.\nMissing:\n"
        + "\n".join(f"  - {item}" for item in missing)
    )


required_app_markers = [
    "/tickets/analyze",
    "/tickets/analyze-batch",
    "selectBatchTicket",
    "renderAnalysisResponse",
]

for marker in required_app_markers:
    if marker not in app_text:
        raise SystemExit(
            f"FAIL: expected app.js marker is missing: {marker}"
        )


if "TicketPipeline" in app_text:
    raise SystemExit(
        "FAIL: TicketPipeline reference detected directly "
        "in frontend app.js."
    )


if "sklearn" in app_text.lower():
    raise SystemExit(
        "FAIL: sklearn reference detected in frontend app.js."
    )


# ============================================================
# PREVENT DOUBLE APPLICATION
# ============================================================

if MARKER in index_text:
    raise SystemExit(
        "FAIL: DEPLOY-OP-047 is already present in index.html."
    )

if MARKER in app_text:
    raise SystemExit(
        "FAIL: DEPLOY-OP-047 is already present in app.js."
    )

if MARKER in css_text:
    raise SystemExit(
        "FAIL: DEPLOY-OP-047 is already present in style.css."
    )


# ============================================================
# BACKUPS
# ============================================================

index_backup = FRONTEND / "index.html.before-deploy-op047"
app_backup = FRONTEND / "app.js.before-deploy-op047"
css_backup = FRONTEND / "style.css.before-deploy-op047"


for source, backup in (
    (INDEX, index_backup),
    (APP, app_backup),
    (CSS, css_backup),
):
    if backup.exists():
        raise SystemExit(
            f"FAIL: expected backup path already exists: {backup}"
        )

    backup.write_bytes(source.read_bytes())


# ============================================================
# LANDING PAGE
# ============================================================

landing_html = r'''
<!-- =========================================================
     DEPLOY-OP-047 — PROJECT LANDING
     ========================================================= -->

<section
    id="project-landing"
    class="project-view project-landing"
>

    <div class="project-landing-inner">

        <div class="project-kicker">
            RESEARCH / ENGINEERING SYSTEM
        </div>

        <h1>
            IT Ticket<br>
            <span>Intelligence</span>
        </h1>

        <p class="project-motto">
            Evidence-first ticket triage and human decision support.
        </p>

        <p class="project-introduction">
            A research and engineering system for analysing IT support
            tickets through a traceable T1–T11 evidence pipeline.
            The system combines task-level evidence, historical
            retrieval, duplicate analysis, resolution evidence,
            evidence integration and an explicit human decision boundary.
        </p>


        <div class="project-actions">

            <button
                type="button"
                id="enter-system-button"
                class="project-primary-action"
            >
                ENTER SYSTEM
            </button>

            <button
                type="button"
                id="view-research-button"
                class="project-secondary-action"
            >
                VIEW RESEARCH
            </button>

        </div>


        <div
            id="project-research-strip"
            class="project-research-strip"
        >

            <article class="project-feature">
                <span class="project-feature-index">
                    01
                </span>

                <div>
                    <h3>
                        DATASET INVESTIGATION
                    </h3>

                    <p>
                        Dataset integrity and feasibility were investigated
                        before the deployed analysis workflow was defined.
                    </p>
                </div>
            </article>


            <article class="project-feature">
                <span class="project-feature-index">
                    02
                </span>

                <div>
                    <h3>
                        T1–T11 EVIDENCE CHAIN
                    </h3>

                    <p>
                        Ticket analysis is exposed as a traceable sequence
                        of task-level evidence rather than a single opaque result.
                    </p>
                </div>
            </article>


            <article class="project-feature">
                <span class="project-feature-index">
                    03
                </span>

                <div>
                    <h3>
                        HUMAN DECISION BOUNDARY
                    </h3>

                    <p>
                        The system provides evidence and explicitly preserves
                        human review as the operational decision boundary.
                    </p>
                </div>
            </article>


            <article class="project-feature">
                <span class="project-feature-index">
                    04
                </span>

                <div>
                    <h3>
                        DEPLOYMENT INTEGRITY
                    </h3>

                    <p>
                        The deployment preserves the documented runtime
                        contracts and known evidence limitations.
                    </p>
                </div>
            </article>

        </div>

    </div>

</section>


<!-- =========================================================
     DEPLOY-OP-047 — WORKSPACE HOME
     ========================================================= -->

<section
    id="workspace-home"
    class="project-view workspace-home hidden"
>

    <div class="workspace-home-inner">

        <div class="workspace-heading">

            <div>

                <div class="project-kicker">
                    IT TICKET INTELLIGENCE
                </div>

                <h2>
                    Research Workspace
                </h2>

                <p>
                    Select how you want to investigate ticket data.
                    The same evidence-first T1–T11 pipeline is used
                    for both input modes.
                </p>

            </div>

        </div>


        <div class="workspace-entry-grid">

            <article class="workspace-entry workspace-entry-single">

                <div class="workspace-entry-index">
                    01
                </div>

                <div class="workspace-entry-content">

                    <span class="workspace-entry-label">
                        SINGLE TICKET
                    </span>

                    <h3>
                        Investigate one ticket
                    </h3>

                    <p>
                        Enter one ticket manually and inspect its
                        complete T1–T11 evidence chain.
                    </p>

                    <button
                        type="button"
                        id="open-single-ticket-button"
                        class="workspace-entry-action"
                    >
                        OPEN SINGLE TICKET
                    </button>

                </div>

            </article>


            <article class="workspace-entry workspace-entry-batch">

                <div class="workspace-entry-index">
                    02
                </div>

                <div class="workspace-entry-content">

                    <span class="workspace-entry-label">
                        MULTIPLE TICKETS
                    </span>

                    <h3>
                        Analyse existing ticket data
                    </h3>

                    <p>
                        Upload structured JSON or CSV data and
                        analyse each ticket independently.
                    </p>

                    <button
                        type="button"
                        id="open-batch-analysis-button"
                        class="workspace-entry-action"
                    >
                        OPEN BATCH ANALYSIS
                    </button>

                </div>

            </article>

        </div>


        <div class="workspace-information-grid">

            <article class="workspace-information">

                <span>
                    PIPELINE
                </span>

                <strong>
                    T1–T11
                </strong>

                <p>
                    Traceable task-level evidence.
                </p>

            </article>


            <article class="workspace-information">

                <span>
                    DECISION BOUNDARY
                </span>

                <strong>
                    HUMAN REVIEW
                </strong>

                <p>
                    Operational decisions remain external to the system.
                </p>

            </article>


            <article class="workspace-information">

                <span>
                    RUNTIME
                </span>

                <strong>
                    RESEARCH PROTOTYPE
                </strong>

                <p>
                    Evidence-first deployment with documented limitations.
                </p>

            </article>

        </div>

    </div>

</section>
'''


# ============================================================
# INSERT LANDING + HOME BEFORE ANALYSIS WORKSPACE
# ============================================================

main_marker = '<main class="dashboard-shell">'

if main_marker not in index_text:
    raise SystemExit(
        "FAIL: expected dashboard-shell main element was not found."
    )


index_text = index_text.replace(
    main_marker,
    landing_html
    + "\n\n"
    + main_marker,
    1,
)


# Give the existing analysis main a stable identity.
index_text = index_text.replace(
    '<main class="dashboard-shell">',
    '<main id="analysis-workspace" class="dashboard-shell">',
    1,
)


# Add navigation immediately inside the existing analysis workspace.
analysis_navigation = r'''
    <!-- =========================================================
         DEPLOY-OP-047 — ANALYSIS NAVIGATION
         ========================================================= -->

    <div
        id="analysis-navigation"
        class="analysis-navigation"
    >

        <button
            type="button"
            id="analysis-home-button"
            class="analysis-nav-button"
        >
            WORKSPACE HOME
        </button>

        <button
            type="button"
            id="project-overview-button"
            class="analysis-nav-button"
        >
            PROJECT OVERVIEW
        </button>

    </div>
'''

analysis_marker = (
    '<main id="analysis-workspace" class="dashboard-shell">'
)

index_text = index_text.replace(
    analysis_marker,
    analysis_marker
    + "\n"
    + analysis_navigation,
    1,
)


# ============================================================
# FRONTEND NAVIGATION LOGIC
# ============================================================

navigation_js = r'''

/* ============================================================
   DEPLOY-OP-047 — PROJECT INFORMATION ARCHITECTURE
   ------------------------------------------------------------
   Navigation only.
   Does not modify ticket analysis, batch processing,
   rendering, pipeline logic, API calls, or model behaviour.
   ============================================================ */

function showProjectLanding() {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    if (!landing || !home || !analysis) {
        return;
    }

    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showWorkspaceHome() {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    if (!landing || !home || !analysis) {
        return;
    }

    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showAnalysisWorkspace(targetId = null) {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    if (!landing || !home || !analysis) {
        return;
    }

    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    if (targetId) {
        window.setTimeout(() => {
            const target =
                document.getElementById(targetId);

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }, 120);
    }
}


function initializeProjectNavigation() {
    const enterSystemButton =
        document.getElementById(
            "enter-system-button"
        );

    const viewResearchButton =
        document.getElementById(
            "view-research-button"
        );

    const openSingleButton =
        document.getElementById(
            "open-single-ticket-button"
        );

    const openBatchButton =
        document.getElementById(
            "open-batch-analysis-button"
        );

    const analysisHomeButton =
        document.getElementById(
            "analysis-home-button"
        );

    const projectOverviewButton =
        document.getElementById(
            "project-overview-button"
        );

    const resetDashboardButton =
        document.getElementById(
            "reset-dashboard-button"
        );


    if (enterSystemButton) {
        enterSystemButton.addEventListener(
            "click",
            showWorkspaceHome
        );
    }


    if (viewResearchButton) {
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
    }


    if (openSingleButton) {
        openSingleButton.addEventListener(
            "click",
            () => {
                showAnalysisWorkspace(
                    "single-ticket-panel"
                );
            }
        );
    }


    if (openBatchButton) {
        openBatchButton.addEventListener(
            "click",
            () => {
                showAnalysisWorkspace(
                    "batch-input-panel"
                );
            }
        );
    }


    if (analysisHomeButton) {
        analysisHomeButton.addEventListener(
            "click",
            showWorkspaceHome
        );
    }


    if (projectOverviewButton) {
        projectOverviewButton.addEventListener(
            "click",
            showProjectLanding
        );
    }


    if (resetDashboardButton) {
        resetDashboardButton.addEventListener(
            "click",
            () => {
                window.setTimeout(
                    showWorkspaceHome,
                    50
                );
            }
        );
    }


    showProjectLanding();
}


initializeProjectNavigation();
'''


app_text += navigation_js


# ============================================================
# INFORMATION-ARCHITECTURE CSS
# ============================================================

navigation_css = r'''

/* ============================================================
   DEPLOY-OP-047 — INFORMATION ARCHITECTURE
   ------------------------------------------------------------
   Structural presentation only.
   Final visual identity will be designed separately.
   ============================================================ */

.project-view {
    width: min(
        1180px,
        calc(100% - 48px)
    );

    margin: 0 auto;
}

.project-landing {
    min-height: calc(100vh - 150px);

    display: flex;
    align-items: center;

    padding: 70px 0 90px;
}

.project-landing-inner {
    width: 100%;
}

.project-kicker {
    margin-bottom: 18px;

    font-size: 0.72rem;
    font-weight: 850;

    letter-spacing: 0.18em;
}

.project-landing h1 {
    max-width: 900px;

    margin: 0;

    font-size: clamp(
        3.5rem,
        8vw,
        7rem
    );

    line-height: 0.94;
    letter-spacing: -0.055em;
}

.project-landing h1 span {
    opacity: 0.58;
}

.project-motto {
    max-width: 760px;

    margin: 30px 0 0;

    font-size: clamp(
        1.15rem,
        2vw,
        1.55rem
    );

    font-weight: 700;

    line-height: 1.45;
}

.project-introduction {
    max-width: 760px;

    margin: 18px 0 0;

    font-size: 1rem;
    line-height: 1.75;
}


.project-actions {
    display: flex;
    flex-wrap: wrap;

    gap: 12px;

    margin-top: 34px;
}


.project-primary-action,
.project-secondary-action,
.workspace-entry-action,
.analysis-nav-button {
    cursor: pointer;

    font-family: inherit;
}


.project-research-strip {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 1px;

    margin-top: 70px;

    border-top: 1px solid currentColor;
    border-bottom: 1px solid currentColor;
}


.project-feature {
    display: grid;

    grid-template-columns: auto 1fr;

    gap: 16px;

    min-height: 170px;

    padding: 24px 20px;

    border-right: 1px solid currentColor;
}

.project-feature:last-child {
    border-right: 0;
}

.project-feature-index,
.workspace-entry-index {
    font-size: 0.72rem;
    font-weight: 850;
    letter-spacing: 0.12em;
}

.project-feature h3 {
    margin: 0;

    font-size: 0.78rem;
    font-weight: 900;

    letter-spacing: 0.08em;
}

.project-feature p {
    margin: 12px 0 0;

    font-size: 0.84rem;
    line-height: 1.6;
}


.workspace-home {
    min-height: calc(100vh - 150px);

    padding: 72px 0 90px;
}

.workspace-heading {
    display: flex;

    justify-content: space-between;
    align-items: flex-end;

    padding-bottom: 30px;

    border-bottom: 1px solid currentColor;
}

.workspace-heading h2 {
    margin: 0;

    font-size: clamp(
        2.5rem,
        5vw,
        4.5rem
    );

    line-height: 0.98;
    letter-spacing: -0.045em;
}

.workspace-heading p {
    max-width: 600px;

    margin: 16px 0 0;

    line-height: 1.65;
}


.workspace-entry-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 18px;

    margin-top: 32px;
}


.workspace-entry {
    position: relative;

    min-height: 330px;

    display: grid;

    grid-template-columns: auto 1fr;

    gap: 22px;

    padding: 32px;

    border: 1px solid currentColor;

    overflow: hidden;
}

.workspace-entry-content {
    align-self: end;
}

.workspace-entry-label {
    font-size: 0.72rem;
    font-weight: 900;

    letter-spacing: 0.16em;
}

.workspace-entry h3 {
    margin: 12px 0 0;

    font-size: clamp(
        1.8rem,
        3vw,
        2.8rem
    );

    line-height: 1;
    letter-spacing: -0.035em;
}

.workspace-entry p {
    max-width: 470px;

    margin: 16px 0 24px;

    line-height: 1.65;
}


.workspace-information-grid {
    display: grid;

    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    margin-top: 48px;

    border-top: 1px solid currentColor;
    border-bottom: 1px solid currentColor;
}

.workspace-information {
    min-height: 150px;

    padding: 24px;

    border-right: 1px solid currentColor;
}

.workspace-information:last-child {
    border-right: 0;
}

.workspace-information span {
    display: block;

    margin-bottom: 12px;

    font-size: 0.7rem;
    font-weight: 900;

    letter-spacing: 0.14em;
}

.workspace-information strong {
    display: block;

    font-size: 1.1rem;
    font-weight: 850;
}

.workspace-information p {
    margin: 8px 0 0;

    font-size: 0.82rem;
    line-height: 1.55;
}


.analysis-navigation {
    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 18px;

    padding-bottom: 12px;

    border-bottom: 1px solid currentColor;
}

.analysis-nav-button {
    padding: 8px 12px;

    border: 1px solid currentColor;

    background: transparent;

    font-size: 0.68rem;
    font-weight: 850;

    letter-spacing: 0.08em;
}


.hidden {
    display: none !important;
}


@media (max-width: 900px) {

    .project-research-strip,
    .workspace-information-grid {
        grid-template-columns: 1fr 1fr;
    }

    .project-feature:nth-child(2) {
        border-right: 0;
    }

    .workspace-entry-grid {
        grid-template-columns: 1fr;
    }
}


@media (max-width: 620px) {

    .project-view {
        width: min(
            100% - 28px,
            1180px
        );
    }

    .project-landing {
        min-height: auto;
        padding: 52px 0 60px;
    }

    .project-research-strip,
    .workspace-information-grid {
        grid-template-columns: 1fr;
    }

    .project-feature,
    .workspace-information {
        border-right: 0;
        border-bottom: 1px solid currentColor;
    }

    .project-feature:last-child,
    .workspace-information:last-child {
        border-bottom: 0;
    }

    .workspace-entry {
        min-height: 280px;
        padding: 24px;
    }

    .analysis-navigation {
        overflow-x: auto;
    }
}


/* ============================================================
   END DEPLOY-OP-047
   ============================================================ */
'''


css_text += navigation_css


# ============================================================
# WRITE FILES
# ============================================================

INDEX.write_text(index_text, encoding="utf-8")
APP.write_text(app_text, encoding="utf-8")
CSS.write_text(css_text, encoding="utf-8")


# ============================================================
# POST-WRITE CONTRACT CHECKS
# ============================================================

index_after = sha256(INDEX)
app_after = sha256(APP)
css_after = sha256(CSS)

new_index = INDEX.read_text(encoding="utf-8")
new_app = APP.read_text(encoding="utf-8")
new_css = CSS.read_text(encoding="utf-8")


checks = {
    "landing_view_added":
        'id="project-landing"' in new_index,

    "workspace_home_added":
        'id="workspace-home"' in new_index,

    "analysis_workspace_preserved":
        'id="analysis-workspace"' in new_index,

    "single_ticket_panel_preserved":
        'id="single-ticket-panel"' in new_index,

    "batch_input_panel_preserved":
        'id="batch-input-panel"' in new_index,

    "batch_results_preserved":
        'id="batch-results-panel"' in new_index,

    "selected_ticket_results_preserved":
        'id="results-panel"' in new_index,

    "ticket_form_preserved":
        'id="ticket-form"' in new_index,

    "six_ticket_fields_preserved":
        all(
            f'id="{field}"' in new_index
            for field in (
                "ticket_id",
                "creation_time",
                "creator",
                "creator_detail",
                "summary",
                "description",
            )
        ),

    "batch_input_preserved":
        all(
            marker in new_index
            for marker in (
                'id="batch-file"',
                'id="batch-validate-button"',
            )
        ),

    "batch_table_preserved":
        all(
            marker in new_index
            for marker in (
                'id="batch-results-table"',
                'id="batch-results-table-body"',
            )
        ),

    "analysis_navigation_added":
        'id="analysis-navigation"' in new_index,

    "navigation_logic_added":
        "initializeProjectNavigation" in new_app,

    "single_navigation_added":
        "open-single-ticket-button" in new_app,

    "batch_navigation_added":
        "open-batch-analysis-button" in new_app,

    "existing_single_api_preserved":
        "/tickets/analyze" in new_app,

    "existing_batch_api_preserved":
        "/tickets/analyze-batch" in new_app,

    "batch_selection_preserved":
        "selectBatchTicket" in new_app,

    "detail_renderer_preserved":
        "renderAnalysisResponse" in new_app,

    "no_ticket_pipeline_frontend":
        "TicketPipeline" not in new_app,

    "no_sklearn_frontend":
        "sklearn" not in new_app.lower(),

    "visual_architecture_css_added":
        MARKER in new_css,
}


if not all(checks.values()):
    failed = [
        name
        for name, value in checks.items()
        if not value
    ]

    # Restore immediately if the contract failed.
    INDEX.write_bytes(index_backup.read_bytes())
    APP.write_bytes(app_backup.read_bytes())
    CSS.write_bytes(css_backup.read_bytes())

    raise SystemExit(
        "FAIL: post-write contract failed.\n"
        + "\n".join(
            f"  - {item}"
            for item in failed
        )
        + "\nAll modified files were restored from backups."
    )


# ============================================================
# EVIDENCE
# ============================================================

METRICS.mkdir(parents=True, exist_ok=True)

evidence = {
    "operation": MARKER,
    "title": "FRONTEND INFORMATION ARCHITECTURE",
    "status": "PASS",

    "scope": "frontend architecture only",

    "architecture": {
        "landing_page": True,
        "workspace_home": True,
        "single_ticket_entry": True,
        "multiple_ticket_entry": True,
        "existing_analysis_workspace_reused": True,
        "existing_batch_results_reused": True,
        "existing_detail_view_reused": True,
    },

    "files_modified": {
        "index.html": str(INDEX),
        "app.js": str(APP),
        "style.css": str(CSS),
    },

    "backups": {
        "index.html": str(index_backup),
        "app.js": str(app_backup),
        "style.css": str(css_backup),
    },

    "protected_components": {
        "fastapi": True,
        "ticket_pipeline": True,
        "ticket_explanation": True,
        "t1_t11_runtime": True,
        "model_artifacts": True,
        "single_ticket_api": True,
        "batch_api": True,
        "batch_selection": True,
        "detail_renderer": True,
    },

    "checks": checks,

    "hashes_before": {
        "index.html": index_before,
        "app.js": app_before,
        "style.css": css_before,
    },

    "hashes_after": {
        "index.html": index_after,
        "app.js": app_after,
        "style.css": css_after,
    },

    "bytes_after": {
        "index.html": INDEX.stat().st_size,
        "app.js": APP.stat().st_size,
        "style.css": CSS.stat().st_size,
    },
}

EVIDENCE.write_text(
    json.dumps(evidence, indent=2) + "\n",
    encoding="utf-8",
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 58)
print("DEPLOY-OP-047 — FRONTEND INFORMATION ARCHITECTURE")
print("=" * 58)
print("STATUS: PASS")
print()
print("LANDING PAGE:                    ADDED")
print("WORKSPACE HOME:                  ADDED")
print("SINGLE TICKET ENTRY:             PRESERVED")
print("MULTIPLE TICKET ENTRY:           PRESERVED")
print("EXISTING ANALYSIS WORKSPACE:     PRESERVED")
print("BATCH RESULTS:                   PRESERVED")
print("T1-T11 DETAIL VIEW:              PRESERVED")
print("SINGLE API:                      PRESERVED")
print("BATCH API:                       PRESERVED")
print("TICKET PIPELINE:                 UNTOUCHED")
print("FROZEN RUNTIME:                  UNTOUCHED")
print("MODEL ARTIFACTS:                 UNTOUCHED")
print()
print("BACKUPS:")
print(index_backup)
print(app_backup)
print(css_backup)
print()
print("EVIDENCE:")
print(EVIDENCE)
print("=" * 58)
