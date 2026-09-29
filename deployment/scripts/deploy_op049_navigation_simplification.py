from pathlib import Path
import hashlib
import json
import shutil
import subprocess


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

INDEX_BACKUP = FRONTEND / "index.html.before-deploy-op049-final"
APP_BACKUP = FRONTEND / "app.js.before-deploy-op049-final"
STYLE_BACKUP = FRONTEND / "style.css.before-deploy-op049-final"


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def require_file(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"FAIL: required file missing: {path}")


def replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"FAIL: {description}: expected exactly one match, "
            f"found {count}"
        )

    return text.replace(old, new, 1)


print("=" * 64)
print("DEPLOY-OP-049 — NAVIGATION SIMPLIFICATION")
print("=" * 64)
print()

for path in (INDEX, APP, STYLE):
    require_file(path)

original_index = INDEX.read_text(encoding="utf-8")
original_app = APP.read_text(encoding="utf-8")
original_style_hash = sha256(STYLE)

print("[1] SOURCE CONTRACT")
print("-" * 64)

# ------------------------------------------------------------
# Exact HTML blocks from the verified source inspection
# ------------------------------------------------------------

single_button_block = """                    <button
                        type="button"
                        id="open-single-ticket-button"
                        class="workspace-entry-action"
                    >
                        OPEN SINGLE TICKET
                    </button>
"""

batch_button_block = """                    <button
                        type="button"
                        id="open-batch-analysis-button"
                        class="workspace-entry-action"
                    >
                        OPEN BATCH ANALYSIS
                    </button>
"""

workspace_information_marker = """        <div class="workspace-information-grid">
"""

# ------------------------------------------------------------
# Exact JS declarations from verified source inspection
# ------------------------------------------------------------

single_declaration = """    const openSingleButton =
        document.getElementById(
            "open-single-ticket-button"
        );

"""

batch_declaration = """    const openBatchButton =
        document.getElementById(
            "open-batch-analysis-button"
        );

"""

# ------------------------------------------------------------
# Exact JS listener blocks from verified source inspection
# ------------------------------------------------------------

single_listener = """    if (openSingleButton) {
        openSingleButton.addEventListener(
            "click",
            () => {
                showAnalysisWorkspace(
                    "single-ticket-panel"
                );
            }
        );
    }


"""

batch_listener = """    if (openBatchButton) {
        openBatchButton.addEventListener(
            "click",
            () => {
                showAnalysisWorkspace(
                    "batch-input-panel"
                );
            }
        );
    }


"""

view_research_declaration = """    const viewResearchButton =
        document.getElementById(
            "view-research-button"
        );

"""

analysis_home_anchor = """    if (analysisHomeButton) {
"""

shared_declaration = """    const openAnalysisWorkspaceButton =
        document.getElementById(
            "open-analysis-workspace-button"
        );

"""

shared_listener = """    if (openAnalysisWorkspaceButton) {
        openAnalysisWorkspaceButton.addEventListener(
            "click",
            showAnalysisWorkspace
        );
    }


"""

# ------------------------------------------------------------
# Verify every exact source block BEFORE creating backups
# ------------------------------------------------------------

required_source_blocks = {
    "HTML_SINGLE_BUTTON": single_button_block,
    "HTML_BATCH_BUTTON": batch_button_block,
    "HTML_WORKSPACE_INSERTION_POINT": workspace_information_marker,
    "JS_SINGLE_DECLARATION": single_declaration,
    "JS_BATCH_DECLARATION": batch_declaration,
    "JS_SINGLE_LISTENER": single_listener,
    "JS_BATCH_LISTENER": batch_listener,
    "JS_VIEW_RESEARCH_DECLARATION": view_research_declaration,
    "JS_ANALYSIS_HOME_ANCHOR": analysis_home_anchor,
}

for name, marker in required_source_blocks.items():
    count = (
        original_index.count(marker)
        if name.startswith("HTML_")
        else original_app.count(marker)
    )

    if count != 1:
        raise RuntimeError(
            f"FAIL: {name}: expected exactly one match, found {count}"
        )

    print(f"{name:<38}: FOUND")

print()

# ------------------------------------------------------------
# Verify existing functionality before modification
# ------------------------------------------------------------

existing_contract = {
    "SINGLE_API": "/tickets/analyze" in original_app,
    "BATCH_API": "/tickets/analyze-batch" in original_app,
    "BATCH_SELECTION": "selectBatchTicket" in original_app,
    "DETAIL_RENDERER": "renderAnalysisResponse" in original_app,
    "ANALYSIS_WORKSPACE": "showAnalysisWorkspace" in original_app,
    "SINGLE_PANEL": "single-ticket-panel" in original_index,
    "BATCH_INPUT": "batch-input-panel" in original_index,
}

