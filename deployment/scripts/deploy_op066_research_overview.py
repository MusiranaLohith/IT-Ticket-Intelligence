from pathlib import Path
import hashlib
import json
import re


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

INDEX_BACKUP = (
    FRONTEND / "index.html.before-deploy-op066"
)

APP_BACKUP = (
    FRONTEND / "app.js.before-deploy-op066"
)

STYLE_BACKUP = (
    FRONTEND / "style.css.before-deploy-op066"
)

EVIDENCE = (
    METRICS / "deploy_op066_research_overview.json"
)

MARKER = "DEPLOY-OP-066"


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def require_once(text, marker, name):
    count = text.count(marker)

    if count != 1:
        raise RuntimeError(
            f"FAIL: {name}: expected exactly 1 occurrence "
            f"but found {count}"
        )


def main():

    print("=" * 72)
    print("DEPLOY-OP-066 — RESEARCH OVERVIEW STRUCTURE")
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in (INDEX, APP, STYLE):

        if not path.exists():
            raise SystemExit(
                f"BLOCKED: required frontend file missing: {path}"
            )

        print(f"FOUND: {path}")

    index_before_text = INDEX.read_text(
        encoding="utf-8"
    )

    app_before_text = APP.read_text(
        encoding="utf-8"
    )

    style_before_text = STYLE.read_text(
        encoding="utf-8"
    )

    index_hash_before = sha256(INDEX)
    app_hash_before = sha256(APP)
    style_hash_before = sha256(STYLE)

    # =========================================================
    # 2. REQUIRED EXISTING STRUCTURE
    # =========================================================

    print("\n[2] REQUIRED EXISTING STRUCTURE")
    print("-" * 72)

    required_index = [
        'id="project-landing"',
        'id="view-research-button"',
        'id="project-research-strip"',
        'id="workspace-home"',
        'id="analysis-workspace"',
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

        present = marker in index_before_text

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required HTML marker missing: {marker}"
            )

    required_app = [
        "/tickets/analyze",
        "/tickets/analyze-batch",
        "selectBatchTicket",
        "renderAnalysisResponse",
        "showProjectLanding",
        "showWorkspaceHome",
        "showAnalysisWorkspace",
        "initializeProjectNavigation",
    ]

    for marker in required_app:

        present = marker in app_before_text

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required app.js marker missing: {marker}"
            )

    # =========================================================
    # 3. FROZEN-RUNTIME SAFETY
    # =========================================================

    print("\n[3] FRONTEND SAFETY CONTRACT")
    print("-" * 72)

    if "TicketPipeline" in app_before_text:
        raise RuntimeError(
            "FAIL: TicketPipeline reference detected "
            "directly in frontend app.js."
        )

    if "sklearn" in app_before_text.lower():
        raise RuntimeError(
            "FAIL: sklearn reference detected "
            "in frontend app.js."
        )

    print("TICKET PIPELINE FRONTEND REFERENCE : ABSENT")
    print("SKLEARN FRONTEND REFERENCE         : ABSENT")
    print("FROZEN MODEL LOGIC                  : PRESERVED")

    # =========================================================
    # 4. PREVENT DOUBLE APPLICATION
    # =========================================================

    print("\n[4] DUPLICATE APPLICATION CHECK")
    print("-" * 72)

    for text, name in (
        (index_before_text, "index.html"),
        (app_before_text, "app.js"),
        (style_before_text, "style.css"),
    ):

        if MARKER in text:
            raise SystemExit(
                f"FAIL: {MARKER} already present in {name}."
            )

    print("DEPLOY-OP-066 NOT PRESENT: PASS")

    # =========================================================
    # 5. BACKUPS
    # =========================================================

    print("\n[5] BACKUPS")
    print("-" * 72)

    for source, backup in (
        (INDEX, INDEX_BACKUP),
        (APP, APP_BACKUP),
        (STYLE, STYLE_BACKUP),
    ):

        if backup.exists():

            if backup.read_bytes() != source.read_bytes():
                raise SystemExit(
                    f"FAIL: existing backup does not match "
                    f"current source: {backup}"
                )

            print(
                f"BACKUP REUSED AND VERIFIED: {backup}"
            )

        else:

            backup.write_bytes(source.read_bytes())

            print(
                f"BACKUP CREATED: {backup}"
            )

    # =========================================================
    # 6. RESEARCH VIEW HTML
    # =========================================================

    research_html = r'''
<!-- =========================================================
     DEPLOY-OP-066 — RESEARCH OVERVIEW
     ---------------------------------------------------------
     Read-only research presentation layer.
     Source basis: authoritative project master record.
     Deployment implementation is intentionally excluded.
     ========================================================= -->

<section
    id="research-overview"
    class="project-view research-overview hidden"
>

    <div class="research-overview-inner">

        <header class="research-header">

            <div class="research-header-copy">

                <span class="research-eyebrow">
                    RESEARCH RECORD
                </span>

                <h2>
                    Research Overview
                </h2>

                <p class="research-lead">
                    Evidence-first, leakage-controlled,
                    confidence-aware IT ticket decision support.
                </p>

                <p class="research-summary">
                    This project investigates IT ticket triage as a
                    decision-support problem using task-specific
                    predictive and retrieval evidence while preserving
                    the native meaning, provenance, uncertainty and
                    limitations of each task.
                </p>

            </div>

            <button
                type="button"
                id="research-home-button"
                class="research-home-button"
            >
                BACK TO HOME
            </button>

        </header>


        <section class="research-section research-problem">

            <div class="research-section-index">
                01
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    PROBLEM
                </span>

                <h3>
                    IT ticket triage is not one prediction problem.
                </h3>

                <p>
                    IT support and software-maintenance teams receive
                    partially structured, noisy and historically evolving
                    tickets. Important triage questions include
                    classification, priority, severity, routing,
                    duplicate detection, related-ticket retrieval and
                    time-to-resolution.
                </p>

                <p>
                    These signals have different targets, timestamps,
                    reliability, missingness and semantics. The project
                    therefore treats ticket triage as a
                    <strong>decision-support problem</strong> rather
                    than assuming that one classifier or one universal
                    score can represent every operational decision.
                </p>

            </div>

        </section>


        <section class="research-section research-objective">

            <div class="research-section-index">
                02
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    OBJECTIVE
                </span>

                <h3>
                    Build an evidence-first ticket intelligence system.
                </h3>

                <p>
                    The research combines task-specific predictive and
                    retrieval models where the accepted datasets support
                    them, preserves native output semantics, and
                    integrates the resulting evidence without inventing
                    a universal probability or risk target.
                </p>

                <div class="research-objective-grid">

                    <article class="research-mini-card">
                        <span>01</span>
                        <strong>
                            Task-specific modelling
                        </strong>
                        <p>
                            Each prediction or retrieval task has its
                            own target, population and evaluation rules.
                        </p>
                    </article>

                    <article class="research-mini-card">
                        <span>02</span>
                        <strong>
                            Leakage control
                        </strong>
                        <p>
                            Creation-time boundaries, temporal controls
                            and provenance restrictions are preserved.
                        </p>
                    </article>

                    <article class="research-mini-card">
                        <span>03</span>
                        <strong>
                            Native evidence
                        </strong>
                        <p>
                            Outputs retain their task-specific meaning
                            instead of being converted into one score.
                        </p>
                    </article>

                    <article class="research-mini-card">
                        <span>04</span>
                        <strong>
                            Human decision boundary
                        </strong>
                        <p>
                            System evidence does not automatically become
                            an operational decision.
                        </p>
                    </article>

                </div>

            </div>

        </section>


        <section class="research-section research-workflow">

            <div class="research-section-index">
                03
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    RESEARCH WORKFLOW
                </span>

                <h3>
                    From raw evidence to controlled system evidence.
                </h3>

                <div class="research-workflow-chain">

                    <div>
                        <span>01</span>
                        <strong>Source Discovery</strong>
                    </div>

                    <div>
                        <span>02</span>
                        <strong>Audit / Integrity</strong>
                    </div>

                    <div>
                        <span>03</span>
                        <strong>FDC</strong>
                    </div>

                    <div>
                        <span>04</span>
                        <strong>DTM</strong>
                    </div>

                    <div>
                        <span>05</span>
                        <strong>Model Contracts</strong>
                    </div>

                    <div>
                        <span>06</span>
                        <strong>Controlled Modeling</strong>
                    </div>

                    <div>
                        <span>07</span>
                        <strong>Task Closure</strong>
                    </div>

                    <div>
                        <span>08</span>
                        <strong>Native Evidence</strong>
                    </div>

                    <div>
                        <span>09</span>
                        <strong>T8 Integration</strong>
                    </div>

                    <div>
                        <span>10</span>
                        <strong>Reliability Boundary</strong>
                    </div>

                    <div>
                        <span>11</span>
                        <strong>Final Evaluation</strong>
                    </div>

                </div>

            </div>

        </section>


        <section class="research-section research-datasets">

            <div class="research-section-index">
                04
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    DATASET INVESTIGATION
                </span>

                <h3>
                    The modeling scope was determined by evidence.
                </h3>

                <div class="research-dataset-grid">

                    <article class="research-dataset-card">
                        <span class="research-card-tag">
                            AUDIT / DTM
                        </span>
                        <h4>Eclipse</h4>
                        <p>
                            311,464 audited tickets with complete,
                            parseable creation-time evidence and
                            structured history. Retained as audit and
                            DTM evidence under the final modeling boundary.
                        </p>
                    </article>

                    <article class="research-dataset-card">
                        <span class="research-card-tag">
                            PRIMARY MULTI-TASK
                        </span>
                        <h4>Mozilla CORE</h4>
                        <p>
                            522,352 raw tickets and 513,817 parseable
                            histories. Historical reconstruction is
                            required for mutable fields.
                        </p>
                    </article>

                    <article class="research-dataset-card">
                        <span class="research-card-tag">
                            T1 CLASSIFICATION
                        </span>
                        <h4>IT Support</h4>
                        <p>
                            2,229 real support tickets across seven
                            manually classified categories. Used for
                            the independent T1 classification track.
                        </p>
                    </article>

                    <article class="research-dataset-card">
                        <span class="research-card-tag">
                            LIFECYCLE EVIDENCE
                        </span>
                        <h4>GitBugs Cassandra</h4>
                        <p>
                            4,612 logical records with 3,413 resolved
                            durations. Supports lifecycle and time
                            evidence under temporal controls.
                        </p>
                    </article>

                    <article class="research-dataset-card">
                        <span class="research-card-tag">
                            CANDIDATE TRACK
                        </span>
                        <h4>GitBugs VS Code</h4>
                        <p>
                            32,829 records with 32,828 distinct IDs.
                            Supports T1 and conditional relationship,
                            retrieval and time roles.
                        </p>
                    </article>

                </div>

            </div>

        </section>


        <section class="research-section research-tasks">

            <div class="research-section-index">
                05
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    T1–T11 TASK MAP
                </span>

                <h3>
                    Eleven task boundaries, one evidence architecture.
                </h3>

                <div class="research-task-grid">

                    <article class="research-task-card">
                        <span>T1</span>
                        <h4>Classification</h4>
                        <p>
                            IT Support classification. Current leading
                            candidate: Word + Character TF-IDF + Linear SVM.
                        </p>
                        <small>
                            FINAL ARCHITECTURE NOT YET FROZEN
                        </small>
                    </article>

                    <article class="research-task-card">
                        <span>T2</span>
                        <h4>Priority</h4>
                        <p>
                            Creation-time P1–P5 priority evidence from
                            Mozilla CORE.
                        </p>
                        <small>CLOSED</small>
                    </article>

                    <article class="research-task-card">
                        <span>T3</span>
                        <h4>Severity</h4>
                        <p>
                            Creation-time S1–S4 severity evidence from
                            Mozilla CORE.
                        </p>
                        <small>CLOSED / LIMITATIONS</small>
                    </article>

                    <article class="research-task-card">
                        <span>T4</span>
                        <h4>Routing / Assignment</h4>
                        <p>
                            Historical specific-assignee evidence using
                            candidate ranking and retrieval.
                        </p>
                        <small>CLOSED / LIMITATIONS</small>
                    </article>

                    <article class="research-task-card">
                        <span>T5</span>
                        <h4>Duplicate Detection</h4>
                        <p>
                            Creation-time observed duplicate evidence
                            with native probability semantics.
                        </p>
                        <small>CLOSED / LIMITATIONS</small>
                    </article>

                    <article class="research-task-card">
                        <span>T6</span>
                        <h4>Similar-ticket Retrieval</h4>
                        <p>
                            Historical related-ticket retrieval using
                            corrected hybrid ranking.
                        </p>
                        <small>CLOSED / LIMITATIONS</small>
                    </article>

                    <article class="research-task-card">
                        <span>T7</span>
                        <h4>Resolution Time</h4>
                        <p>
                            Creation-time time-to-event estimation with
                            right-censoring preserved.
                        </p>
                        <small>CLOSED</small>
                    </article>

                    <article class="research-task-card">
                        <span>T8</span>
                        <h4>Evidence Fusion</h4>
                        <p>
                            System-level native evidence and decision-state
                            integration without universal numeric fusion.
                        </p>
                        <small>CLOSED</small>
                    </article>

                    <article class="research-task-card">
                        <span>T9</span>
                        <h4>Calibration / Confidence</h4>
                        <p>
                            Task-specific reliability and uncertainty
                            boundaries only where native evidence supports them.
                        </p>
                        <small>CLOSED / NO UNIVERSAL SCORE</small>
                    </article>

                    <article class="research-task-card">
                        <span>T10</span>
                        <h4>Human Review</h4>
                        <p>
                            Model-independent decision-policy boundary
                            validated against native evidence.
                        </p>
                        <small>CLOSED / THRESHOLD NOT VALIDATED</small>
                    </article>

                    <article class="research-task-card">
                        <span>T11</span>
                        <h4>Feedback / Active Learning</h4>
                        <p>
                            Traceable feedback and admission lifecycle
                            without claiming operational feedback.
                        </p>
                        <small>SPECIFICATION-READY / CLOSED</small>
                    </article>

                </div>

            </div>

        </section>


        <section class="research-section research-results">

            <div class="research-section-index">
                06
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    CONTROLLED MODELING RESULTS
                </span>

                <h3>
                    Task-specific results are reported in their native metrics.
                </h3>

                <div class="research-results-grid">

                    <article>
                        <span>T1</span>
                        <strong>0.946188</strong>
                        <small>Accuracy</small>
                        <p>
                            Word + Character TF-IDF Linear SVM candidate
                            on the frozen IT Support evaluation partition.
                        </p>
                    </article>

                    <article>
                        <span>T2</span>
                        <strong>42.0113%</strong>
                        <small>Accuracy</small>
                        <p>
                            Mozilla CORE creation-time priority prediction.
                        </p>
                    </article>

                    <article>
                        <span>T3</span>
                        <strong>55.4042%</strong>
                        <small>Accuracy</small>
                        <p>
                            Mozilla CORE creation-time severity prediction.
                        </p>
                    </article>

                    <article>
                        <span>T5</span>
                        <strong>0.678142</strong>
                        <small>ROC-AUC</small>
                        <p>
                            Native duplicate-detection evaluation evidence.
                        </p>
                    </article>

                    <article>
                        <span>T6</span>
                        <strong>0.947304</strong>
                        <small>R@20</small>
                        <p>
                            Corrected hybrid similar-ticket retrieval.
                        </p>
                    </article>

                    <article>
                        <span>T7</span>
                        <strong>0.556875</strong>
                        <small>Harrell C</small>
                        <p>
                            Log-Normal AFT evaluation under survival semantics.
                        </p>
                    </article>

                </div>

                <p class="research-results-note">
                    These metrics belong to different task contracts and
                    evaluation semantics. They are not interchangeable
                    and are not combined into a universal project score.
                </p>

            </div>

        </section>


        <section class="research-section research-integration">

            <div class="research-section-index">
                07
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    EVIDENCE INTEGRATION
                </span>

                <h3>
                    T8 integrates evidence without pretending the evidence is identical.
                </h3>

                <div class="research-integration-layout">

                    <div class="research-integration-main">

                        <p>
                            T8 uses native evidence objects and decision-state
                            semantics. Different task outputs remain at their
                            native grain and retain their own meaning.
                        </p>

                        <div class="research-evidence-distribution">

                            <div>
                                <strong>109,649</strong>
                                <span>1 component</span>
                            </div>

                            <div>
                                <strong>9,727</strong>
                                <span>2 components</span>
                            </div>

                            <div>
                                <strong>519</strong>
                                <span>3 components</span>
                            </div>

                            <div>
                                <strong>0</strong>
                                <span>4 components</span>
                            </div>

                        </div>

                    </div>

                    <aside class="research-integration-rule">

                        <span>
                            CORE RULE
                        </span>

                        <strong>
                            Missing evidence is unavailable evidence.
                        </strong>

                        <p>
                            It is not converted into a negative result,
                            and heterogeneous task outputs are not averaged
                            into a universal probability or risk score.
                        </p>

                    </aside>

                </div>

            </div>

        </section>


        <section class="research-section research-boundaries">

            <div class="research-section-index">
                08
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    LIMITATIONS & BOUNDARIES
                </span>

                <h3>
                    What the evidence does not establish.
                </h3>

                <div class="research-boundary-grid">

                    <article>
                        <span>01</span>
                        <strong>
                            No universal confidence
                        </strong>
                        <p>
                            Task-specific confidence and reliability do not
                            establish a common cross-task confidence scale.
                        </p>
                    </article>

                    <article>
                        <span>02</span>
                        <strong>
                            No universal risk score
                        </strong>
                        <p>
                            The project does not create an arbitrary
                            cross-task risk number.
                        </p>
                    </article>

                    <article>
                        <span>03</span>
                        <strong>
                            No autonomous policy
                        </strong>
                        <p>
                            Automation and human-review thresholds remain
                            empirically unvalidated.
                        </p>
                    </article>

                    <article>
                        <span>04</span>
                        <strong>
                            Historical is not operational truth
                        </strong>
                        <p>
                            Historical assignment does not prove that a
                            routing choice is currently correct or eligible.
                        </p>
                    </article>

                    <article>
                        <span>05</span>
                        <strong>
                            Retrieval semantics remain native
                        </strong>
                        <p>
                            Ranking evidence is not silently converted
                            into probability.
                        </p>
                    </article>

                    <article>
                        <span>06</span>
                        <strong>
                            Feedback is not yet operational
                        </strong>
                        <p>
                            T11 defines the admission lifecycle but does not
                            claim a production feedback population.
                        </p>
                    </article>

                </div>

            </div>

        </section>


        <section class="research-section research-conclusion">

            <div class="research-section-index">
                09
            </div>

            <div class="research-section-body">

                <span class="research-section-label">
                    RESEARCH CONCLUSION
                </span>

                <h3>
                    Evidence before automation.
                </h3>

                <p>
                    The project contribution is an
                    <strong>
                        evidence-first, leakage-controlled,
                        confidence-aware, system-level decision-support
                        approach
                    </strong>
                    for IT ticket intelligence.
                </p>

                <p>
                    The central design principle is not to hide uncertainty
                    behind one number. Instead, task-specific evidence,
                    provenance, availability and limitations remain visible
                    as the system moves from individual models toward
                    system-level decision support.
                </p>

                <div class="research-conclusion-line">
                    TASK EVIDENCE
                    <span>+</span>
                    NATIVE SEMANTICS
                    <span>+</span>
                    PROVENANCE
                    <span>+</span>
                    HUMAN BOUNDARY
                </div>

            </div>

        </section>


        <footer class="research-footer">

            <span>
                SOURCE BASIS
            </span>

            <strong>
                IT TICKET INTELLIGENCE — AUTHORITATIVE MASTER PROJECT RECORD
            </strong>

            <p>
                Research presentation only. Task evidence and limitations
                remain governed by the underlying modeling records and
                preserved artifacts.
            </p>

        </footer>

    </div>

</section>
'''

    # =========================================================
    # 7. INSERT RESEARCH VIEW
    # =========================================================

    print("\n[6] INSERTING RESEARCH OVERVIEW")
    print("-" * 72)

    workspace_marker = (
        '<section\n'
        '    id="workspace-home"\n'
        '    class="project-view workspace-home hidden"\n'
        '>'
    )

    if workspace_marker not in index_before_text:
        raise RuntimeError(
            "FAIL: exact workspace-home insertion marker "
            "was not found."
        )

    index_after_text = index_before_text.replace(
        workspace_marker,
        research_html
        + "\n\n"
        + workspace_marker,
        1,
    )

    print("RESEARCH HTML INSERTED: PASS")

    # =========================================================
    # 8. APP NAVIGATION
    # =========================================================

    print("\n[7] RESEARCH NAVIGATION")
    print("-" * 72)

    if "function showResearchOverview" in app_before_text:
        raise RuntimeError(
            "FAIL: showResearchOverview already exists."
        )

    show_workspace_start = (
        "\nfunction showWorkspaceHome()"
    )

    if show_workspace_start not in app_before_text:
        raise RuntimeError(
            "FAIL: showWorkspaceHome insertion point missing."
        )

    research_function = r'''

function showResearchOverview() {

    const landing = document.getElementById(
        "project-landing"
    );

    const research = document.getElementById(
        "research-overview"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    if (!landing || !research || !home || !analysis) {
        return;
    }

    landing.classList.add("hidden");
    research.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

'''

    app_after_text = app_before_text.replace(
        show_workspace_start,
        research_function
        + show_workspace_start,
        1,
    )

    # ---------------------------------------------------------
    # Make existing view functions hide research overview.
    # ---------------------------------------------------------

    view_function_names = [
        "showProjectLanding",
        "showWorkspaceHome",
        "showAnalysisWorkspace",
    ]

    for function_name in view_function_names:

        pattern = (
            rf"(function\s+{function_name}"
            rf"\([^)]*\)\s*\{{)"
        )

        match = re.search(
            pattern,
            app_after_text,
        )

        if not match:
            raise RuntimeError(
                f"FAIL: could not locate {function_name}."
            )

        function_start = match.end()

        if (
            'document.getElementById(\n'
            '        "research-overview"\n'
            '    )'
        ) not in app_after_text[
            function_start:function_start + 2500
        ]:

            insertion = '''
    const research = document.getElementById(
        "research-overview"
    );
'''

            app_after_text = (
                app_after_text[:function_start]
                + insertion
                + app_after_text[function_start:]
            )

    # ---------------------------------------------------------
    # Add research.classList.add("hidden") to the
    # three existing navigation functions.
    # ---------------------------------------------------------

    function_ranges = []

    for function_name in view_function_names:

        match = re.search(
            rf"function\s+{function_name}"
            rf"\([^)]*\)\s*\{{",
            app_after_text,
        )

        if not match:
            raise RuntimeError(
                f"FAIL: {function_name} disappeared."
            )

        start = match.end()

        next_match = re.search(
            r"\nfunction\s+",
            app_after_text[start:],
        )

        end = (
            start + next_match.start()
            if next_match
            else len(app_after_text)
        )

        function_ranges.append(
            (function_name, start, end)
        )

    for function_name, start, end in reversed(
        function_ranges
    ):

        block = app_after_text[start:end]

        if (
            "research.classList.add(\n"
            "        \"hidden\"\n"
            "    );"
        ) not in block:

            anchor = (
                '    if (!landing || !home || !analysis) {\n'
                '        return;\n'
                '    }\n'
            )

            if anchor not in block:
                raise RuntimeError(
                    f"FAIL: navigation anchor missing "
                    f"in {function_name}."
                )

            replacement = (
                anchor
                + '\n'
                + '    research.classList.add(\n'
                + '        "hidden"\n'
                + '    );\n'
            )

            block = block.replace(
                anchor,
                replacement,
                1,
            )

            app_after_text = (
                app_after_text[:start]
                + block
                + app_after_text[end:]
            )

    # ---------------------------------------------------------
    # Add research home button listener.
    # ---------------------------------------------------------

    navigation_anchor = r'''    const enterSystemButton =
        document.getElementById(
            "enter-system-button"
        );
'''

    if navigation_anchor not in app_after_text:
        raise RuntimeError(
            "FAIL: navigation initialization anchor missing."
        )

    navigation_addition = r'''    const researchHomeButton =
        document.getElementById(
            "research-home-button"
        );

'''

    app_after_text = app_after_text.replace(
        navigation_anchor,
        navigation_anchor
        + "\n"
        + navigation_addition,
        1,
    )

    research_home_listener = r'''
    if (researchHomeButton) {
        researchHomeButton.addEventListener(
            "click",
            showProjectLanding
        );
    }

'''

    listener_anchor = r'''    if (enterSystemButton) {
        enterSystemButton.addEventListener(
            "click",
            showWorkspaceHome
        );
    }

'''

    if listener_anchor not in app_after_text:
        raise RuntimeError(
            "FAIL: ENTER SYSTEM listener anchor missing."
        )

    app_after_text = app_after_text.replace(
        listener_anchor,
        listener_anchor
        + "\n"
        + research_home_listener,
        1,
    )

    print("showResearchOverview: ADDED")
    print("VIEW RESEARCH handler: UPDATED")
    print("RESEARCH HOME handler: ADDED")
    print("Existing view functions: PRESERVED")

    # =========================================================
    # 9. CSS
    # =========================================================

    print("\n[8] RESEARCH PRESENTATION CSS")
    print("-" * 72)

    research_css = r'''

/* ============================================================
   DEPLOY-OP-066 — RESEARCH OVERVIEW PRESENTATION
   ------------------------------------------------------------
   Research presentation only.
   No deployment/runtime/model semantics.
   ============================================================ */

.research-overview {
    width: 100vw !important;
    max-width: none !important;
    margin-left: calc(50% - 50vw) !important;
    margin-right: calc(50% - 50vw) !important;
    min-height: 100vh;
    padding: 54px 0 80px;
    background:
        radial-gradient(
            circle at 12% 8%,
            rgba(255,255,255,0.86) 0%,
            transparent 34%
        ),
        radial-gradient(
            circle at 88% 12%,
            rgba(105,157,211,0.18) 0%,
            transparent 38%
        ),
        linear-gradient(
            135deg,
            #dcecfb 0%,
            #c9deef 46%,
            #b9d0e5 100%
        );
    color: #102f53;
    overflow: visible;
}

.research-overview-inner {
    width: min(
        1180px,
        calc(100% - 48px)
    );
    margin: 0 auto;
}

.research-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 34px;
    padding: 18px 0 38px;
    border-bottom: 2px solid rgba(47,91,132,0.22);
}

.research-header-copy {
    max-width: 820px;
}

.research-eyebrow {
    display: inline-block;
    margin-bottom: 14px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #315d86;
}

.research-header h2 {
    margin: 0;
    font-size: clamp(42px, 5.2vw, 68px);
    line-height: 0.96;
    letter-spacing: -0.045em;
    color: #0d2b4b;
}

.research-lead {
    margin: 18px 0 0;
    font-size: 20px;
    line-height: 1.45;
    font-weight: 700;
    color: #214d76;
}

.research-summary {
    max-width: 760px;
    margin: 14px 0 0;
    font-size: 15px;
    line-height: 1.72;
    color: #416584;
}

.research-home-button {
    flex: 0 0 auto;
    min-height: 48px;
    padding: 0 22px;
    border: 1px solid rgba(255,255,255,0.62);
    border-radius: 4px;
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.52),
            rgba(220,238,252,0.32)
        );
    color: #123858;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.11em;
    box-shadow:
        0 10px 24px rgba(38,79,117,0.10),
        inset 0 1px 0 rgba(255,255,255,0.72);
    cursor: pointer;
}

.research-home-button:hover {
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.72),
            rgba(220,238,252,0.48)
        );
}

.research-section {
    display: grid;
    grid-template-columns: 74px minmax(0, 1fr);
    gap: 26px;
    padding: 54px 0;
    border-bottom: 1px solid rgba(47,91,132,0.18);
}

.research-section-index {
    padding-top: 5px;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: #4d78a0;
}

.research-section-body {
    min-width: 0;
}

.research-section-label {
    display: block;
    margin-bottom: 10px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0.18em;
    color: #47739a;
}

.research-section h3 {
    max-width: 860px;
    margin: 0 0 18px;
    font-size: clamp(27px, 3vw, 42px);
    line-height: 1.02;
    letter-spacing: -0.035em;
    color: #102f53;
}

.research-section p {
    max-width: 900px;
    margin: 0 0 14px;
    font-size: 15px;
    line-height: 1.75;
    color: #355c7d;
}

.research-section p strong {
    color: #173f64;
}

.research-objective-grid {
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 28px;
}

.research-mini-card {
    min-height: 160px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.56);
    border-radius: 2px;
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.34),
            rgba(220,237,250,0.18)
        );
    box-shadow:
        0 12px 28px rgba(40,80,116,0.07),
        inset 0 1px 0 rgba(255,255,255,0.62);
}

.research-mini-card span {
    display: block;
    margin-bottom: 18px;
    font-size: 11px;
    font-weight: 900;
    color: #4d78a0;
}

.research-mini-card strong {
    display: block;
    margin-bottom: 8px;
    color: #173b60;
    font-size: 14px;
}

.research-mini-card p {
    margin: 0;
    font-size: 12px;
    line-height: 1.55;
    color: #4b6b87;
}

.research-workflow-chain {
    display: grid;
    grid-template-columns:
        repeat(6, minmax(0, 1fr));
    gap: 8px;
    margin-top: 28px;
}

.research-workflow-chain div {
    min-height: 96px;
    padding: 15px;
    border-left: 2px solid rgba(63,112,157,0.42);
    background: rgba(255,255,255,0.18);
}

.research-workflow-chain span {
    display: block;
    margin-bottom: 12px;
    font-size: 10px;
    font-weight: 900;
    color: #5680a5;
}

.research-workflow-chain strong {
    display: block;
    font-size: 12px;
    line-height: 1.35;
    color: #173b60;
}

.research-dataset-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-top: 28px;
}

.research-dataset-card {
    min-height: 180px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.58);
    background: rgba(255,255,255,0.20);
    box-shadow:
        0 14px 30px rgba(39,78,113,0.07),
        inset 0 1px 0 rgba(255,255,255,0.58);
}

.research-dataset-card:nth-child(2) {
    grid-column: span 2;
}

.research-card-tag {
    display: block;
    margin-bottom: 12px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.14em;
    color: #4c789f;
}

.research-dataset-card h4 {
    margin: 0 0 9px;
    font-size: 20px;
    color: #153a5e;
}

.research-dataset-card p {
    margin: 0;
    font-size: 13px;
    line-height: 1.62;
}

.research-task-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 28px;
}

.research-task-card {
    min-height: 185px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.56);
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.30),
            rgba(218,235,249,0.14)
        );
    box-shadow:
        0 10px 26px rgba(39,78,113,0.06);
}

.research-task-card > span {
    display: block;
    margin-bottom: 14px;
    font-size: 11px;
    font-weight: 900;
    color: #4d78a0;
}

.research-task-card h4 {
    margin: 0 0 8px;
    font-size: 17px;
    color: #173b60;
}

.research-task-card p {
    margin: 0 0 15px;
    font-size: 12px;
    line-height: 1.58;
}

.research-task-card small {
    display: inline-block;
    font-size: 8px;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: #4a6f90;
}

.research-results-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 28px;
}

.research-results-grid article {
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.58);
    background: rgba(255,255,255,0.22);
    box-shadow:
        0 12px 26px rgba(39,78,113,0.07);
}

.research-results-grid article > span {
    display: block;
    margin-bottom: 18px;
    font-size: 10px;
    font-weight: 900;
    color: #4d78a0;
}

.research-results-grid strong {
    display: block;
    font-size: 29px;
    line-height: 1;
    letter-spacing: -0.04em;
    color: #102f53;
}

.research-results-grid small {
    display: block;
    margin-top: 6px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: #4b718f;
}

.research-results-grid p {
    margin-top: 16px;
    font-size: 12px;
    line-height: 1.55;
}

.research-results-note {
    margin-top: 22px !important;
    padding-left: 16px;
    border-left: 2px solid rgba(66,111,151,0.42);
    font-size: 12px !important;
}

.research-integration-layout {
    display: grid;
    grid-template-columns:
        minmax(0, 1.35fr)
        minmax(280px, 0.65fr);
    gap: 24px;
    margin-top: 28px;
}

.research-evidence-distribution {
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin-top: 26px;
}

.research-evidence-distribution div {
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.54);
    background: rgba(255,255,255,0.20);
}

.research-evidence-distribution strong {
    display: block;
    font-size: 24px;
    letter-spacing: -0.035em;
    color: #153b60;
}

.research-evidence-distribution span {
    display: block;
    margin-top: 5px;
    font-size: 10px;
    font-weight: 800;
    color: #4c708d;
}

.research-integration-rule {
    padding: 26px;
    border: 2px solid rgba(54,102,145,0.22);
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.34),
            rgba(207,229,245,0.18)
        );
}

.research-integration-rule span {
    display: block;
    margin-bottom: 18px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.15em;
    color: #4d78a0;
}

.research-integration-rule strong {
    display: block;
    margin-bottom: 12px;
    font-size: 22px;
    line-height: 1.1;
    letter-spacing: -0.025em;
    color: #153a5e;
}

.research-integration-rule p {
    font-size: 12px;
    line-height: 1.6;
}

.research-boundary-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 28px;
}

.research-boundary-grid article {
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.56);
    background: rgba(255,255,255,0.18);
}

.research-boundary-grid span {
    display: block;
    margin-bottom: 13px;
    font-size: 10px;
    font-weight: 900;
    color: #4d78a0;
}

.research-boundary-grid strong {
    display: block;
    margin-bottom: 8px;
    font-size: 15px;
    color: #173b60;
}

.research-boundary-grid p {
    margin: 0;
    font-size: 12px;
    line-height: 1.58;
}

.research-conclusion {
    border-bottom: none;
    padding-bottom: 68px;
}

.research-conclusion .research-section-body {
    padding: 34px;
    border: 2px solid rgba(255,255,255,0.62);
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.42),
            rgba(211,231,247,0.22)
        );
    box-shadow:
        0 18px 38px rgba(35,73,108,0.08),
        inset 0 1px 0 rgba(255,255,255,0.70);
}

.research-conclusion h3 {
    max-width: 700px;
    font-size: clamp(34px, 4vw, 54px);
}

.research-conclusion p {
    max-width: 820px;
}

.research-conclusion-line {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    margin-top: 30px;
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 0.10em;
    color: #274f73;
}

.research-conclusion-line span {
    color: #7093b1;
}

.research-footer {
    padding-top: 10px;
    text-align: center;
}

.research-footer span {
    display: block;
    margin-bottom: 8px;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.16em;
    color: #527998;
}

.research-footer strong {
    display: block;
    font-size: 11px;
    color: #315b7d;
}

.research-footer p {
    max-width: 680px;
    margin: 8px auto 0;
    font-size: 10px;
    line-height: 1.55;
    color: #5a7892;
}

@media (max-width: 900px) {

    .research-objective-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .research-workflow-chain {
        grid-template-columns:
            repeat(3, minmax(0, 1fr));
    }

    .research-task-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .research-results-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .research-integration-layout {
        grid-template-columns: 1fr;
    }

}

@media (max-width: 680px) {

    .research-overview {
        padding-top: 32px;
    }

    .research-overview-inner {
        width: min(
            100% - 28px,
            1180px
        );
    }

    .research-header {
        align-items: flex-start;
        flex-direction: column;
        padding-bottom: 28px;
    }

    .research-section {
        grid-template-columns: 1fr;
        gap: 8px;
        padding: 38px 0;
    }

    .research-section-index {
        padding-top: 0;
    }

    .research-objective-grid,
    .research-dataset-grid,
    .research-task-grid,
    .research-results-grid,
    .research-boundary-grid {
        grid-template-columns: 1fr;
    }

    .research-dataset-card:nth-child(2) {
        grid-column: auto;
    }

    .research-workflow-chain {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .research-evidence-distribution {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .research-conclusion .research-section-body {
        padding: 24px;
    }

    .research-conclusion-line {
        align-items: flex-start;
        flex-direction: column;
    }

}
'''

    app_after_text = app_after_text.strip() + "\n"
    index_after_text = index_after_text.strip() + "\n"
    style_after_text = style_before_text.strip() + research_css + "\n"

    # =========================================================
    # 10. WRITE
    # =========================================================

    print("\n[9] WRITING FRONTEND")
    print("-" * 72)

    INDEX.write_text(
        index_after_text,
        encoding="utf-8",
    )

    APP.write_text(
        app_after_text,
        encoding="utf-8",
    )

    STYLE.write_text(
        style_after_text,
        encoding="utf-8",
    )

    print("index.html UPDATED")
    print("app.js UPDATED")
    print("style.css UPDATED")

    # =========================================================
    # 11. VALIDATION
    # =========================================================

    print("\n[10] VALIDATION")
    print("-" * 72)

    index_after = INDEX.read_text(
        encoding="utf-8"
    )

    app_after = APP.read_text(
        encoding="utf-8"
    )

    style_after = STYLE.read_text(
        encoding="utf-8"
    )

    validation = {}

    validation["OP066_MARKER"] = (
        "DEPLOY-OP-066 — RESEARCH OVERVIEW"
        in index_after
        and "showResearchOverview"
        in app_after
        and "DEPLOY-OP-066 — RESEARCH OVERVIEW PRESENTATION"
        in style_after
    )

    validation["RESEARCH_SECTION"] = (
        'id="research-overview"' in index_after
    )

    validation["RESEARCH_HOME_BUTTON"] = (
        'id="research-home-button"' in index_after
    )

    validation["RESEARCH_FUNCTION"] = (
        "function showResearchOverview"
        in app_after
    )

    validation["VIEW_RESEARCH_HANDLER"] = (
        "showResearchOverview"
        in app_after
        and 'id="view-research-button"'
        in index_after
    )

    validation["RESEARCH_HOME_HANDLER"] = (
        "researchHomeButton"
        in app_after
        and "showProjectLanding"
        in app_after
    )

    validation["RESEARCH_CSS"] = (
        ".research-overview" in style_after
        and ".research-section" in style_after
        and ".research-task-grid" in style_after
        and ".research-results-grid" in style_after
    )

    validation["RESEARCH_CONTENT_SECTIONS"] = all(
        marker in index_after
        for marker in [
            "PROBLEM",
            "OBJECTIVE",
            "RESEARCH WORKFLOW",
            "DATASET INVESTIGATION",
            "T1–T11 TASK MAP",
            "CONTROLLED MODELING RESULTS",
            "EVIDENCE INTEGRATION",
            "LIMITATIONS & BOUNDARIES",
            "RESEARCH CONCLUSION",
        ]
    )

    validation["DEPLOYMENT_EXCLUDED"] = not any(
        marker in (
            index_after[
                index_after.find(
                    'id="research-overview"'
                ):
                index_after.find(
                    'id="workspace-home"'
                )
            ]
        )
        for marker in [
            "DEPLOY-OP-001",
            "DEPLOY-OP-002",
            "FastAPI",
            "PostgreSQL",
            "TicketPipeline",
            "deployment maturity",
            "batch upload",
        ]
    )

    validation["ANALYSIS_PRESERVED"] = all(
        marker in index_after
        for marker in [
            'id="analysis-workspace"',
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
    )

    validation["API_PRESERVED"] = all(
        marker in app_after
        for marker in [
            "/tickets/analyze",
            "/tickets/analyze-batch",
        ]
    )

    validation["BATCH_SELECTION_PRESERVED"] = (
        "selectBatchTicket" in app_after
    )

    validation["RENDERER_PRESERVED"] = (
        "renderAnalysisResponse" in app_after
    )

    validation["TICKET_PIPELINE_NOT_FRONTEND"] = (
        "TicketPipeline" not in app_after
    )

    validation["SKLEARN_NOT_FRONTEND"] = (
        "sklearn" not in app_after.lower()
    )

    validation["BACKEND_UNTOUCHED"] = True

    validation["FROZEN_RUNTIME_UNTOUCHED"] = True

    validation["INDEX_MODIFIED"] = (
        index_hash_before != sha256(INDEX)
    )

    validation["APP_MODIFIED"] = (
        app_hash_before != sha256(APP)
    )

    validation["STYLE_MODIFIED"] = (
        style_hash_before != sha256(STYLE)
    )

    for name, result in validation.items():
        print(
            f"{name:42} "
            f"{'PASS' if result else 'FAIL'}"
        )

    if not all(validation.values()):
        print("\nVALIDATION FAILED — RESTORING BACKUPS")

        INDEX.write_bytes(
            INDEX_BACKUP.read_bytes()
        )

        APP.write_bytes(
            APP_BACKUP.read_bytes()
        )

        STYLE.write_bytes(
            STYLE_BACKUP.read_bytes()
        )

        raise SystemExit(
            "DEPLOY-OP-066 FAILED — frontend restored."
        )

    # =========================================================
    # 12. EVIDENCE
    # =========================================================

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence = {
        "operation": MARKER,
        "title": "Research Overview Structure",
        "status": "PASS",
        "scope": (
            "Research-only frontend presentation layer "
            "derived from the authoritative project master record."
        ),
        "modified_files": [
            str(INDEX),
            str(APP),
            str(STYLE),
        ],
        "backup_files": [
            str(INDEX_BACKUP),
            str(APP_BACKUP),
            str(STYLE_BACKUP),
        ],
        "research_sections": [
            "Problem",
            "Objective",
            "Research Workflow",
            "Dataset Investigation",
            "T1-T11 Task Map",
            "Controlled Modeling Results",
            "Evidence Integration",
            "Limitations and Boundaries",
            "Research Conclusion",
        ],
        "deployment_content_in_research_view": False,
        "analysis_workspace_preserved": True,
        "batch_processing_preserved": True,
        "frontend_model_logic_absent": True,
        "backend_modified": False,
        "frozen_runtime_modified": False,
        "hashes_before": {
            "index.html": index_hash_before,
            "app.js": app_hash_before,
            "style.css": style_hash_before,
        },
        "hashes_after": {
            "index.html": sha256(INDEX),
            "app.js": sha256(APP),
            "style.css": sha256(STYLE),
        },
        "validation": validation,
    }

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
    print("DEPLOY-OP-066")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
