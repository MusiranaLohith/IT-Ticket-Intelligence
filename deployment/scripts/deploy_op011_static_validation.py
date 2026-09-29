from pathlib import Path
import re


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = (
    ROOT
    / "deployment"
    / "frontend"
)

HTML_PATH = FRONTEND / "index.html"
JS_PATH = FRONTEND / "app.js"


html = HTML_PATH.read_text(
    encoding="utf-8"
)

js = JS_PATH.read_text(
    encoding="utf-8"
)


# Remove JavaScript comments before checking
# implementation boundaries.
js_without_comments = re.sub(
    r"/\*.*?\*/",
    "",
    js,
    flags=re.DOTALL
)

js_without_comments = re.sub(
    r"//.*",
    "",
    js_without_comments
)


checks = {

    "INDEX_EXISTS":
        HTML_PATH.exists(),

    "APP_EXISTS":
        JS_PATH.exists(),

    "SINGLE_TICKET_FORM":
        'id="ticket-form"' in html,

    "SIX_TICKET_FIELDS":
        all(
            f'id="{field}"' in html
            for field in [
                "ticket_id",
                "creation_time",
                "creator",
                "creator_detail",
                "summary",
                "description",
            ]
        ),

    "BATCH_INPUT":
        'id="batch-file"' in html,

    "BATCH_VALIDATE_BUTTON":
        'id="batch-validate-button"' in html,

    "BATCH_RESULTS_PANEL":
        'id="batch-results-panel"' in html,

    "BATCH_RESULTS_TABLE":
        'id="batch-results-table"' in html,

    "BATCH_RESULTS_BODY":
        'id="batch-results-table-body"' in html,

    "BATCH_ROW_RENDERING":
        "createBatchResultRow" in js,

    "BATCH_RESULT_RENDERING":
        "renderBatchResults" in js,

    # Whitespace-independent check that the selected
    # batch result is sent through the same detailed
    # rendering function used by single-ticket analysis.
    "SINGLE_DETAIL_REUSE":
        re.search(
            r"renderAnalysisResponse\s*\(\s*ticketResponse\s*\)",
            js
        ) is not None,

    "SINGLE_API_PRESERVED":
        "/tickets/analyze" in js,

    "BATCH_API_PRESENT":
        "/tickets/analyze-batch" in js,

    # Check executable JavaScript rather than comments.
    "PREDICT_BATCH_NOT_IN_FRONTEND":
        "predict_batch" not in js_without_comments,

    "TICKET_PIPELINE_NOT_IN_FRONTEND":
        "TicketPipeline" not in js_without_comments,

    "NO_SKLEARN":
        "sklearn" not in js_without_comments.lower(),

    "NO_CONFIDENCE_FABRICATION":
        "confidence_score" not in js_without_comments.lower(),

    "NO_RISK_FABRICATION":
        "risk_score" not in js_without_comments.lower(),
}


for name, passed in checks.items():

    print(
        f'[{"PASS" if passed else "FAIL"}] {name}'
    )


print("=" * 60)


if all(checks.values()):

    print(
        "DEPLOY-OP-011 STATIC VALIDATION: PASS"
    )

else:

    print(
        "DEPLOY-OP-011 STATIC VALIDATION: FAIL"
    )

    raise SystemExit(1)