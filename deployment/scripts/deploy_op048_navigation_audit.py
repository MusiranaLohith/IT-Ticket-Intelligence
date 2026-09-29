from pathlib import Path
import hashlib
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"FAIL: required file missing: {path}")


def count(text: str, marker: str) -> int:
    return text.count(marker)


print("=" * 58)
print("DEPLOY-OP-048 — NAVIGATION SIMPLIFICATION AUDIT")
print("=" * 58)

for path in (INDEX, APP, STYLE):
    require_file(path)

index_text = INDEX.read_text(encoding="utf-8")
app_text = APP.read_text(encoding="utf-8")
style_text = STYLE.read_text(encoding="utf-8")

before_hashes = {
    "index.html": sha256(INDEX),
    "app.js": sha256(APP),
    "style.css": sha256(STYLE),
}

print("READ_ONLY: TRUE")
print("SOURCE_FILES_MODIFIED: FALSE")
print()

print("[1] CURRENT NAVIGATION ELEMENTS")
print("-" * 58)

navigation_markers = [
    "enter-system-button",
    "view-research-button",
    "open-single-ticket-button",
    "open-batch-analysis-button",
    "analysis-home-button",
    "project-overview-button",
    "reset-dashboard-button",
]

for marker in navigation_markers:
    print(
        f"{marker:<32} "
        f"HTML={count(index_text, marker):<3} "
        f"APP.JS={count(app_text, marker):<3}"
    )

print()
print("[2] CURRENT WORKSPACE CONTRACT")
print("-" * 58)

workspace_markers = [
    "analysis-workspace",
    "single-ticket-panel",
    "batch-file",
    "batch-results-panel",
    "results-panel",
    "batch-results-table",
    "evidence-content",
    "pipeline-content",
    "human-review-content",
    "limitations-content",
    "explanation-content",
]

for marker in workspace_markers:
    print(
        f"{marker:<32} "
        f"HTML={count(index_text, marker):<3}"
    )

print()
print("[3] API / PIPELINE SAFETY")
print("-" * 58)

safety_checks = {
    "SINGLE_API": "/tickets/analyze" in app_text,
    "BATCH_API": "/tickets/analyze-batch" in app_text,
    "BATCH_SELECTION": "selectBatchTicket" in app_text,
    "DETAIL_RENDERER": "renderAnalysisResponse" in app_text,
    "FRONTEND_TICKET_PIPELINE_ABSENT": "TicketPipeline" not in app_text,
    "FRONTEND_SKLEARN_ABSENT": "sklearn" not in app_text,
    "FRONTEND_PREDICT_BATCH_ABSENT": "predict_batch(" not in app_text,
}

for name, passed in safety_checks.items():
    print(f"{name:<40}: {'PASS' if passed else 'FAIL'}")

print()
print("[4] EXACT NAVIGATION REFERENCES")
print("-" * 58)

for marker in (
    "open-single-ticket-button",
    "open-batch-analysis-button",
):
    print()
    print(f"MARKER: {marker}")

    index_lines = [
        (i + 1, line.strip())
        for i, line in enumerate(index_text.splitlines())
        if marker in line
    ]

    app_lines = [
        (i + 1, line.strip())
        for i, line in enumerate(app_text.splitlines())
        if marker in line
    ]

    print("HTML:")
    for line_no, line in index_lines:
        print(f"  {line_no}: {line}")

    print("APP.JS:")
    for line_no, line in app_lines:
        print(f"  {line_no}: {line}")

print()
print("[5] SOURCE INTEGRITY")
print("-" * 58)

after_hashes = {
    "index.html": sha256(INDEX),
    "app.js": sha256(APP),
    "style.css": sha256(STYLE),
}

integrity_pass = before_hashes == after_hashes

print(f"INDEX_HASH_UNCHANGED:  {before_hashes['index.html'] == after_hashes['index.html']}")
print(f"APP_HASH_UNCHANGED:    {before_hashes['app.js'] == after_hashes['app.js']}")
print(f"STYLE_HASH_UNCHANGED:  {before_hashes['style.css'] == after_hashes['style.css']}")
print(f"READ_ONLY_INTEGRITY:   {integrity_pass}")

print()
print("[6] EVIDENCE")
print("-" * 58)

METRICS.mkdir(parents=True, exist_ok=True)

evidence = {
    "operation": "DEPLOY-OP-048",
    "title": "Navigation Simplification Audit",
    "status": "PASS" if integrity_pass and all(safety_checks.values()) else "FAIL",
    "read_only": True,
    "source_files_modified": False,
    "navigation_markers": {
        marker: {
            "html_count": count(index_text, marker),
            "app_js_count": count(app_text, marker),
        }
        for marker in navigation_markers
    },
    "workspace_markers": {
        marker: count(index_text, marker)
        for marker in workspace_markers
    },
    "safety_checks": safety_checks,
    "sha256": before_hashes,
}

evidence_path = METRICS / "deploy_op048_navigation_audit.json"
evidence_path.write_text(
    json.dumps(evidence, indent=2),
    encoding="utf-8",
)

print(f"EVIDENCE_WRITTEN: {evidence_path}")

print()
print("=" * 58)
print(
    "STATUS:",
    evidence["status"],
)
print("=" * 58)
