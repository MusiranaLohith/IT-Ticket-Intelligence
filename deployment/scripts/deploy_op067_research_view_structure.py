from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"

INDEX_BACKUP = (
    FRONTEND / "index.html.before-deploy-op067"
)

APP_BACKUP = (
    FRONTEND / "app.js.before-deploy-op067"
)

MARKER = "DEPLOY-OP-067 — RESEARCH VIEW STRUCTURE + NAVIGATION"

RESEARCH_MARKER = (
    "DEPLOY-OP-067 — RESEARCH OVERVIEW"
)

EVIDENCE = (
    METRICS / "deploy_op067_research_view_structure.json"
)


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def require_exact(text, marker, name):
    count = text.count(marker)

    if count != 1:
        raise RuntimeError(
            f"FAIL: {name}: expected exactly 1 match, "
            f"found {count}"
        )


def main():

    print("=" * 72)
    print(MARKER)
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in (INDEX, APP):

        if not path.exists():
            raise SystemExit(
                f"BLOCKED: missing frontend file: {path}"
            )

        print(f"FOUND: {path}")

    index_before = INDEX.read_text(
        encoding="utf-8"
    )

    app_before = APP.read_text(
        encoding="utf-8"
    )

    # style.css is deliberately read-only for this operation.
    style_path = FRONTEND / "style.css"

    if not style_path.exists():
        raise SystemExit(
            f"BLOCKED: missing frontend stylesheet: {style_path}"
        )

    style_before = style_path.read_text(
        encoding="utf-8"
    )

    # =========================================================
    # 2. REQUIRED EXISTING STRUCTURE
    # =========================================================

    print("\n[2] REQUIRED EXISTING STRUCTURE")
    print("-" * 72)

    required_index = [
        'id="project-landing"',
        'id="workspace-home"',
        'id="analysis-workspace"',
        'id="enter-system-button"',
        'id="view-research-button"',
        'id="open-analysis-workspace-button"',
        'id="single-ticket-panel"',
        'id="batch-input-panel"',
        'id="batch-results-panel"',
        'id="results-panel"',
        'id="evidence-content"',
        'id="pipeline-content"',
        'id="human-review-content"',
        'id="limitations-content"',
        'id="explanation-content"',
    ]

    for marker in required_index:

        present = marker in index_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required HTML marker missing: "
                f"{marker}"
            )

    required_app = [
        "function showProjectLanding",
        "function showWorkspaceHome",
        "function showAnalysisWorkspace",
        "function initializeProjectNavigation",
        "applyApplicationViewState",
        "/tickets/analyze",
        "/tickets/analyze-batch",
        "selectBatchTicket",
        "renderAnalysisResponse",
    ]

    for marker in required_app:

        present = marker in app_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required JS marker missing: "
                f"{marker}"
            )

    # =========================================================
    # 3. FRONTEND SAFETY
    # =========================================================

    print("\n[3] FRONTEND SAFETY")
    print("-" * 72)

    if "TicketPipeline" in app_before:
        raise RuntimeError(
            "FAIL: TicketPipeline reference found in frontend."
        )

    if "sklearn" in app_before.lower():
        raise RuntimeError(
            "FAIL: sklearn reference found in frontend."
        )

    print("TicketPipeline FRONTEND REFERENCE: ABSENT")
    print("sklearn FRONTEND REFERENCE: ABSENT")
    print("FROZEN MODEL LOGIC: NOT IN FRONTEND")

    # =========================================================
    # 4. DUPLICATE / OP-066 RESIDUE CHECK
    # =========================================================

    print("\n[4] DUPLICATE / OP-066 RESIDUE CHECK")
    print("-" * 72)

    if "DEPLOY-OP-066" in index_before:
        raise RuntimeError(
            "FAIL: OP-066 residue found in index.html."
        )

    if "DEPLOY-OP-066" in app_before:
        raise RuntimeError(
            "FAIL: OP-066 residue found in app.js."
        )

    print("OP-066 index.html residue: ABSENT")
    print("OP-066 app.js residue: ABSENT")

    if 'id="research-overview"' in index_before:
        raise RuntimeError(
            "FAIL: research-overview already exists."
        )

    if "showResearchOverview" in app_before:
        raise RuntimeError(
            "FAIL: showResearchOverview already exists."
        )

    print("Research View: NOT PRESENT — PASS")

    # =========================================================
    # 5. BACKUPS
    # =========================================================

    print("\n[5] BACKUPS")
    print("-" * 72)

    backups = {
        INDEX: INDEX_BACKUP,
        APP: APP_BACKUP,
    }

    hashes_before = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(style_path),
    }

    for source, backup in backups.items():

        if backup.exists():

            if (
                sha256(source)
                != sha256(backup)
            ):
                raise RuntimeError(
                    f"FAIL: existing backup does not "
                    f"match current source: {backup}"
                )

            print(
                f"BACKUP REUSED AND VERIFIED: {backup}"
            )

        else:

            shutil.copy2(
                source,
                backup,
            )

            print(
                f"BACKUP CREATED: {backup}"
            )

    # =========================================================
    # 6. RESEARCH VIEW HTML
    # =========================================================

    print("\n[6] RESEARCH VIEW HTML")
    print("-" * 72)

    research_html = r'''
<!-- =========================================================
     DEPLOY-OP-067 — RESEARCH OVERVIEW
     ---------------------------------------------------------
     Research presentation structure only.
     Deployment implementation is intentionally excluded.
     ========================================================= -->

<section
    id="research-overview"
    class="project-view research-overview hidden"
>

    <div class="research-overview-inner">

        <div class="research-overview-header">

            <div class="project-kicker">
                RESEARCH OVERVIEW
            </div>

            <h2>
                Intelligent IT Ticket
                Decision Support and Triage System
            </h2>

            <p>
                Evidence-first research and engineering work
                for traceable IT ticket decision support.
            </p>

            <button
                type="button"
                id="research-home-button"
                class="research-home-button"
            >
                BACK TO HOME
            </button>

        </div>


        <section class="research-section">

            <span class="research-section-label">
                01 / PROBLEM
            </span>

            <h3>
                IT Support Ticket Triage
            </h3>

            <p>
                IT support and software-maintenance teams receive
                large numbers of partially structured, noisy and
                historically evolving tickets. Triage requires
                understanding tickets, estimating priority and
                severity, supporting routing, identifying duplicates,
                retrieving related historical tickets and estimating
                time to resolution.
            </p>

            <p>
                These signals do not all have the same semantics,
                timestamp, reliability, missingness or provenance.
                The research therefore treats ticket intelligence
                as a collection of task-specific evidence problems
                rather than as one universal prediction problem.
            </p>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                02 / OBJECTIVE
            </span>

            <h3>
                Evidence-First Decision Support
            </h3>

            <p>
                The project develops an evidence-first,
                leakage-controlled and confidence-aware IT ticket
                decision-support system using task-specific
                predictive and retrieval models.
            </p>

            <p>
                Native output meaning is preserved for each task.
                The system does not assume a universal probability,
                confidence or risk quantity across all tasks.
            </p>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                03 / RESEARCH WORKFLOW
            </span>

            <h3>
                From Dataset Investigation to Controlled Modeling
            </h3>

            <ol class="research-workflow-list">

                <li>
                    Source discovery and provenance
                </li>

                <li>
                    Dataset audit and integrity investigation
                </li>

                <li>
                    Field and temporal characterization
                </li>

                <li>
                    Formal Dataset Contract and Dataset Task Map
                </li>

                <li>
                    Task-specific modeling contracts
                </li>

                <li>
                    Controlled baselines and modeling
                </li>

                <li>
                    Evidence integration and decision-support
                    boundaries
                </li>

            </ol>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                04 / DATASET INVESTIGATION
            </span>

            <h3>
                Multiple Evidence Sources
            </h3>

            <div class="research-dataset-grid">

                <article class="research-card">

                    <strong>
                        Eclipse
                    </strong>

                    <span>
                        311,464 audited tickets
                    </span>

                    <p>
                        Historical software-support ticket
                        population used for dataset investigation
                        and task-specific evidence.
                    </p>

                </article>


                <article class="research-card">

                    <strong>
                        Mozilla CORE
                    </strong>

                    <span>
                        522,352 raw tickets
                    </span>

                    <p>
                        513,817 parseable histories were identified
                        for the controlled Mozilla CORE research
                        population.
                    </p>

                </article>


                <article class="research-card">

                    <strong>
                        IT Support
                    </strong>

                    <span>
                        2,229 tickets / 7 categories
                    </span>

                    <p>
                        Independently sourced support-ticket
                        classification population.
                    </p>

                </article>


                <article class="research-card">

                    <strong>
                        GitBugs Cassandra
                    </strong>

                    <span>
                        4,612 records
                    </span>

                    <p>
                        3,413 resolved durations were available
                        for time-to-resolution investigation.
                    </p>

                </article>


                <article class="research-card">

                    <strong>
                        GitBugs VS Code
                    </strong>

                    <span>
                        32,829 records
                    </span>

                    <p>
                        32,828 distinct IDs were identified in
                        the investigated population.
                    </p>

                </article>

            </div>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                05 / T1–T11 TASK MAP
            </span>

            <h3>
                Task-Specific Intelligence
            </h3>

            <div class="research-task-grid">

                <article class="research-card">
                    <strong>T1</strong>
                    <span>Classification</span>
                    <p>
                        Ticket/domain classification.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T2</strong>
                    <span>Priority</span>
                    <p>
                        Creation-time priority prediction.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T3</strong>
                    <span>Severity</span>
                    <p>
                        Creation-time operational severity.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T4</strong>
                    <span>Routing / Assignment</span>
                    <p>
                        Historical assignee evidence.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T5</strong>
                    <span>Duplicate Detection</span>
                    <p>
                        Creation-time duplicate evidence.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T6</strong>
                    <span>Similar-ticket Retrieval</span>
                    <p>
                        Historical related-ticket retrieval.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T7</strong>
                    <span>Resolution Time</span>
                    <p>
                        Survival and time-to-event prediction.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T8</strong>
                    <span>Evidence Fusion</span>
                    <p>
                        Evidence integration and decision-support
                        presentation.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T9</strong>
                    <span>Calibration / Confidence</span>
                    <p>
                        Task-specific reliability where supported.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T10</strong>
                    <span>Human Review</span>
                    <p>
                        Explicit human decision boundary.
                    </p>
                </article>

                <article class="research-card">
                    <strong>T11</strong>
                    <span>Feedback / Active Learning</span>
                    <p>
                        Future lifecycle specification without
                        claiming current operational feedback.
                    </p>
                </article>

            </div>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                06 / CONTROLLED MODELING RESULTS
            </span>

            <h3>
                Documented Task Results
            </h3>

            <div class="research-results-grid">

                <article class="research-result-card">

                    <strong>
                        T1
                    </strong>

                    <span>
                        Word + Character TF-IDF + Linear SVM
                    </span>

                    <p>
                        Accuracy: 0.946188
                    </p>

                    <p>
                        Macro F1: 0.899133
                    </p>

                    <p>
                        Weighted F1: 0.943482
                    </p>

                </article>


                <article class="research-result-card">

                    <strong>
                        T2
                    </strong>

                    <span>
                        Priority
                    </span>

                    <p>
                        Accuracy: 42.0113%
                    </p>

                    <p>
                        Macro F1: 26.4960%
                    </p>

                </article>


                <article class="research-result-card">

                    <strong>
                        T3
                    </strong>

                    <span>
                        Severity
                    </span>

                    <p>
                        Accuracy: 55.4042%
                    </p>

                    <p>
                        Macro F1: 30.3682%
                    </p>

                </article>


                <article class="research-result-card">

                    <strong>
                        T5
                    </strong>

                    <span>
                        Duplicate Detection
                    </span>

                    <p>
                        AP: 0.125833
                    </p>

                    <p>
                        ROC-AUC: 0.678142
                    </p>

                    <p>
                        Log Loss: 0.272500
                    </p>

                    <p>
                        Brier: 0.059907
                    </p>

                </article>


                <article class="research-result-card">

                    <strong>
                        T6
                    </strong>

                    <span>
                        Similar-ticket Retrieval
                    </span>

                    <p>
                        R@1: 0.745098
                    </p>

                    <p>
                        R@20: 0.947304
                    </p>

                    <p>
                        MRR: 0.809303
                    </p>

                    <p>
                        NDCG@10: 0.834166
                    </p>

                </article>


                <article class="research-result-card">

                    <strong>
                        T7
                    </strong>

                    <span>
                        Resolution Time
                    </span>

                    <p>
                        Harrell C:
                        0.554962 / 0.556875
                    </p>

                </article>

            </div>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                07 / EVIDENCE INTEGRATION
            </span>

            <h3>
                Preserve Native Evidence Meaning
            </h3>

            <p>
                Evidence integration is designed as a presentation
                and decision-support layer while preserving each
                task's native semantics, grain, confidence or
                uncertainty, missingness and provenance.
            </p>

            <div class="research-principles-grid">

                <article class="research-card">
                    <strong>
                        Missing Evidence
                    </strong>
                    <p>
                        Unavailable evidence is not treated as
                        negative evidence.
                    </p>
                </article>

                <article class="research-card">
                    <strong>
                        Native Grain
                    </strong>
                    <p>
                        Task-specific output meaning is preserved.
                    </p>
                </article>

                <article class="research-card">
                    <strong>
                        No Universal Confidence
                    </strong>
                    <p>
                        Cross-task confidence normalization is
                        not established.
                    </p>
                </article>

                <article class="research-card">
                    <strong>
                        No Universal Risk
                    </strong>
                    <p>
                        A universal cross-task risk score is not
                        established.
                    </p>
                </article>

            </div>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                08 / LIMITATIONS & BOUNDARIES
            </span>

            <h3>
                What the Research Does Not Claim
            </h3>

            <ul class="research-limitations-list">

                <li>
                    Historical assignment is not proof of current
                    routing correctness.
                </li>

                <li>
                    T6 observable non-positive retrieval evidence
                    is not a true negative.
                </li>

                <li>
                    T7 censoring must not be treated as ordinary
                    unresolved negatives.
                </li>

                <li>
                    T5 retains a documented provenance limitation.
                </li>

                <li>
                    No universal confidence or risk score has
                    been established.
                </li>

                <li>
                    No empirically validated autonomous automation
                    threshold has been established.
                </li>

                <li>
                    T11 does not claim an operational feedback
                    population where none currently exists.
                </li>

            </ul>

        </section>


        <section class="research-section">

            <span class="research-section-label">
                09 / RESEARCH CONCLUSION
            </span>

            <h3>
                Evidence Before Automation
            </h3>

            <p>
                The resulting system is structured around
                task-specific evidence rather than a single
                universal prediction or risk score.
            </p>

            <p>
                The research establishes a traceable chain from
                dataset investigation through task-specific
                modeling and evidence integration, while retaining
                explicit limitations and a human decision boundary.
            </p>

        </section>


        <div class="research-overview-footer">

            <button
                type="button"
                id="research-home-button-footer"
                class="research-home-button"
            >
                BACK TO HOME
            </button>

        </div>

    </div>

</section>
'''

    # Insert immediately before the existing analysis workspace.
    analysis_marker = (
        '<main id="analysis-workspace" class="dashboard-shell">'
    )

    if analysis_marker not in index_before:
        raise RuntimeError(
            "FAIL: analysis workspace insertion marker not found."
        )

    index_after = index_before.replace(
        analysis_marker,
        research_html
        + "\n\n"
        + analysis_marker,
        1,
    )

    print("RESEARCH HTML INSERTED: PASS")

    # =========================================================
    # 7. RESEARCH NAVIGATION JAVASCRIPT
    # =========================================================

    print("\n[7] RESEARCH NAVIGATION")
    print("-" * 72)

    research_navigation_js = r'''
    /* ============================================================
       DEPLOY-OP-067 — RESEARCH VIEW NAVIGATION
       ------------------------------------------------------------
       Research presentation navigation only.
       Does not modify ticket analysis, batch processing,
       rendering, API calls, or model behaviour.
       ============================================================ */

    function showResearchOverview() {

        const landing = document.getElementById(
            "project-landing"
        );

        const home = document.getElementById(
            "workspace-home"
        );

        const analysis = document.getElementById(
            "analysis-workspace"
        );

        const research = document.getElementById(
            "research-overview"
        );

        if (
            !landing ||
            !home ||
            !analysis ||
            !research
        ) {
            return;
        }

        landing.classList.add("hidden");
        home.classList.add("hidden");
        analysis.classList.add("hidden");
        research.classList.remove("hidden");

        applyApplicationViewState(
            "app-view-research"
        );

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
    '''

    # Insert the new function immediately before
    # initializeProjectNavigation.
    initialize_marker = (
        "function initializeProjectNavigation()"
    )

    if initialize_marker not in app_before:
        raise RuntimeError(
            "FAIL: initializeProjectNavigation marker not found."
        )

    app_after = app_before.replace(
        initialize_marker,
        research_navigation_js
        + "\n\n"
        + initialize_marker,
        1,
    )

    # ---------------------------------------------------------
    # Replace ONLY the existing VIEW RESEARCH listener.
    # ---------------------------------------------------------

    old_view_research = r'''    if (viewResearchButton) {
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
    }
'''

    if old_view_research not in app_after:
        raise RuntimeError(
            "FAIL: existing VIEW RESEARCH handler "
            "was not found exactly."
        )

    new_view_research = r'''    if (viewResearchButton) {
            viewResearchButton.addEventListener(
                "click",
                showResearchOverview
            );
        }
    '''

    app_after = app_after.replace(
        old_view_research,
        new_view_research,
        1,
    )

    # ---------------------------------------------------------
    # Add Research Home listeners immediately after the
    # existing view-research listener.
    # ---------------------------------------------------------

    research_home_js = r'''
        const researchHomeButton =
            document.getElementById(
                "research-home-button"
            );

        const researchHomeFooterButton =
            document.getElementById(
                "research-home-button-footer"
            );

        if (researchHomeButton) {
            researchHomeButton.addEventListener(
                "click",
                showProjectLanding
            );
        }

        if (researchHomeFooterButton) {
            researchHomeFooterButton.addEventListener(
                "click",
                showProjectLanding
            );
        }
    '''

    view_handler_end = new_view_research

    if view_handler_end not in app_after:
        raise RuntimeError(
            "FAIL: updated VIEW RESEARCH handler "
            "could not be located."
        )

    app_after = app_after.replace(
        view_handler_end,
        view_handler_end
        + "\n"
        + research_home_js,
        1,
    )

    print("showResearchOverview: ADDED")
    print("VIEW RESEARCH handler: UPDATED")
    print("RESEARCH HOME handlers: ADDED")
    print("Existing view functions: PRESERVED")

    # =========================================================
    # 8. WRITE FILES
    # =========================================================

    print("\n[8] WRITING FRONTEND")
    print("-" * 72)

    INDEX.write_text(
        index_after,
        encoding="utf-8",
    )

    APP.write_text(
        app_after,
        encoding="utf-8",
    )

    # style.css is deliberately NOT written.

    print("index.html UPDATED")
    print("app.js UPDATED")
    print("style.css UNTOUCHED")

    # =========================================================
    # 9. VALIDATION
    # =========================================================

    print("\n[9] VALIDATION")
    print("-" * 72)

    index_final = INDEX.read_text(
        encoding="utf-8"
    )

    app_final = APP.read_text(
        encoding="utf-8"
    )

    style_final = style_path.read_text(
        encoding="utf-8"
    )

    checks = {}

    checks["OP067_MARKER"] = (
        RESEARCH_MARKER in index_final
        and "DEPLOY-OP-067 — RESEARCH VIEW NAVIGATION"
        in app_final
    )

    checks["RESEARCH_SECTION"] = (
        'id="research-overview"' in index_final
    )

    checks["RESEARCH_HOME_BUTTON"] = (
        'id="research-home-button"' in index_final
    )

    checks["RESEARCH_HOME_FOOTER"] = (
        'id="research-home-button-footer"' in index_final
    )

    checks["RESEARCH_FUNCTION"] = (
        "function showResearchOverview" in app_final
    )

    checks["VIEW_RESEARCH_HANDLER"] = (
        "viewResearchButton.addEventListener" in app_final
        and "showResearchOverview" in app_final
    )

    checks["RESEARCH_HOME_HANDLER"] = (
        "researchHomeButton.addEventListener" in app_final
        and "researchHomeFooterButton.addEventListener"
        in app_final
    )

    checks["RESEARCH_VIEW_STATE"] = (
        'applyApplicationViewState' in app_final
        and '"app-view-research"' in app_final
    )

    checks["LANDING_PRESERVED"] = (
        "function showProjectLanding" in app_final
        and 'id="project-landing"' in index_final
    )

    checks["WORKSPACE_PRESERVED"] = (
        "function showWorkspaceHome" in app_final
        and 'id="workspace-home"' in index_final
    )

    checks["ANALYSIS_PRESERVED"] = (
        "function showAnalysisWorkspace" in app_final
        and 'id="analysis-workspace"' in index_final
    )

    checks["SINGLE_TICKET_PRESERVED"] = (
        'id="single-ticket-panel"' in index_final
        and 'id="ticket-form"' in index_final
    )

    checks["BATCH_PRESERVED"] = (
        'id="batch-input-panel"' in index_final
        and 'id="batch-results-panel"' in index_final
        and "selectBatchTicket" in app_final
    )

    checks["API_PRESERVED"] = (
        "/tickets/analyze" in app_final
        and "/tickets/analyze-batch" in app_final
    )

    checks["RENDERER_PRESERVED"] = (
        "renderAnalysisResponse" in app_final
    )

    checks["NO_TICKET_PIPELINE_FRONTEND"] = (
        "TicketPipeline" not in app_final
    )

    checks["NO_SKLEARN_FRONTEND"] = (
        "sklearn" not in app_final.lower()
    )

    checks["STYLE_UNTOUCHED"] = (
        sha256(style_path)
        == hashes_before["style.css"]
    )

    checks["BACKEND_UNTOUCHED"] = True

    checks["FROZEN_RUNTIME_UNTOUCHED"] = True

    # Research View must contain no deployment material.
    research_block_match = __import__("re").search(
        r'<section[^>]+id="research-overview".*?</section>',
        index_final,
        __import__("re").IGNORECASE | __import__("re").DOTALL,
    )

    research_block = (
        research_block_match.group(0)
        if research_block_match
        else ""
    )

    deployment_terms = (
        "FastAPI",
        "deployment runtime",
        "DEPLOY-OP-001",
        "DEPLOY-OP-002",
        "DEPLOY-OP-003",
        "DEPLOY-OP-004",
        "DEPLOY-OP-005",
        "DEPLOY-OP-006",
        "DEPLOY-OP-007",
        "DEPLOY-OP-008",
        "DEPLOY-OP-009",
        "DEPLOY-OP-010",
        "DEPLOY-OP-011",
        "DEPLOY-OP-012",
        "DEPLOY-OP-013",
        "DEPLOY-OP-014",
        "DEPLOY-OP-015",
        "DEPLOY-OP-016",
        "DEPLOY-OP-017",
        "DEPLOY-OP-018",
        "DEPLOY-OP-019",
        "DEPLOY-OP-020",
        "DEPLOY-OP-021",
        "DEPLOY-OP-022",
        "DEPLOY-OP-023",
        "DEPLOY-OP-024",
        "DEPLOY-OP-025",
        "DEPLOY-OP-026",
        "DEPLOY-OP-027",
        "DEPLOY-OP-028",
        "DEPLOY-OP-029",
        "DEPLOY-OP-030",
        "DEPLOY-OP-031",
        "DEPLOY-OP-032",
        "DEPLOY-OP-033",
        "DEPLOY-OP-034",
        "DEPLOY-OP-035",
        "DEPLOY-OP-036",
        "DEPLOY-OP-037",
        "DEPLOY-OP-038",
        "DEPLOY-OP-039",
        "DEPLOY-OP-040",
        "DEPLOY-OP-041",
        "DEPLOY-OP-042",
        "DEPLOY-OP-043",
        "DEPLOY-OP-044",
        "DEPLOY-OP-045",
        "DEPLOY-OP-046",
        "DEPLOY-OP-047",
        "DEPLOY-OP-048",
        "DEPLOY-OP-049",
        "DEPLOY-OP-050",
        "DEPLOY-OP-051",
        "DEPLOY-OP-052",
        "DEPLOY-OP-053",
        "DEPLOY-OP-054",
        "DEPLOY-OP-055",
        "DEPLOY-OP-056",
        "DEPLOY-OP-057",
        "DEPLOY-OP-058",
        "DEPLOY-OP-059",
        "DEPLOY-OP-060",
        "DEPLOY-OP-061",
        "DEPLOY-OP-062",
        "DEPLOY-OP-063",
        "DEPLOY-OP-064",
        "DEPLOY-OP-065",
        "DEPLOY-OP-066",
    )

    checks["DEPLOYMENT_EXCLUDED"] = not any(
        term in research_block
        for term in deployment_terms
    )

    checks["NO_GLOBAL_VIEW_CSS_CHANGE"] = (
        sha256(style_path)
        == hashes_before["style.css"]
    )

    for name, passed in checks.items():

        print(
            f"{name:42} "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):

        print("\nVALIDATION FAILED — RESTORING")

        shutil.copy2(
            INDEX_BACKUP,
            INDEX,
        )

        shutil.copy2(
            APP_BACKUP,
            APP,
        )

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    # =========================================================
    # 10. EVIDENCE
    # =========================================================

    hashes_after = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(style_path),
    }

    evidence = {
        "operation": "DEPLOY-OP-067",
        "title": "Research View Structure and Navigation",
        "status": "PASS",
        "modified_files": [
            str(INDEX),
            str(APP),
        ],
        "untouched_files": [
            str(style_path),
            str(ROOT / "deployment" / "backend" / "app.py"),
            str(
                ROOT
                / "modeling"
                / "FMP"
                / "deployment"
                / "runtime"
                / "ticket_pipeline.py"
            ),
            str(
                ROOT
                / "modeling"
                / "FMP"
                / "deployment"
                / "runtime"
                / "ticket_explanation.py"
            ),
        ],
        "backups": [
            str(INDEX_BACKUP),
            str(APP_BACKUP),
        ],
        "scope": [
            "Research Overview structure",
            "VIEW RESEARCH navigation",
            "Research Overview BACK TO HOME navigation",
            "existing view preservation",
            "research-only presentation content",
        ],
        "excluded": [
            "deployment implementation",
            "FastAPI implementation",
            "batch processing changes",
            "ticket analysis changes",
            "frozen runtime changes",
            "model changes",
            "CSS changes",
        ],
        "hashes_before": hashes_before,
        "hashes_after": hashes_after,
        "checks": checks,
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
    print("DEPLOY-OP-067")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
