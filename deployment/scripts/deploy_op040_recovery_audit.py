from pathlib import Path
import hashlib
import json
import re
import sys


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
BACKEND = ROOT / "deployment" / "backend"
RUNTIME = (
    ROOT
    / "modeling"
    / "FMP"
    / "deployment"
    / "runtime"
)
METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

APP_JS = FRONTEND / "app.js"
STYLE_CSS = FRONTEND / "style.css"
INDEX_HTML = FRONTEND / "index.html"
BACKEND_APP = BACKEND / "app.py"
PIPELINE = RUNTIME / "ticket_pipeline.py"
EXPLANATION = RUNTIME / "ticket_explanation.py"

BACKUP_APP_OP036 = (
    FRONTEND / "app.js.before-deploy-op036"
)

BACKUP_APP_OP039 = (
    FRONTEND
    / "app.js.before-deploy-op039-final-tweak"
)

BACKUP_CSS_OP039 = (
    FRONTEND / "style.css.before-deploy-op039"
)

EVIDENCE = (
    METRICS / "deploy_op040_recovery_audit.json"
)


def sha256(path: Path):
    if not path.exists():
        return None

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def file_info(path: Path):
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
        }

    return {
        "exists": True,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def read_text(path: Path):
    if not path.exists():
        return ""

    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def contains(text: str, pattern: str):
    return re.search(
        pattern,
        text,
        re.MULTILINE,
    ) is not None


def count_matches(text: str, pattern: str):
    return len(
        re.findall(
            pattern,
            text,
            re.MULTILINE,
        )
    )


def main():
    print("=" * 70)
    print("DEPLOY-OP-040 — READ-ONLY DEPLOYMENT RECOVERY AUDIT")
    print("=" * 70)

    results = {}

    # ------------------------------------------------------------
    # FILE EXISTENCE
    # ------------------------------------------------------------

    print("\n[1] CORE FILE EXISTENCE")

    required_files = {
        "frontend_app_js": APP_JS,
        "frontend_index_html": INDEX_HTML,
        "frontend_style_css": STYLE_CSS,
        "backend_app": BACKEND_APP,
        "frozen_pipeline": PIPELINE,
        "frozen_explanation": EXPLANATION,
    }

    results["files"] = {}

    for name, path in required_files.items():
        info = file_info(path)
        results["files"][name] = info

        print(
            f"{name}: "
            f"{'EXISTS' if info['exists'] else 'MISSING'}"
        )

    # ------------------------------------------------------------
    # BACKUP STATE
    # ------------------------------------------------------------

    print("\n[2] RECOVERY BACKUPS")

    backups = {
        "app_before_op036": BACKUP_APP_OP036,
        "app_before_op039_final_tweak": BACKUP_APP_OP039,
        "css_before_op039": BACKUP_CSS_OP039,
    }

    results["backups"] = {}

    for name, path in backups.items():
        info = file_info(path)
        results["backups"][name] = info

        print(
            f"{name}: "
            f"{'EXISTS' if info['exists'] else 'MISSING'}"
        )

    # ------------------------------------------------------------
    # CURRENT HASHES
    # ------------------------------------------------------------

    print("\n[3] CURRENT SOURCE HASHES")

    results["current_hashes"] = {
        "app_js": sha256(APP_JS),
        "style_css": sha256(STYLE_CSS),
        "index_html": sha256(INDEX_HTML),
        "backend_app": sha256(BACKEND_APP),
        "pipeline": sha256(PIPELINE),
        "explanation": sha256(EXPLANATION),
    }

    for name, value in results["current_hashes"].items():
        print(f"{name}: {value}")

    # ------------------------------------------------------------
    # BACKEND CONTRACT
    # ------------------------------------------------------------

    print("\n[4] BACKEND BATCH CONTRACT")

    backend_text = read_text(BACKEND_APP)

    backend_checks = {
        "health_route": contains(
            backend_text,
            r'@app\.get\(\s*["\']/health["\']',
        ),
        "single_ticket_route": contains(
            backend_text,
            r'@app\.post\(\s*["\']/tickets/analyze["\']',
        ),
        "batch_ticket_route": contains(
            backend_text,
            r'@app\.post\(\s*["\']/tickets/analyze-batch["\']',
        ),
        "predict_present": ".predict(" in backend_text,
        "predict_batch_present": ".predict_batch(" in backend_text,
        "ticket_pipeline_present": (
            "TicketPipeline" in backend_text
        ),
        "ticket_explanation_present": (
            "TicketExplanation" in backend_text
        ),
    }

    results["backend_checks"] = backend_checks

    for name, passed in backend_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # ------------------------------------------------------------
    # FROZEN RUNTIME CONTRACT
    # ------------------------------------------------------------

    print("\n[5] FROZEN RUNTIME CONTRACT")

    pipeline_text = read_text(PIPELINE)
    explanation_text = read_text(EXPLANATION)

    runtime_checks = {
        "predict_present": contains(
            pipeline_text,
            r"def\s+predict\s*\(",
        ),
        "predict_batch_present": contains(
            pipeline_text,
            r"def\s+predict_batch\s*\(",
        ),
        "ticket_pipeline_present": (
            "class TicketPipeline" in pipeline_text
        ),
        "ticket_explanation_present": (
            "TicketExplanation" in explanation_text
            or "def explain" in explanation_text
        ),
    }

    results["runtime_checks"] = runtime_checks

    for name, passed in runtime_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # ------------------------------------------------------------
    # FRONTEND BATCH PATH
    # ------------------------------------------------------------

    print("\n[6] FRONTEND BATCH PATH")

    app_text = read_text(APP_JS)

    frontend_checks = {
        "batch_file_input_reference": (
            "batch-file" in app_text
        ),
        "batch_button_reference": (
            "batch-validate-button" in app_text
            or "batch-analyze-button" in app_text
        ),
        "analyze_batch_function": contains(
            app_text,
            r"async\s+function\s+analyzeBatch\s*\(",
        ),
        "handle_batch_analysis_function": contains(
            app_text,
            r"async\s+function\s+handleBatchAnalysis\s*\(",
        ),
        "render_batch_results_function": contains(
            app_text,
            r"function\s+renderBatchResults\s*\(",
        ),
        "select_batch_ticket_function": contains(
            app_text,
            r"function\s+selectBatchTicket\s*\(",
        ),
        "render_analysis_response_function": contains(
            app_text,
            r"function\s+renderAnalysisResponse\s*\(",
        ),
        "render_pipeline_function": contains(
            app_text,
            r"function\s+renderPipeline\s*\(",
        ),
        "render_explanation_function": contains(
            app_text,
            r"function\s+renderExplanation\s*\(",
        ),
        "batch_api_route_reference": (
            "/tickets/analyze-batch" in app_text
        ),
        "single_api_route_reference": (
            "/tickets/analyze" in app_text
        ),
    }

    results["frontend_checks"] = frontend_checks

    for name, passed in frontend_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # ------------------------------------------------------------
    # CLICK HANDLER EVIDENCE
    # ------------------------------------------------------------

    print("\n[7] BATCH ROW CLICK PATH")

    select_match = re.search(
        r"function\s+selectBatchTicket\s*\("
        r"[\s\S]{0,12000}?"
        r"\n\}",
        app_text,
        re.MULTILINE,
    )

    select_block = (
        select_match.group(0)
        if select_match
        else ""
    )

    click_checks = {
        "select_function_found": bool(select_match),
        "select_calls_render_analysis_response": (
            "renderAnalysisResponse" in select_block
        ),
        "select_uses_batch_response": (
            "currentBatchResponse" in select_block
            or "currentBatchTickets" in select_block
        ),
        "row_click_listener_present": (
            "addEventListener" in app_text
            and '"click"' in app_text
        ),
        "keyboard_support_present": (
            "keydown" in app_text
        ),
    }

    results["click_checks"] = click_checks

    for name, passed in click_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if select_block:
        print("\n--- SELECT BATCH TICKET FUNCTION ---")
        print(select_block[:6000])

    # ------------------------------------------------------------
    # RESPONSE RENDERER
    # ------------------------------------------------------------

    print("\n[8] DETAIL RESPONSE RENDERER")

    renderer_match = re.search(
        r"function\s+renderAnalysisResponse\s*\("
        r"[\s\S]{0,16000}?"
        r"\n\}",
        app_text,
        re.MULTILINE,
    )

    renderer_block = (
        renderer_match.group(0)
        if renderer_match
        else ""
    )

    renderer_checks = {
        "renderer_found": bool(renderer_match),
        "renderer_calls_summary": (
            "renderSummary" in renderer_block
        ),
        "renderer_calls_evidence": (
            "renderEvidence" in renderer_block
        ),
        "renderer_calls_pipeline": (
            "renderPipeline" in renderer_block
        ),
        "renderer_calls_review": (
            "renderReviewBoundary" in renderer_block
        ),
        "renderer_calls_explanation": (
            "renderExplanation" in renderer_block
        ),
        "renderer_shows_results": (
            "showResults" in renderer_block
        ),
    }

    results["renderer_checks"] = renderer_checks

    for name, passed in renderer_checks.items():
        print(
            f"{name}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # ------------------------------------------------------------
    # OP-039 EXPLANATION CHANGE DETECTION
    # ------------------------------------------------------------

    print("\n[9] OP-039 EXPLANATION CHANGE DETECTION")

    explanation_change_checks = {
        "integrity_wrapper_present": (
            "op39-integrity-display" in app_text
        ),
        "plain_text_explanation_assignment_present": (
            "explanationElement.textContent" in app_text
        ),
        "split_explanation_sections_present": (
            "splitExplanationSections" in app_text
        ),
        "render_explanation_section_present": (
            "renderExplanationSection" in app_text
        ),
    }

    results["explanation_change_checks"] = (
        explanation_change_checks
    )

    for name, passed in explanation_change_checks.items():
        print(
            f"{name}: "
            f"{'PRESENT' if passed else 'ABSENT'}"
        )

    # ------------------------------------------------------------
    # JS STRUCTURE COUNTS
    # ------------------------------------------------------------

    print("\n[10] JAVASCRIPT STRUCTURE COUNTS")

    structure_counts = {
        "renderAnalysisResponse": count_matches(
            app_text,
            r"function\s+renderAnalysisResponse\s*\(",
        ),
        "selectBatchTicket": count_matches(
            app_text,
            r"function\s+selectBatchTicket\s*\(",
        ),
        "renderPipeline": count_matches(
            app_text,
            r"function\s+renderPipeline\s*\(",
        ),
        "renderExplanation": count_matches(
            app_text,
            r"function\s+renderExplanation\s*\(",
        ),
        "analyzeBatch": count_matches(
            app_text,
            r"async\s+function\s+analyzeBatch\s*\(",
        ),
    }

    results["structure_counts"] = structure_counts

    for name, count in structure_counts.items():
        print(f"{name}: {count}")

    # ------------------------------------------------------------
    # BACKUP COMPARISON
    # ------------------------------------------------------------

    print("\n[11] APP.JS BACKUP COMPARISON")

    backup_comparison = {}

    if BACKUP_APP_OP036.exists():
        backup_comparison["current_equals_op036"] = (
            sha256(APP_JS)
            == sha256(BACKUP_APP_OP036)
        )
    else:
        backup_comparison["current_equals_op036"] = None

    if BACKUP_APP_OP039.exists():
        backup_comparison["current_equals_op039_final_tweak"] = (
            sha256(APP_JS)
            == sha256(BACKUP_APP_OP039)
        )
    else:
        backup_comparison[
            "current_equals_op039_final_tweak"
        ] = None

    results["backup_comparison"] = backup_comparison

    for name, value in backup_comparison.items():
        print(f"{name}: {value}")

    # ------------------------------------------------------------
    # READ-ONLY GUARANTEE
    # ------------------------------------------------------------

    print("\n[12] READ-ONLY GUARANTEE")

    results["read_only"] = True
    results["files_modified"] = False
    results["backend_modified"] = False
    results["frontend_modified"] = False
    results["runtime_modified"] = False
    results["model_modified"] = False

    print("FILES_MODIFIED: FALSE")
    print("BACKEND_MODIFIED: FALSE")
    print("FRONTEND_MODIFIED: FALSE")
    print("FROZEN_RUNTIME_MODIFIED: FALSE")
    print("MODEL_MODIFIED: FALSE")

    # ------------------------------------------------------------
    # OVERALL
    # ------------------------------------------------------------

    critical_checks = [
        *backend_checks.values(),
        *runtime_checks.values(),
        frontend_checks[
            "select_batch_ticket_function"
        ],
        frontend_checks[
            "render_analysis_response_function"
        ],
        frontend_checks[
            "render_pipeline_function"
        ],
    ]

    overall_pass = all(critical_checks)

    results["overall"] = (
        "PASS"
        if overall_pass
        else "INVESTIGATION_REQUIRED"
    )

    print("\n" + "=" * 70)
    print(
        "DEPLOY-OP-040 STATUS: "
        + results["overall"]
    )
    print("=" * 70)

    # ------------------------------------------------------------
    # EVIDENCE WRITE
    # ------------------------------------------------------------

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE.write_text(
        json.dumps(
            results,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print(f"\nEVIDENCE: {EVIDENCE}")
    print("READ_ONLY: TRUE")
    print("NO SOURCE FILES MODIFIED: TRUE")


if __name__ == "__main__":
    main()