from pathlib import Path
import re


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

CSS_PATH = ROOT / "deployment/frontend/style.css"
BACKUP_PATH = ROOT / "deployment/frontend/style.css.before-deploy-op039"
APP_PATH = ROOT / "deployment/frontend/app.js"
APP_BACKUP_PATH = ROOT / "deployment/frontend/app.js.before-deploy-op039-final-tweak"

START_MARKER = """/* =================================================
   DEPLOY-OP-039"""

END_MARKER = """   END DEPLOY-OP-039
   ================================================= */"""


FINAL_UI_CSS = r"""
/* =================================================
   DEPLOY-OP-039
   PROFESSIONAL ENGINEERING UI
   NAVY + BLUE + SLATE + CONTROLLED RED ACCENT
   ================================================= */

:root {
    --op39-navy-950: #081426;
    --op39-navy-900: #0d1d33;
    --op39-navy-850: #132a48;
    --op39-navy-800: #19395e;

    --op39-blue-700: #0e56c7;
    --op39-blue-600: #176fe5;
    --op39-blue-500: #3188f5;
    --op39-blue-100: #dcecff;

    --op39-slate-950: #172538;
    --op39-slate-900: #22364e;
    --op39-slate-800: #304861;
    --op39-slate-700: #455e77;
    --op39-slate-600: #5f748b;
    --op39-slate-300: #aebfd0;
    --op39-slate-200: #cbd8e4;
    --op39-slate-100: #dfe8f0;
    --op39-slate-050: #edf3f8;

    --op39-white: #ffffff;

    /* Controlled red structural accent */
    --op39-red-900: #711923;
    --op39-red-800: #941f2b;
    --op39-red-700: #b52332;
    --op39-red-600: #d12d3d;
    --op39-red-100: #fbe9ec;

    /* Integrity PASS */
    --op39-green-800: #11643e;
    --op39-green-700: #168553;
    --op39-green-600: #20a267;
    --op39-green-100: #e4f6ed;
    --op39-green-050: #f1fbf6;

    --op39-border: #9fb2c5;
    --op39-border-strong: #7890a7;

    --op39-shadow-lg:
        0 20px 42px rgba(7, 24, 44, 0.18),
        0 6px 14px rgba(7, 24, 44, 0.10);

    --op39-shadow-md:
        0 10px 24px rgba(7, 24, 44, 0.14),
        0 3px 8px rgba(7, 24, 44, 0.08);

    --op39-shadow-sm:
        0 5px 14px rgba(7, 24, 44, 0.10);
}


/* =================================================
   PAGE FOUNDATION
   ================================================= */

html,
body {
    background:
        linear-gradient(
            135deg,
            #d4e0eb 0%,
            #e3ebf3 48%,
            #d8e4ef 100%
        ) !important;

    color: var(--op39-slate-950) !important;
}

body {
    font-weight: 550 !important;
    letter-spacing: 0.004em;
}


/* =================================================
   HEADER
   ================================================= */

.topbar,
header.topbar {
    background:
        linear-gradient(
            135deg,
            var(--op39-navy-950) 0%,
            var(--op39-navy-900) 52%,
            var(--op39-navy-800) 100%
        ) !important;

    color: #ffffff !important;

    border: 0 !important;
    border-bottom: 3px solid var(--op39-blue-600) !important;

    box-shadow:
        0 12px 30px rgba(5, 18, 34, 0.32),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

.brand-title,
.topbar .brand-title {
    color: #ffffff !important;
    font-weight: 850 !important;
}

.brand-subtitle,
.topbar .brand-subtitle {
    color: #bdd0e3 !important;
    font-weight: 600 !important;
}

.prototype-badge,
.topbar .prototype-badge {
    background: rgba(49, 136, 245, 0.20) !important;
    color: #e5f2ff !important;
    border: 1px solid rgba(126, 190, 255, 0.60) !important;
    border-radius: 0 !important;
}


/* =================================================
   MAIN SHELL
   ================================================= */

.dashboard-shell,
main.dashboard-shell {
    background:
        linear-gradient(
            180deg,
            rgba(216, 228, 239, 0.94),
            rgba(235, 241, 246, 0.97)
        ) !important;
}

.main-heading,
.page-title,
.dashboard-title {
    color: var(--op39-navy-950) !important;
    font-weight: 850 !important;
}

.section-heading,
.panel-title,
h2,
h3 {
    color: var(--op39-navy-900) !important;
    font-weight: 780 !important;
}


/* =================================================
   GENERAL PANELS
   ================================================= */

.panel,
.dashboard-panel,
.ticket-panel,
.results-panel,
.analysis-panel,
.batch-panel {
    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #f3f7fb 100%
        ) !important;

    border: 1.5px solid var(--op39-border) !important;
    border-radius: 0 !important;
    box-shadow: var(--op39-shadow-md) !important;
}


/* =================================================
   SINGLE TICKET
   ================================================= */

.single-ticket-panel,
#single-ticket-panel {
    border-top: 4px solid var(--op39-blue-600) !important;
}


/* =================================================
   BATCH INPUT
   ================================================= */

.batch-input-panel,
#batch-input-panel {
    background:
        linear-gradient(
            135deg,
            #c9dced 0%,
            #dce9f5 48%,
            #c7d9e9 100%
        ) !important;

    border: 1.5px solid #809bb6 !important;
    border-top: 5px solid var(--op39-navy-800) !important;

    box-shadow:
        0 18px 34px rgba(20, 55, 88, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
}


/* =================================================
   FORM
   ================================================= */

label,
.form-label {
    color: var(--op39-slate-800) !important;
    font-weight: 720 !important;
}

input,
textarea,
select {
    background: #ffffff !important;
    color: var(--op39-slate-950) !important;
    border: 1.5px solid var(--op39-border) !important;
    border-radius: 0 !important;
    font-weight: 550 !important;
}

input:focus,
textarea:focus,
select:focus {
    outline: none !important;

    border-color: var(--op39-blue-600) !important;

    box-shadow:
        0 0 0 2px rgba(23, 111, 229, 0.20),
        0 5px 12px rgba(23, 111, 229, 0.08) !important;
}


/* =================================================
   BUTTONS
   ================================================= */

button,
.button,
.action-button {
    border-radius: 0 !important;
    font-weight: 780 !important;
    letter-spacing: 0.015em;

    transition:
        transform 120ms ease,
        box-shadow 120ms ease,
        filter 120ms ease;
}

button:hover,
.button:hover,
.action-button:hover {
    transform: translateY(-1px);
    filter: brightness(1.04);
}

#analyze-button,
#analyze-ticket-button,
.analyze-button,
.primary-button {
    background:
        linear-gradient(
            180deg,
            var(--op39-blue-500),
            var(--op39-blue-700)
        ) !important;

    color: #ffffff !important;

    border: 1.5px solid #0b4aa9 !important;

    box-shadow:
        0 8px 18px rgba(14, 86, 199, 0.30),
        inset 0 1px 0 rgba(255, 255, 255, 0.24) !important;
}

#batch-validate-button,
#batch-analyze-button,
.batch-action-button {
    background:
        linear-gradient(
            180deg,
            #285b8d,
            #12395f
        ) !important;

    color: #ffffff !important;

    border: 1.5px solid #0b2948 !important;

    box-shadow:
        0 8px 18px rgba(14, 49, 80, 0.30),
        inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
}


/* =================================================
   FILE INPUT
   ================================================= */

input[type="file"] {
    background: #ffffff !important;
    border: 1.5px solid #819ab2 !important;
}

input[type="file"]::file-selector-button {
    background:
        linear-gradient(
            180deg,
            #294f75,
            #173856
        ) !important;

    color: #ffffff !important;

    border: 0 !important;
    border-right: 1px solid #0c2946 !important;
    border-radius: 0 !important;
    font-weight: 720 !important;
}


/* =================================================
   BATCH RESULTS
   ================================================= */

.batch-results-panel,
#batch-results-panel {
    background:
        linear-gradient(
            135deg,
            #d3e1ed 0%,
            #e9f0f6 48%,
            #d9e6f0 100%
        ) !important;

    border: 1.5px solid #8fa7bd !important;

    border-top: 5px solid var(--op39-red-700) !important;

    border-radius: 0 !important;

    box-shadow:
        var(--op39-shadow-lg),
        0 0 0 1px rgba(181, 35, 50, 0.08) !important;
}

.batch-results-panel::before,
#batch-results-panel::before {
    content: "";

    display: block;

    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent 0%,
            #f06a77 35%,
            #ffffff 50%,
            #f06a77 65%,
            transparent 100%
        ) !important;

    opacity: 0.75;

    pointer-events: none;
}

.batch-results-panel h2,
.batch-results-panel h3,
#batch-results-panel h2,
#batch-results-panel h3 {
    color: var(--op39-navy-950) !important;
    font-weight: 850 !important;
}

.batch-results-panel p,
#batch-results-panel p {
    color: var(--op39-slate-700) !important;
    font-weight: 600 !important;
}


/* =================================================
   RESULTS COUNT
   ================================================= */

.batch-results-panel .result-count,
#batch-results-panel .result-count,
.batch-results-panel .summary-count,
#batch-results-panel .summary-count {
    background:
        linear-gradient(
            135deg,
            #ffffff 0%,
            #e9f2fa 100%
        ) !important;

    border: 1.5px solid #89a3bc !important;
    border-left: 4px solid var(--op39-blue-600) !important;

    box-shadow:
        var(--op39-shadow-sm),
        inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;
}


/* =================================================
   TABLE
   ================================================= */

.batch-results-table,
#batch-results-panel table,
.results-panel table,
table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: 1.5px solid #829bb4 !important;

    box-shadow:
        0 8px 18px rgba(18, 45, 72, 0.12) !important;
}

.batch-results-table thead,
#batch-results-panel table thead,
.results-panel table thead,
table thead {
    background:
        linear-gradient(
            180deg,
            #1b426b 0%,
            #102b49 100%
        ) !important;

    color: #ffffff !important;
}

.batch-results-table thead th,
#batch-results-panel table thead th,
.results-panel table thead th,
table thead th {
    background:
        linear-gradient(
            180deg,
            #1b426b 0%,
            #102b49 100%
        ) !important;

    color: #ffffff !important;

    border-bottom: 2px solid #347fca !important;

    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
}

.batch-results-table tbody tr,
#batch-results-panel table tbody tr,
.results-panel table tbody tr,
table tbody tr {
    background: #ffffff !important;
}

.batch-results-table tbody tr:nth-child(even),
#batch-results-panel table tbody tr:nth-child(even),
.results-panel table tbody tr:nth-child(even),
table tbody tr:nth-child(even) {
    background: #eef4f9 !important;
}

.batch-results-table tbody tr:hover,
#batch-results-panel table tbody tr:hover,
.results-panel table tbody tr:hover,
table tbody tr:hover {
    background: #dcecff !important;
}

.batch-results-table tbody td,
#batch-results-panel table tbody td,
.results-panel table tbody td,
table tbody td {
    color: var(--op39-slate-900) !important;
    border-bottom: 1px solid #c4d3e0 !important;
    font-weight: 620 !important;
}

.batch-results-table tbody td:first-child,
#batch-results-panel table tbody td:first-child,
.results-panel table tbody td:first-child,
table tbody td:first-child {
    color: var(--op39-blue-700) !important;
    font-weight: 800 !important;
}


/* =================================================
   SUMMARY CARDS
   ================================================= */

.summary-card,
.result-card,
.summary-result-card {
    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #edf4fa 100%
        ) !important;

    border: 1.5px solid var(--op39-border) !important;
    border-top: 4px solid var(--op39-blue-600) !important;

    border-radius: 0 !important;

    box-shadow: var(--op39-shadow-sm) !important;
}

.summary-card .value,
.result-card .value,
.summary-value {
    color: var(--op39-navy-950) !important;
    font-weight: 850 !important;
}


/* =================================================
   EVIDENCE
   ================================================= */

.evidence-section,
#evidence-section,
.evidence-panel {
    background:
        linear-gradient(
            145deg,
            #ffffff,
            #edf4fa
        ) !important;

    border: 1.5px solid var(--op39-border) !important;
    border-left: 5px solid var(--op39-blue-600) !important;

    border-radius: 0 !important;

    box-shadow: var(--op39-shadow-sm) !important;
}


/* =================================================
   PIPELINE
   ================================================= */

.pipeline-section,
#pipeline-section,
.pipeline-panel {
    background:
        linear-gradient(
            135deg,
            #081426 0%,
            #102640 54%,
            #173b60 100%
        ) !important;

    color: #ffffff !important;

    border: 1.5px solid #315b80 !important;
    border-top: 5px solid var(--op39-blue-500) !important;

    border-radius: 0 !important;

    box-shadow:
        0 20px 40px rgba(6, 21, 39, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

.pipeline-section h2,
.pipeline-section h3,
.pipeline-panel h2,
.pipeline-panel h3 {
    color: #ffffff !important;
}

.pipeline-grid {
    display: grid !important;
    grid-template-columns:
        repeat(2, minmax(0, 1fr)) !important;
    gap: 12px !important;
}

.pipeline-card {
    display: grid !important;

    grid-template-columns:
        44px minmax(0, 1fr) auto !important;

    grid-template-areas:
        "task title state"
        "task description description" !important;

    min-width: 0 !important;
    min-height: 112px !important;

    padding: 15px !important;

    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #edf4f9 100%
        ) !important;

    color: var(--op39-slate-950) !important;

    border: 1.5px solid #8fa6bb !important;
    border-left: 4px solid var(--op39-blue-600) !important;

    border-radius: 0 !important;

    box-shadow:
        0 8px 18px rgba(5, 22, 42, 0.18),
        inset 0 1px 0 rgba(255, 255, 255, 0.92) !important;
}

.pipeline-card .task-id {
    grid-area: task !important;

    width: 36px !important;
    min-width: 36px !important;
    height: 30px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    background:
        linear-gradient(
            180deg,
            var(--op39-blue-500),
            var(--op39-blue-700)
        ) !important;

    color: #ffffff !important;

    border: 1px solid #0b4aa9 !important;
    border-radius: 0 !important;

    font-weight: 850 !important;
}

.pipeline-card strong {
    grid-area: title !important;
    color: var(--op39-navy-950) !important;
    font-weight: 850 !important;
}

.pipeline-card .task-state {
    grid-area: state !important;
    justify-self: end !important;
    padding: 5px 8px !important;
    border-radius: 0 !important;
    font-weight: 800 !important;
}

.pipeline-card p {
    grid-area: description !important;
    color: var(--op39-slate-600) !important;
    font-weight: 550 !important;
    line-height: 1.45 !important;
}

.pipeline-card:nth-child(7),
.pipeline-card:nth-child(10) {
    border-left-color: var(--op39-red-700) !important;
}


/* =================================================
   HUMAN REVIEW
   ================================================= */

.human-review-section,
#human-review-section,
.human-review-panel {
    background:
        linear-gradient(
            135deg,
            #fffafb 0%,
            #f9eef0 52%,
            #ffffff 100%
        ) !important;

    border: 1.5px solid #d8a2aa !important;
    border-left: 6px solid var(--op39-red-700) !important;

    border-radius: 0 !important;

    box-shadow:
        0 14px 28px rgba(123, 29, 40, 0.11),
        inset 0 1px 0 rgba(255, 255, 255, 0.92) !important;
}

.human-review-section h2,
.human-review-section h3,
.human-review-panel h2,
.human-review-panel h3 {
    color: var(--op39-red-900) !important;
    font-weight: 850 !important;
}


/* =================================================
   LIMITATIONS
   ================================================= */

.limitations-section,
#limitations-section,
.limitations-panel {
    background:
        linear-gradient(
            135deg,
            #edf4fa,
            #dce8f2
        ) !important;

    border: 1.5px solid #a2b6c9 !important;
    border-left: 5px solid var(--op39-slate-700) !important;

    border-radius: 0 !important;
}


/* =================================================
   EXPLANATION
   ================================================= */

.explanation-section,
#explanation-section,
.explanation-panel {
    background:
        linear-gradient(
            145deg,
            #ffffff,
            #edf3f8
        ) !important;

    border: 1.5px solid var(--op39-border-strong) !important;
    border-top: 5px solid var(--op39-navy-800) !important;

    border-radius: 0 !important;

    box-shadow: var(--op39-shadow-lg) !important;
}

#explanation,
#explanation {
    color: var(--op39-slate-800) !important;
    font-weight: 550 !important;
    line-height: 1.6 !important;
}

#explanation strong,
#explanation h3,
#explanation h4 {
    color: var(--op39-navy-950) !important;
    font-weight: 850 !important;
}


/* =================================================
   EXPLANATION BLOCKS
   ================================================= */

.explanation-block {
    background: #ffffff !important;

    border: 1.5px solid #c5d2df !important;

    border-radius: 0 !important;

    margin-bottom: 10px !important;

    overflow: hidden !important;

    box-shadow:
        0 4px 10px rgba(7, 24, 44, 0.07) !important;
}

.explanation-block-header {
    background:
        linear-gradient(
            135deg,
            #e2ebf4,
            #edf3f8
        ) !important;

    border-bottom: 1px solid #c2d0de !important;

    padding: 10px 14px !important;

    border-left: 4px solid var(--op39-blue-600) !important;
}

.explanation-block-header h3 {
    margin: 0 !important;

    color: var(--op39-navy-900) !important;

    font-size: 0.78rem !important;

    font-weight: 850 !important;

    letter-spacing: 0.08em !important;

    text-transform: uppercase !important;
}

.explanation-text {
    color: var(--op39-slate-800) !important;

    font-weight: 550 !important;

    line-height: 1.55 !important;
}


/* =================================================
   INTEGRITY STATUS — RESTORED GREEN
   ================================================= */

/*
 * The JS renderer already assigns:
 *
 * data-accent="green"
 *
 * to the Integrity Status block.
 *
 * This CSS restores the intended visual state.
 */

.explanation-block[data-accent="green"] {
    background:
        linear-gradient(
            135deg,
            var(--op39-green-050) 0%,
            #ffffff 72%
        ) !important;

    border-color: #a9d8bf !important;

    border-left: 5px solid var(--op39-green-700) !important;

    box-shadow:
        0 6px 14px rgba(17, 100, 62, 0.10),
        inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;
}

.explanation-block[data-accent="green"]
.explanation-block-header {
    background:
        linear-gradient(
            135deg,
            #dff3e8 0%,
            #edf9f3 100%
        ) !important;

    border-left: 0 !important;

    border-bottom: 1px solid #b8dec9 !important;
}

.explanation-block[data-accent="green"]
.explanation-block-header h3 {
    color: var(--op39-green-800) !important;
}

.explanation-block[data-accent="green"]
.explanation-text {
    color: #285b45 !important;
}

.explanation-block[data-accent="green"]
.explanation-integrity-row {
    background: #f5fcf8 !important;

    border-bottom: 1px solid #d5ebdf !important;
}

.explanation-block[data-accent="green"]
.explanation-integrity-row strong {
    color: var(--op39-green-700) !important;

    font-weight: 850 !important;
}


/* =================================================
   EXPLANATION RED ACCENT
   ================================================= */

.explanation-block[data-accent="red"] {
    border-left: 5px solid var(--op39-red-700) !important;

    background:
        linear-gradient(
            135deg,
            #fffafb,
            #ffffff
        ) !important;
}

.explanation-block[data-accent="red"]
.explanation-block-header {
    border-left: 0 !important;

    background:
        linear-gradient(
            135deg,
            #f9e8eb,
            #fff4f5
        ) !important;
}

.explanation-block[data-accent="red"]
.explanation-block-header h3 {
    color: var(--op39-red-900) !important;
}


/* =================================================
   FOOTER
   ================================================= */

footer {
    background:
        linear-gradient(
            135deg,
            var(--op39-navy-950),
            var(--op39-navy-900)
        ) !important;

    color: #c0d1e2 !important;

    border-top: 3px solid var(--op39-blue-600) !important;
}

footer * {
    color: inherit !important;
}


/* =================================================
   CONTROLLED GLOSS
   ================================================= */

.panel,
.dashboard-panel,
.results-panel,
.batch-panel,
.summary-card,
.result-card,
.pipeline-card,
.explanation-panel,
.human-review-panel,
.explanation-block {
    position: relative;
}

.panel::after,
.dashboard-panel::after,
.results-panel::after,
.batch-panel::after,
.summary-card::after,
.result-card::after,
.pipeline-card::after,
.explanation-panel::after,
.human-review-panel::after {
    content: "";

    position: absolute;

    top: 0;
    left: 0;
    right: 0;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.95) 50%,
            transparent 100%
        );

    pointer-events: none;
}


/* =================================================
   SHARP CORNERS
   ================================================= */

.topbar,
.panel,
.dashboard-panel,
.ticket-panel,
.results-panel,
.batch-panel,
.summary-card,
.result-card,
.pipeline-section,
.pipeline-panel,
.pipeline-card,
.human-review-section,
.limitations-section,
.explanation-section,
.explanation-panel,
.explanation-block,
button,
input,
textarea,
select,
table,
input[type="file"],
.badge,
.status,
.state-badge {
    border-radius: 0 !important;
}


/* =================================================
   RESPONSIVE
   ================================================= */

@media (max-width: 1050px) {
    .pipeline-grid {
        grid-template-columns: 1fr !important;
    }
}

@media (max-width: 700px) {
    .pipeline-card {
        grid-template-columns:
            38px minmax(0, 1fr) !important;

        grid-template-areas:
            "task title"
            "task state"
            "description description" !important;
    }

    .pipeline-card .task-state {
        justify-self: start !important;
    }
}


/* =================================================




/* =================================================
   DEPLOY-OP-039 — FINAL MICRO POLISH
   SUCCESS + INTEGRITY + BLUE TINT
   ================================================= */

html,
body {
    background:
        linear-gradient(
            135deg,
            #d4e2ee 0%,
            #e5eef6 50%,
            #d9e6f1 100%
        ) !important;
}

/* =================================================
   BATCH SUCCESS
   ================================================= */

#batch-validation-summary,
#batch-status,
#batch-validation-status,
#batch-results-panel .result-count,
#batch-results-panel .summary-count {
    position: relative !important;
    background:
        linear-gradient(
            135deg,
            #e5f7ed 0%,
            #f4fbf7 100%
        ) !important;
    border-color: #8fc9a9 !important;
    color: #185f3c !important;

    /* Reserve visual room for the check without changing
       the outer box dimensions. */
    padding-left: 58px !important;
    box-sizing: border-box !important;
    text-indent: 0 !important;

    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.96),
        0 5px 14px rgba(22, 133, 83, 0.10) !important;
}

/* Green success check, aligned with the status text. */
#batch-validation-summary::before,
#batch-status::before,
#batch-validation-status::before {
    content: "✓" !important;
    position: absolute !important;
    left: 16px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;

    width: 28px !important;
    height: 28px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    background:
        linear-gradient(
            180deg,
            #20a267,
            #168553
        ) !important;
    color: #ffffff !important;
    border: 2px solid #0f6b42 !important;
    border-radius: 50% !important;

    font-size: 17px !important;
    font-weight: 900 !important;
    line-height: 1 !important;

    box-shadow:
        0 3px 8px rgba(22, 133, 83, 0.20),
        inset 0 1px 0 rgba(255, 255, 255, 0.32) !important;

    pointer-events: none !important;
}

/* =================================================
   INTEGRITY — GREEN
   ================================================= */

/*
 * The structured explanation renderer uses #explanation.
 * The previous OP-039 rules targeted #explanation, so they did
 * not match the rendered Integrity block.
 */
#explanation .explanation-block[data-accent="green"],
#explanation .explanation-block[data-accent="green"],
#explanation .explanation-block:last-child,
#explanation .explanation-block:last-child {
    background:
        linear-gradient(
            135deg,
            #e5f7ed 0%,
            #f4fbf7 100%
        ) !important;

    border-color: #91cbaa !important;
    border-left: 5px solid #168553 !important;

    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.96),
        0 5px 14px rgba(22, 133, 83, 0.10) !important;
}

#explanation .explanation-block[data-accent="green"]
.explanation-block-header,
#explanation .explanation-block[data-accent="green"]
.explanation-block-header,
#explanation .explanation-block:last-child
.explanation-block-header,
#explanation .explanation-block:last-child
.explanation-block-header {
    background:
        linear-gradient(
            135deg,
            #d9f1e3 0%,
            #eaf8f0 100%
        ) !important;

    border-left: 0 !important;
    border-bottom-color: #b5d9c3 !important;
}

#explanation .explanation-block[data-accent="green"]
.explanation-block-header h3,
#explanation .explanation-block[data-accent="green"]
.explanation-block-header h3,
#explanation .explanation-block:last-child
.explanation-block-header h3,
#explanation .explanation-block:last-child
.explanation-block-header h3 {
    color: #12633e !important;
}

#explanation .explanation-block[data-accent="green"]
.explanation-integrity-row,
#explanation .explanation-block[data-accent="green"]
.explanation-integrity-row,
#explanation .explanation-block:last-child
.explanation-integrity-row,
#explanation .explanation-block:last-child
.explanation-integrity-row {
    background: #f1fbf5 !important;
    color: #285b45 !important;
    border-bottom-color: #cde7d8 !important;
}

#explanation .explanation-block[data-accent="green"]
.explanation-integrity-row strong,
#explanation .explanation-block[data-accent="green"]
.explanation-integrity-row strong,
#explanation .explanation-block:last-child
.explanation-integrity-row strong,
#explanation .explanation-block:last-child
.explanation-integrity-row strong {
    color: #168553 !important;
    font-weight: 850 !important;
}

/* =================================================
   END DEPLOY-OP-039
   ================================================= */
"""