for name, passed in existing_contract.items():
    print(
        f"{name:<38}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

if not all(existing_contract.values()):
    raise RuntimeError(
        "FAIL: existing application contract is incomplete."
    )

print()

# ------------------------------------------------------------
# Create fresh backups
# ------------------------------------------------------------

print("[2] BACKUPS")
print("-" * 64)

for source, backup in (
    (INDEX, INDEX_BACKUP),
    (APP, APP_BACKUP),
    (STYLE, STYLE_BACKUP),
):
    if backup.exists():
        raise RuntimeError(
            f"FAIL: refusing to overwrite existing backup: {backup}"
        )

    shutil.copy2(source, backup)

    if sha256(source) != sha256(backup):
        raise RuntimeError(
            f"FAIL: backup integrity mismatch: {backup}"
        )

    print(f"BACKUP CREATED: {backup}")

print()

# ------------------------------------------------------------
# HTML modification
# ------------------------------------------------------------

print("[3] HTML MODIFICATION")
print("-" * 64)

new_index = original_index

new_index = replace_once(
    new_index,
    single_button_block,
    "",
    "single ticket button removal",
)

new_index = replace_once(
    new_index,
    batch_button_block,
    "",
    "batch analysis button removal",
)

shared_action = """        <div class="workspace-entry-shared-action">

            <button
                type="button"
                id="open-analysis-workspace-button"
                class="workspace-entry-action workspace-entry-action-primary"
            >
                OPEN ANALYSIS WORKSPACE
            </button>

        </div>


"""

new_index = replace_once(
    new_index,
    workspace_information_marker,
    shared_action + workspace_information_marker,
    "shared workspace action insertion",
)

print("SINGLE BUTTON REMOVED:        PASS")
print("BATCH BUTTON REMOVED:         PASS")
print("SHARED BUTTON INSERTED:       PASS")
print()

# ------------------------------------------------------------
# APP.JS modification
# ------------------------------------------------------------

print("[4] APP.JS MODIFICATION")
print("-" * 64)

new_app = original_app

new_app = replace_once(
    new_app,
    single_declaration,
    "",
    "single navigation declaration removal",
)

new_app = replace_once(
    new_app,
    batch_declaration,
    "",
    "batch navigation declaration removal",
)

new_app = replace_once(
    new_app,
    single_listener,
    "",
    "single navigation listener removal",
)

new_app = replace_once(
    new_app,
    batch_listener,
    "",
    "batch navigation listener removal",
)

new_app = replace_once(
    new_app,
    view_research_declaration,
    view_research_declaration + shared_declaration,
    "shared navigation declaration insertion",
)

new_app = replace_once(
    new_app,
    analysis_home_anchor,
    shared_listener + analysis_home_anchor,
    "shared navigation listener insertion",
)

print("SINGLE NAVIGATION REMOVED:    PASS")
print("BATCH NAVIGATION REMOVED:     PASS")
print("SHARED NAVIGATION ADDED:      PASS")
print()

# ------------------------------------------------------------
# PRE-WRITE safety checks
# ------------------------------------------------------------

print("[5] PRE-WRITE SAFETY")
print("-" * 64)

if "open-single-ticket-button" in new_index:
    raise RuntimeError(
        "FAIL: old single-ticket button remains in HTML."
    )

if "open-batch-analysis-button" in new_index:
    raise RuntimeError(
        "FAIL: old batch-analysis button remains in HTML."
    )

if "openSingleButton" in new_app:
    raise RuntimeError(
        "FAIL: old openSingleButton reference remains in app.js."
    )

if "openBatchButton" in new_app:
    raise RuntimeError(
        "FAIL: old openBatchButton reference remains in app.js."
    )

if new_index.count(
    'id="open-analysis-workspace-button"'
) != 1:
    raise RuntimeError(
        "FAIL: shared workspace button count is not exactly one."
    )

if new_app.count(
    "openAnalysisWorkspaceButton"
) != 3:
    raise RuntimeError(
        "FAIL: shared workspace JS declaration/listener "
        "contract is unexpected."
    )

# Existing application contract must survive.
required_after_markers = [
    "/tickets/analyze",
    "/tickets/analyze-batch",
    "selectBatchTicket",
    "renderAnalysisResponse",
    "showAnalysisWorkspace",
]

for marker in required_after_markers:
    if marker not in new_app:
        raise RuntimeError(
            f"FAIL: required application marker disappeared: {marker}"
        )

# Frontend must remain free of model implementation.
for forbidden in (
    "TicketPipeline",
    "sklearn",
    "predict_batch(",
):
    if forbidden in new_app:
        raise RuntimeError(
            f"FAIL: forbidden frontend marker present: {forbidden}"
        )

print("OLD SINGLE BUTTON ABSENT:        PASS")
print("OLD BATCH BUTTON ABSENT:         PASS")
print("SHARED BUTTON COUNT:              PASS")
print("SINGLE API PRESERVED:             PASS")
print("BATCH API PRESERVED:              PASS")
print("BATCH SELECTION PRESERVED:        PASS")
print("DETAIL RENDERER PRESERVED:        PASS")
print("TICKET PIPELINE ABSENT:           PASS")
print("SKLEARN ABSENT:                   PASS")
print("PREDICT_BATCH ABSENT:             PASS")
print()

# ------------------------------------------------------------
# Write ONLY index.html and app.js
# ------------------------------------------------------------

INDEX.write_text(new_index, encoding="utf-8")
APP.write_text(new_app, encoding="utf-8")

print("[6] SOURCE WRITE")
print("-" * 64)
print("INDEX.HTML UPDATED:               TRUE")
print("APP.JS UPDATED:                   TRUE")
print("STYLE.CSS MODIFIED:               FALSE")
print()

# ------------------------------------------------------------
# JavaScript syntax check
# ------------------------------------------------------------

print("[7] JAVASCRIPT SYNTAX")
print("-" * 64)

syntax_result = subprocess.run(
    ["node", "--check", str(APP)],
    capture_output=True,
    text=True,
)

if syntax_result.returncode != 0:
    print(syntax_result.stdout)
    print(syntax_result.stderr)

    # Automatic rollback because the syntax contract failed.
    shutil.copy2(INDEX_BACKUP, INDEX)
    shutil.copy2(APP_BACKUP, APP)

    raise RuntimeError(
        "FAIL: node --check failed. "
        "index.html and app.js were automatically restored."
    )

print("NODE --CHECK: PASS")
print()

# ------------------------------------------------------------
# Final source validation
# ------------------------------------------------------------

final_index = INDEX.read_text(encoding="utf-8")
final_app = APP.read_text(encoding="utf-8")

print("[8] FINAL VALIDATION")
print("-" * 64)

final_checks = {
    "OLD_SINGLE_BUTTON_ABSENT":
        "open-single-ticket-button" not in final_index,

    "OLD_BATCH_BUTTON_ABSENT":
        "open-batch-analysis-button" not in final_index,

    "SHARED_BUTTON_PRESENT":
        final_index.count(
            'id="open-analysis-workspace-button"'
        ) == 1,

    "SHARED_HANDLER_DECLARATION_PRESENT":
        final_app.count(
            "openAnalysisWorkspaceButton"
        ) == 3,

    "SINGLE_API_PRESENT":
        "/tickets/analyze" in final_app,

    "BATCH_API_PRESENT":
        "/tickets/analyze-batch" in final_app,

    "BATCH_SELECTION_PRESENT":
        "selectBatchTicket" in final_app,

    "DETAIL_RENDERER_PRESENT":
        "renderAnalysisResponse" in final_app,

    "TICKET_PIPELINE_ABSENT":
        "TicketPipeline" not in final_app,

    "SKLEARN_ABSENT":
        "sklearn" not in final_app,

    "PREDICT_BATCH_ABSENT":
        "predict_batch(" not in final_app,

    "STYLE_UNCHANGED":
        sha256(STYLE) == original_style_hash,
}

for name, passed in final_checks.items():
    print(
        f"{name:<38}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

if not all(final_checks.values()):
    # Restore both changed source files if final validation fails.
    shutil.copy2(INDEX_BACKUP, INDEX)
    shutil.copy2(APP_BACKUP, APP)

    raise RuntimeError(
        "FAIL: final validation failed. "
        "index.html and app.js were automatically restored."
    )

# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

METRICS.mkdir(parents=True, exist_ok=True)

evidence = {
    "operation": "DEPLOY-OP-049",
    "title": "Navigation Simplification",
    "status": "PASS",
    "purpose": (
        "Replace two redundant workspace entry buttons with "
        "one shared analysis workspace action."
    ),
    "modified_files": [
        str(INDEX),
        str(APP),
    ],
    "style_modified": False,
    "backend_modified": False,
    "frozen_runtime_modified": False,
    "model_artifacts_modified": False,
    "backups": {
        "index": str(INDEX_BACKUP),
        "app": str(APP_BACKUP),
        "style": str(STYLE_BACKUP),
    },
    "checks": final_checks,
    "sha256": {
        "index_before": sha256(INDEX_BACKUP),
        "index_after": sha256(INDEX),
        "app_before": sha256(APP_BACKUP),
        "app_after": sha256(APP),
        "style_before": sha256(STYLE_BACKUP),
        "style_after": sha256(STYLE),
    },
}

evidence_path = (
    METRICS /
    "deploy_op049_navigation_simplification.json"
)

evidence_path.write_text(
    json.dumps(evidence, indent=2),
    encoding="utf-8",
)

print()
print("[9] EVIDENCE")
print("-" * 64)
print(f"EVIDENCE_WRITTEN: {evidence_path}")

print()
print("=" * 64)
print("DEPLOY-OP-049 — NAVIGATION SIMPLIFICATION")
print("STATUS: PASS")
print("=" * 64)
