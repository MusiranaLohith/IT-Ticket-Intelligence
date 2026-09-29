from pathlib import Path


FRONTEND = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/deployment/frontend"
)

CSS = FRONTEND / "style.css"
BACKUP = FRONTEND / "style.css.before-deploy-op037"


if not CSS.exists():
    raise SystemExit(
        f"FAIL: style.css not found: {CSS}"
    )


current = CSS.read_text(
    encoding="utf-8"
)


if BACKUP.exists():
    raise SystemExit(
        f"FAIL: backup already exists: {BACKUP}"
    )


BACKUP.write_text(
    current,
    encoding="utf-8"
)


FINAL_UI_CSS = r"""

/* =========================================================
   DEPLOY-OP-037
   FINAL SHARP / GLOSSY UI POLISH
   =========================================================

   Scope:
   - Presentation only.
   - No application logic.
   - No API logic.
   - No model logic.
   - No TicketPipeline logic.
   - No TicketExplanation data modification.

   This layer intentionally overrides the earlier visual layer
   instead of replacing the existing stylesheet. This preserves
   the already-tested dashboard styling and behavior.
   ========================================================= */


/* =========================================================
   SHARP ENGINEERING DESIGN TOKENS
   ========================================================= */

:root {

    --ui-sharp-radius: 0px;

    --ui-border:
        #cbd5e1;

    --ui-border-strong:
        #aebdce;

    --ui-surface:
        #ffffff;

    --ui-surface-soft:
        #f6f8fb;

    --ui-surface-deep:
        #eef2f6;

    --ui-text:
        #172033;

    --ui-text-soft:
        #536174;

    --ui-blue:
        #2167e8;

    --ui-blue-dark:
        #174fb7;

    --ui-blue-soft:
        #edf4ff;

    --ui-amber:
        #b66a00;

    --ui-amber-soft:
        #fff7e8;

    --ui-green:
        #16764a;

    --ui-green-soft:
        #eef9f3;

    --ui-red:
        #b42318;

    --ui-red-soft:
        #fff1ef;

    --ui-shadow:
        0 8px 24px rgba(
            18,
            31,
            52,
            0.075
        );

    --ui-shadow-small:
        0 2px 8px rgba(
            18,
            31,
            52,
            0.055
        );
}


/* =========================================================
   GLOBAL SHARP CORNERS
   ========================================================= */

.panel,
.subpanel,
.result-card,
.batch-results-table-wrapper,
.batch-file-area,
.batch-input-information,
.batch-results-table,
input,
textarea,
select,
button,
.error-message,
.evidence-note,
.explanation-content,
.explanation-block,
.decision-boundary-message,
.review-step,
.form-actions,
.prototype-status {
    border-radius: 0 !important;
}


/* =========================================================
   BODY / BACKGROUND
   ========================================================= */

body {

    background:
        linear-gradient(
            180deg,
            #e8edf3 0%,
            #f5f7fa 34%,
            #edf1f5 100%
        );

    color:
        var(--ui-text);
}


/* =========================================================
   TOP BAR
   ========================================================= */

.topbar {

    border-bottom:
        1px solid
        var(--ui-border-strong);

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f4f7fa 100%
        );

    box-shadow:
        0 4px 16px
        rgba(
            18,
            31,
            52,
            0.07
        );
}


.brand-title {

    letter-spacing:
        -0.025em;
}


.prototype-status {

    border:
        1px solid
        var(--ui-border-strong) !important;

    background:
        linear-gradient(
            180deg,
            #f8fafc,
            #edf1f5
        ) !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.95
        ),
        var(--ui-shadow-small);
}


/* =========================================================
   PANELS
   ========================================================= */

.panel {

    border:
        1px solid
        var(--ui-border) !important;

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f8fafc 100%
        ) !important;

    box-shadow:
        var(--ui-shadow) !important;
}


/* =========================================================
   SECTION HEADERS
   ========================================================= */

.section-header {

    border-bottom:
        1px solid
        #dfe5ec;
}


.section-tag {

    border-radius:
        0 !important;

    border:
        1px solid
        #c5d2e0;

    background:
        #eef3f8;

    color:
        #415268;
}


/* =========================================================
   FORM CONTROLS
   ========================================================= */

input,
textarea,
select {

    border:
        1px solid
        var(--ui-border-strong) !important;

    background:
        #ffffff !important;

    color:
        var(--ui-text) !important;

    box-shadow:
        inset 0 1px 2px
        rgba(
            18,
            31,
            52,
            0.035
        );
}


input:focus,
textarea:focus,
select:focus {

    outline:
        2px solid
        rgba(
            33,
            103,
            232,
            0.16
        );

    outline-offset:
        0;

    border-color:
        var(--ui-blue) !important;

    box-shadow:
        0 0 0 1px
        var(--ui-blue);
}


/* =========================================================
   BUTTONS
   ========================================================= */

button {

    border-radius:
        0 !important;

    border:
        1px solid
        var(--ui-blue-dark) !important;

    background:
        linear-gradient(
            180deg,
            #2c73ef 0%,
            #1d5fd7 100%
        ) !important;

    color:
        #ffffff !important;

    box-shadow:
        0 3px 9px
        rgba(
            23,
            79,
            183,
            0.22
        ),
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.20
        );

    font-weight:
        800;

    letter-spacing:
        0.035em;

    transition:
        transform 120ms ease,
        box-shadow 120ms ease,
        filter 120ms ease;
}


button:hover:not(:disabled) {

    filter:
        brightness(1.035);

    box-shadow:
        0 5px 14px
        rgba(
            23,
            79,
            183,
            0.26
        ),
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.22
        );
}


button:active:not(:disabled) {

    transform:
        translateY(1px);
}


button:disabled {

    cursor:
        not-allowed;

    opacity:
        0.52;

    filter:
        grayscale(0.2);
}


/* =========================================================
   RESULT CARDS
   ========================================================= */

.result-card {

    border:
        1px solid
        var(--ui-border) !important;

    background:
        linear-gradient(
            180deg,
            #ffffff,
            #f4f7fa
        ) !important;

    box-shadow:
        var(--ui-shadow-small) !important;
}


/* =========================================================
   BATCH RESULT TABLE
   ========================================================= */

.batch-results-table-wrapper {

    border:
        1px solid
        var(--ui-border) !important;

    background:
        #ffffff !important;

    box-shadow:
        var(--ui-shadow-small);
}


.batch-results-table {

    border-collapse:
        collapse;
}


.batch-results-table th {

    background:
        linear-gradient(
            180deg,
            #edf2f7,
            #e3e9f0
        ) !important;

    border-bottom:
        1px solid
        var(--ui-border-strong) !important;

    color:
        #34445a !important;

    font-weight:
        800;

    letter-spacing:
        0.035em;
}


.batch-results-table td {

    border-bottom:
        1px solid
        #e2e7ed !important;

    background:
        #ffffff;
}


.batch-results-table tbody tr {

    transition:
        background 100ms ease;
}


.batch-results-table tbody tr:hover {

    background:
        #f3f7fc !important;
}


/* =========================================================
   BATCH TICKET ID / SELECTABLE ROW
   ========================================================= */

.batch-results-table tbody tr {

    cursor:
        pointer;
}


.batch-results-table tbody tr:focus {

    outline:
        2px solid
        var(--ui-blue);

    outline-offset:
        -2px;
}


/* =========================================================
   RESULT SUMMARY
   ========================================================= */

#summary-category,
#summary-priority,
#summary-severity,
#summary-evidence-state,
#summary-action,
#summary-lifecycle {

    border-radius:
        0 !important;
}


/* =========================================================
   EVIDENCE
   ========================================================= */

.evidence-list,
.evidence-item {

    border-radius:
        0 !important;
}


.evidence-item {

    border:
        1px solid
        #d7e0e9;

    background:
        linear-gradient(
            180deg,
            #ffffff,
            #f7f9fb
        );

    box-shadow:
        0 2px 7px
        rgba(
            18,
            31,
            52,
            0.035
        );
}


/* =========================================================
   PIPELINE TRACE
   ========================================================= */

.pipeline-content,
#pipeline-content {

    border-radius:
        0 !important;
}


.pipeline-step {

    border-radius:
        0 !important;
}


/* =========================================================
   HUMAN REVIEW BOUNDARY
   ========================================================= */

.decision-boundary-message {

    border:
        1px solid
        #e1c98e !important;

    background:
        linear-gradient(
            180deg,
            #fffdf7,
            #fff8e9
        ) !important;

    box-shadow:
        0 3px 10px
        rgba(
            118,
            82,
            15,
            0.055
        );
}


.review-step {

    border:
        1px solid
        #dfcfaa !important;

    background:
        #ffffff !important;
}


/* =========================================================
   LIMITATIONS
   ========================================================= */

#limitations-content {

    border-radius:
        0 !important;
}


#limitations-content > * {

    border-radius:
        0 !important;
}


/* =========================================================
   EXPLANATION CONTAINER
   ========================================================= */

.explanation-content {

    max-height:
        760px;

    overflow-y:
        auto;

    margin:
        0;

    padding:
        0;

    background:
        linear-gradient(
            180deg,
            #f3f6f9 0%,
            #eef2f6 100%
        ) !important;

    border:
        1px solid
        #cbd5df !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.95
        ),
        0 6px 18px
        rgba(
            18,
            31,
            52,
            0.055
        );

    scrollbar-color:
        #9daabb
        #e7ecf1;
}


/* =========================================================
   STRUCTURED EXPLANATION BLOCKS
   ========================================================= */

.explanation-block {

    position:
        relative;

    margin:
        0;

    padding:
        0;

    border:
        0 !important;

    border-bottom:
        1px solid
        #cfd8e2 !important;

    background:
        #ffffff !important;

    box-shadow:
        none !important;

    border-radius:
        0 !important;
}


.explanation-block:last-child {

    border-bottom:
        0 !important;
}


/* =========================================================
   EXPLANATION BLOCK TITLE
   ========================================================= */

.explanation-block-title {

    display:
        flex;

    align-items:
        center;

    min-height:
        42px;

    padding:
        10px 16px;

    border-bottom:
        1px solid
        #d6dee7;

    background:
        linear-gradient(
            180deg,
            #eef3f7 0%,
            #e5ebf1 100%
        );

    color:
        #2d4056;

    font-size:
        11px;

    font-weight:
        900;

    letter-spacing:
        0.095em;

    text-transform:
        uppercase;
}


/* =========================================================
   EXPLANATION BLOCK CONTENT
   ========================================================= */

.explanation-block-content {

    margin:
        0;

    padding:
        15px 18px 17px;

    color:
        #344256;

    font-size:
        13px;

    line-height:
        1.68;

    white-space:
        pre-wrap;

    overflow-wrap:
        anywhere;

    word-break:
        normal;

    background:
        #ffffff;
}


/* =========================================================
   TICKET BLOCK
   ========================================================= */

.explanation-block:first-child
.explanation-block-content {

    color:
        #174fb7;

    font-weight:
        900;

    font-size:
        14px;

    letter-spacing:
        0.025em;

    background:
        linear-gradient(
            180deg,
            #f5f9ff,
            #edf4ff
        );
}


/* =========================================================
   EXPLANATION EMPHASIS
   ========================================================= */

.explanation-block:nth-child(2)
.explanation-block-title {

    background:
        linear-gradient(
            180deg,
            #fff5f3,
            #ffefec
        );

    color:
        var(--ui-red);

    border-bottom-color:
        #ebd0cb;
}


.explanation-block:nth-child(3)
.explanation-block-title {

    background:
        linear-gradient(
            180deg,
            #fff9ed,
            #fff2d9
        );

    color:
        var(--ui-amber);

    border-bottom-color:
        #ead7ad;
}


/* =========================================================
   T4–T7 EVIDENCE SECTIONS
   ========================================================= */

.explanation-block-title {

    position:
        relative;
}


.explanation-block-title::before {

    content:
        "";

    display:
        inline-block;

    width:
        3px;

    height:
        18px;

    margin-right:
        9px;

    background:
        var(--ui-blue);
}


/* =========================================================
   DECISION / MATURITY / INTEGRITY
   ========================================================= */

.explanation-block:nth-last-child(1)
.explanation-block-title {

    background:
        linear-gradient(
            180deg,
            #eef8f2,
            #e5f3eb
        );

    color:
        var(--ui-green);

    border-bottom-color:
        #c9dfd2;
}


/* =========================================================
   RAW EXPLANATION FALLBACK
   ========================================================= */

.explanation-raw {

    margin:
        0;

    padding:
        18px;

    border:
        0;

    background:
        #ffffff;

    color:
        #344256;

    font-family:
        inherit;

    font-size:
        13px;

    line-height:
        1.68;

    white-space:
        pre-wrap;

    overflow-wrap:
        anywhere;
}


/* =========================================================
   EMPTY EXPLANATION
   ========================================================= */

.explanation-empty {

    margin:
        0;

    padding:
        24px;

    background:
        #ffffff;

    color:
        #68778a;

    font-size:
        13px;

    text-align:
        center;
}


/* =========================================================
   ERROR STATES
   ========================================================= */

.error-message {

    border:
        1px solid
        #e1bdb8 !important;

    background:
        linear-gradient(
            180deg,
            #fff5f3,
            #ffedeb
        ) !important;

    color:
        var(--ui-red) !important;
}


/* =========================================================
   FILE INPUT
   ========================================================= */

input[type="file"] {

    padding:
        9px;

    background:
        #f8fafc !important;
}


input[type="file"]::file-selector-button {

    margin-right:
        10px;

    padding:
        8px 12px;

    border:
        1px solid
        #9eafc2;

    border-radius:
        0;

    background:
        linear-gradient(
            180deg,
            #f7f9fb,
            #e7edf3
        );

    color:
        #33445a;

    font-weight:
        800;

    cursor:
        pointer;
}


/* =========================================================
   SCROLLBARS
   ========================================================= */

.explanation-content::-webkit-scrollbar {

    width:
        10px;
}


.explanation-content::-webkit-scrollbar-track {

    background:
        #e7ecf1;
}


.explanation-content::-webkit-scrollbar-thumb {

    background:
        #9daabb;

    border:
        2px solid
        #e7ecf1;
}


.explanation-content::-webkit-scrollbar-thumb:hover {

    background:
        #8292a6;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {

    border-top:
        1px solid
        var(--ui-border-strong);

    background:
        linear-gradient(
            180deg,
            #f4f7fa,
            #e9eef3
        );
}


/* =========================================================
   MOBILE SAFETY
   ========================================================= */

@media (max-width: 760px) {

    .panel {

        box-shadow:
            0 4px 14px
            rgba(
                18,
                31,
                52,
                0.06
            ) !important;
    }


    .explanation-block-content {

        padding:
            13px 14px 15px;

        font-size:
            12.5px;
    }


    .explanation-block-title {

        min-height:
            40px;

        padding:
            9px 13px;

        font-size:
            10px;
    }
}


/* =========================================================
   END DEPLOY-OP-037
   ========================================================= */
"""


new_source = (
    current.rstrip()
    + "\n\n"
    + FINAL_UI_CSS.lstrip()
    + "\n"
)


CSS.write_text(
    new_source,
    encoding="utf-8"
)


print("============================================================")
print("DEPLOY-OP-037 — FINAL UI POLISH")
print("============================================================")
print("STATUS: PASS")
print(f"CSS_UPDATED: {CSS}")
print(f"BACKUP_CREATED: {BACKUP}")
print("EXISTING_CSS_PRESERVED: True")
print("SHARP_CORNERS_APPLIED: True")
print("GLOSSY_UI_LAYER_APPLIED: True")
print("EXPLANATION_STYLING_APPLIED: True")
print("BATCH_UI_STYLING_PRESERVED: True")
print("SINGLE_TICKET_UI_STYLING_PRESERVED: True")
print("BACKEND_MODIFIED: False")
print("APP_JS_MODIFIED: False")
print("FROZEN_RUNTIME_MODIFIED: False")
print("MODEL_LOGIC_MODIFIED: False")
print(f"NEW_CSS_SIZE_BYTES: {CSS.stat().st_size}")
print("============================================================")