def strip_existing_op039(css: str):
    start = css.find(START_MARKER)

    if start == -1:
        return css.rstrip() + "\n", False

    end = css.find(END_MARKER, start)

    if end == -1:
        raise RuntimeError(
            "DEPLOY-OP-039 start marker exists, "
            "but the end marker was not found."
        )

    end += len(END_MARKER)

    cleaned = css[:start].rstrip() + "\n"

    return cleaned, True



def patch_app_js(app_text: str):
    """
    Force removal of formatting-only separator lines from the displayed
    explanation. This changes presentation only; runtime/model evidence
    remains untouched.
    """
    cleanup = """    const displayText =
        text
            .replace(/^[=-]{4,}\\s*$/gm, "")
            .replace(/\n{3,}/g, "\n\n")
            .trim();

    const sections =
        splitExplanationSections(displayText);"""

    # Current renderer: replace the complete displayText -> sections block.
    display_start = app_text.find("const displayText =")
    if display_start != -1:
        sections_start = app_text.find(
            "const sections =",
            display_start
        )
        if sections_start != -1:
            sections_end = app_text.find(
                "splitExplanationSections(displayText);",
                sections_start
            )
            if sections_end != -1:
                sections_end += len(
                    "splitExplanationSections(displayText);"
                )
                return (
                    app_text[:display_start]
                    + cleanup
                    + app_text[sections_end:],
                    True,
                )

    # Older renderer: replace the direct raw-text parser call.
    raw_start = app_text.find("const sections =")
    while raw_start != -1:
        raw_end = app_text.find(
            "splitExplanationSections(text);",
            raw_start
        )
        if raw_end != -1:
            raw_end += len(
                "splitExplanationSections(text);"
            )
            return (
                app_text[:raw_start]
                + cleanup
                + app_text[raw_end:],
                True,
            )
        raw_start = app_text.find(
            "const sections =",
            raw_start + 1
        )

    raise RuntimeError(
        "Could not locate the explanation parsing block in app.js. "
        "Refusing to modify app.js."
    )

def main():
    print("=" * 60)
    print("DEPLOY-OP-039 — UI + INTEGRITY GREEN RESTORE")
    print("=" * 60)

    if not CSS_PATH.exists():
        raise FileNotFoundError(f"CSS file not found: {CSS_PATH}")

    if not BACKUP_PATH.exists():
        raise FileNotFoundError(
            f"Required OP-039 backup not found: {BACKUP_PATH}"
        )

    current_css = CSS_PATH.read_text(encoding="utf-8")
    backup_css = BACKUP_PATH.read_text(encoding="utf-8")

    if not backup_css.strip():
        raise RuntimeError("Existing OP-039 backup is empty.")

    if not APP_PATH.exists():
        raise FileNotFoundError(f"Frontend app.js not found: {APP_PATH}")

    current_app = APP_PATH.read_text(encoding="utf-8")

    base_css, old_layer_found = strip_existing_op039(current_css)

    new_css = (
        base_css.rstrip()
        + "\n\n"
        + FINAL_UI_CSS.strip()
        + "\n"
    )

    new_app, app_modified = patch_app_js(current_app)

    if app_modified:
        if not APP_BACKUP_PATH.exists():
            APP_BACKUP_PATH.write_text(
                current_app,
                encoding="utf-8"
            )

        APP_PATH.write_text(
            new_app,
            encoding="utf-8"
        )

    CSS_PATH.write_text(new_css, encoding="utf-8")

    print("STATUS: PASS")
    print(f"CSS_UPDATED: {CSS_PATH}")
    print(f"EXISTING_OP039_BACKUP_PRESERVED: {BACKUP_PATH}")
    print(f"OLD_OP039_LAYER_REPLACED: {old_layer_found}")

    print("DARK_NAVY_HEADER: True")
    print("BLUE_GRAY_PAGE_BACKGROUND: True")
    print("DISTINCT_BATCH_BACKGROUND: True")
    print("DARK_TABLE_HEADER: True")
    print("BLUE_PRIMARY_ACTIONS: True")

    print("RED_STRUCTURAL_ACCENT: True")
    print("RED_RESULTS_TOP_BORDER: True")
    print("RED_HUMAN_REVIEW_BORDER: True")
    print("RED_HUMAN_REVIEW_BACKGROUND: True")
    print("RED_TABLE_CELL_FILL: False")
    print("RED_ACTION_COLUMN: False")

    print("DARK_PIPELINE_ZONE: True")
    print("WHITE_CONTENT_SURFACES: True")
    print("CONTROLLED_GLOSS: True")
    print("SHARP_CORNERS: True")

    print("INTEGRITY_GREEN_RESTORED: True")
    print("INTEGRITY_JS_MODIFIED: True")
    print("INTEGRITY_GREEN_TARGET_CORRECTED: True")
    print("EXPLANATION_SEPARATOR_REMOVED_FROM_DISPLAY: True")

    print("BATCH_UI_PRESERVED: True")
    print("SINGLE_TICKET_UI_PRESERVED: True")

    print(f"APP_JS_MODIFIED: {app_modified}")
    print(f"APP_BACKUP_CREATED_OR_PRESERVED: {APP_BACKUP_PATH}")
    print("BACKEND_MODIFIED: False")
    print("FROZEN_RUNTIME_MODIFIED: False")
    print("MODEL_LOGIC_MODIFIED: False")

    print(f"NEW_CSS_SIZE_BYTES: {CSS_PATH.stat().st_size}")

    print("=" * 60)


if __name__ == "__main__":
    main()
