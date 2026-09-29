from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

STYLE = FRONTEND / "style.css"

BACKUP = FRONTEND / "style.css.before-deploy-op051"


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def require_marker(text: str, marker: str, name: str) -> None:
    count = text.count(marker)

    if count < 1:
        raise RuntimeError(
            f"FAIL: required CSS marker missing: {name} "
            f"({marker})"
        )


print("=" * 66)
print("DEPLOY-OP-051 — WORKSPACE VISUAL REDESIGN")
print("=" * 66)
print()

if not STYLE.exists():
    raise RuntimeError(f"FAIL: missing stylesheet: {STYLE}")

style_before = STYLE.read_text(encoding="utf-8")
style_before_hash = sha256(STYLE)

index_before_hash = sha256(
    FRONTEND / "index.html"
)

app_before_hash = sha256(
    FRONTEND / "app.js"
)

print("[1] WORKSPACE CSS CONTRACT")
print("-" * 66)

required_markers = {
    "WORKSPACE_HOME": ".workspace-home",
    "WORKSPACE_HEADING": ".workspace-heading",
    "ENTRY_GRID": ".workspace-entry-grid",
    "ENTRY_CARD": ".workspace-entry",
    "ENTRY_CONTENT": ".workspace-entry-content",
    "ENTRY_INDEX": ".workspace-entry-index",
    "ENTRY_LABEL": ".workspace-entry-label",
    "ENTRY_TITLE": ".workspace-entry h3",
    "ENTRY_DESCRIPTION": ".workspace-entry p",
    "SHARED_ACTION_BASE": ".workspace-entry-action",
    "INFO_GRID": ".workspace-information-grid",
    "INFO_CARD": ".workspace-information",
}

for name, marker in required_markers.items():
    require_marker(
        style_before,
        marker,
        name,
    )
    print(f"{name:<32}: FOUND")

print()

# ------------------------------------------------------------
# Create backup
# ------------------------------------------------------------

print("[2] BACKUP")
print("-" * 66)

if BACKUP.exists():
    if sha256(BACKUP) != style_before_hash:
        raise RuntimeError(
            "FAIL: existing OP-051 backup does not match "
            "the current pre-operation stylesheet."
        )

    print(f"BACKUP REUSED AND VERIFIED: {BACKUP}")

else:
    shutil.copy2(STYLE, BACKUP)

    if sha256(BACKUP) != style_before_hash:
        raise RuntimeError(
            "FAIL: stylesheet backup integrity mismatch."
        )

    print(f"BACKUP CREATED: {BACKUP}")
print()

# ------------------------------------------------------------
# CSS-only visual layer
# ------------------------------------------------------------

css_layer = r'''

/* =========================================================
   DEPLOY-OP-051
   WORKSPACE VISUAL REDESIGN
   =========================================================

   Scope:
   - Workspace presentation only.
   - CSS only.
   - No application logic.
   - No navigation changes.
   - No API changes.
   ========================================================= */


/* ---------------------------------------------------------
   WORKSPACE FOUNDATION
   --------------------------------------------------------- */

.workspace-home {
    width: min(
        calc(100% - 48px),
        1180px
    ) !important;

    margin:
        0 auto !important;

    padding:
        72px 0 76px !important;
}


.workspace-home-inner {
    width: 100% !important;
}


/* ---------------------------------------------------------
   WORKSPACE HEADING
   --------------------------------------------------------- */

.workspace-heading {
    display: block !important;

    max-width: 920px !important;

    margin:
        0 auto 30px !important;

    padding:
        0 8px !important;
}


.workspace-heading h2 {
    margin:
        8px 0 14px !important;

    color:
        #101d35 !important;

    font-size:
        clamp(2.9rem, 5vw, 4.45rem) !important;

    font-weight:
        800 !important;

    letter-spacing:
        -0.045em !important;

    line-height:
        0.98 !important;
}


.workspace-heading p {
    max-width:
        720px !important;

    margin:
        0 !important;

    color:
        #304966 !important;

    font-size:
        1rem !important;

    font-weight:
        550 !important;

    line-height:
        1.65 !important;
}


/* ---------------------------------------------------------
   TWO INPUT-MODE CARDS
   --------------------------------------------------------- */

.workspace-entry-grid {
    display:
        grid !important;

    grid-template-columns:
        repeat(2, minmax(0, 1fr)) !important;

    gap:
        20px !important;

    width:
        100% !important;

    margin:
        0 auto !important;
}


.workspace-entry {
    position:
        relative !important;

    min-height:
        286px !important;

    padding:
        30px 32px !important;

    overflow:
        hidden !important;

    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.96),
            rgba(239, 247, 255, 0.91)
        ) !important;

    border:
        1.5px solid #a9c6e2 !important;

    border-radius:
        14px !important;

    box-shadow:
        0 12px 30px rgba(30, 75, 120, 0.10),
        inset 0 1px 0 rgba(255, 255, 255, 0.95) !important;

    transition:
        transform 160ms ease,
        box-shadow 160ms ease,
        border-color 160ms ease !important;
}


.workspace-entry::before {
    content:
        "" !important;

    position:
        absolute !important;

    inset:
        0 !important;

    pointer-events:
        none !important;

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.52),
            transparent 42%
        ) !important;
}


.workspace-entry:hover {
    transform:
        translateY(-3px) !important;

    border-color:
        #78a9d5 !important;

    box-shadow:
        0 18px 38px rgba(28, 76, 124, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.98) !important;
}


.workspace-entry-index {
    position:
        relative !important;

    display:
        inline-flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    width:
        42px !important;

    height:
        42px !important;

    margin:
        0 0 26px !important;

    background:
        linear-gradient(
            145deg,
            #dbeeff,
            #c6def5
        ) !important;

    border:
        1px solid #a8c6e4 !important;

    border-radius:
        50% !important;

    color:
        #173c65 !important;

    font-size:
        0.78rem !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.08em !important;

    box-shadow:
        0 5px 14px rgba(39, 96, 150, 0.12) !important;
}


.workspace-entry-content {
    position:
        relative !important;

    display:
        flex !important;

    flex-direction:
        column !important;

    align-items:
        flex-start !important;

    height:
        calc(100% - 68px) !important;
}


.workspace-entry-label {
    margin:
        0 0 10px !important;

    color:
        #254e78 !important;

    font-size:
        0.72rem !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.16em !important;
}


.workspace-entry h3 {
    max-width:
        540px !important;

    margin:
        0 0 12px !important;

    color:
        #14243d !important;

    font-size:
        clamp(1.75rem, 2.7vw, 2.35rem) !important;

    font-weight:
        800 !important;

    letter-spacing:
        -0.025em !important;

    line-height:
        1.04 !important;
}


.workspace-entry p {
    max-width:
        500px !important;

    margin:
        0 !important;

    color:
        #3c5874 !important;

    font-size:
        0.96rem !important;

    font-weight:
        550 !important;

    line-height:
        1.65 !important;
}


/* ---------------------------------------------------------
   SHARED ANALYSIS ACTION
   --------------------------------------------------------- */

.workspace-entry-shared-action {
    display:
        flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    width:
        100% !important;

    margin:
        24px auto 30px !important;

    padding:
        0 !important;
}


.workspace-entry-action-primary {
    display:
        inline-flex !important;

    align-items:
        center !important;

    justify-content:
        center !important;

    width:
        min(520px, 72%) !important;

    min-height:
        68px !important;

    padding:
        16px 34px !important;

    background:
        linear-gradient(
            135deg,
            #1769e0 0%,
            #287df0 48%,
            #1763d1 100%
        ) !important;

    border:
        1px solid #0d54bb !important;

    border-radius:
        9px !important;

    color:
        #ffffff !important;

    font-size:
        1.02rem !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.045em !important;

    line-height:
        1 !important;

    text-align:
        center !important;

    box-shadow:
        0 12px 24px rgba(23, 91, 190, 0.25),
        inset 0 1px 0 rgba(255,255,255,0.28) !important;

    cursor:
        pointer !important;

    transition:
        transform 150ms ease,
        box-shadow 150ms ease,
        filter 150ms ease !important;
}


.workspace-entry-action-primary:hover {
    transform:
        translateY(-2px) !important;

    filter:
        brightness(1.04) !important;

    box-shadow:
        0 16px 30px rgba(23, 91, 190, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.32) !important;
}


.workspace-entry-action-primary:active {
    transform:
        translateY(0) !important;

    box-shadow:
        0 8px 18px rgba(23, 91, 190, 0.22),
        inset 0 1px 0 rgba(255,255,255,0.22) !important;
}


/* ---------------------------------------------------------
   WORKSPACE INFORMATION STRIP
   --------------------------------------------------------- */

.workspace-information-grid {
    display:
        grid !important;

    grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;

    width:
        100% !important;

    margin:
        4px auto 0 !important;

    background:
        rgba(231, 242, 253, 0.68) !important;

    border-top:
        1px solid #8fb0d0 !important;

    border-bottom:
        1px solid #8fb0d0 !important;

    box-shadow:
        0 8px 22px rgba(32, 76, 117, 0.06) !important;
}


.workspace-information {
    min-height:
        132px !important;

    padding:
        24px 26px !important;

    border-right:
        1px solid #9cb8d3 !important;
}


.workspace-information:last-child {
    border-right:
        0 !important;
}


.workspace-information span {
    display:
        block !important;

    margin:
        0 0 10px !important;

    color:
        #2c537a !important;

    font-size:
        0.68rem !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.16em !important;
}


.workspace-information strong {
    display:
        block !important;

    margin:
        0 0 8px !important;

    color:
        #152a45 !important;

    font-size:
        1rem !important;

    font-weight:
        800 !important;

    letter-spacing:
        0.015em !important;
}


.workspace-information p {
    margin:
        0 !important;

    color:
        #49637e !important;

    font-size:
        0.82rem !important;

    font-weight:
        550 !important;

    line-height:
        1.55 !important;
}


/* ---------------------------------------------------------
   WORKSPACE RESPONSIVE
   --------------------------------------------------------- */

@media (max-width: 900px) {

    .workspace-home {
        width:
            calc(100% - 32px) !important;

        padding:
            52px 0 60px !important;
    }


    .workspace-entry-grid {
        grid-template-columns:
            1fr !important;
    }


    .workspace-entry {
        min-height:
            250px !important;
    }


    .workspace-entry-action-primary {
        width:
            min(520px, 86%) !important;
    }


    .workspace-information-grid {
        grid-template-columns:
            1fr !important;
    }


    .workspace-information {
        border-right:
            0 !important;

        border-bottom:
            1px solid #9cb8d3 !important;
    }


    .workspace-information:last-child {
        border-bottom:
            0 !important;
    }
}


@media (max-width: 620px) {

    .workspace-home {
        width:
            calc(100% - 22px) !important;

        padding:
            40px 0 48px !important;
    }


    .workspace-heading {
        padding:
            0 4px !important;
    }


    .workspace-heading h2 {
        font-size:
            2.7rem !important;
    }


    .workspace-entry {
        min-height:
            230px !important;

        padding:
            24px !important;
    }


    .workspace-entry-action-primary {
        width:
            100% !important;

        min-height:
            62px !important;

        font-size:
            0.9rem !important;
    }
}


/* ---------------------------------------------------------
   REDUCED MOTION
   --------------------------------------------------------- */

@media (prefers-reduced-motion: reduce) {

    .workspace-entry,
    .workspace-entry-action-primary {
        transition:
            none !important;
    }
}

'''

# ------------------------------------------------------------
# Ensure operation marker is not duplicated
# ------------------------------------------------------------

if "DEPLOY-OP-051" in style_before:
    raise RuntimeError(
        "FAIL: DEPLOY-OP-051 CSS layer already exists. "
        "Refusing duplicate application."
    )

# ------------------------------------------------------------
# Append CSS
# ------------------------------------------------------------

STYLE.write_text(
    style_before + css_layer,
    encoding="utf-8",
)

print("[3] CSS UPDATE")
print("-" * 66)
print("WORKSPACE FOUNDATION:          UPDATED")
print("TWO INPUT CARDS:               UPDATED")
print("SHARED ACTION POSITION:        UPDATED")
print("SHARED ACTION SIZE:            UPDATED")
print("INFORMATION STRIP:             UPDATED")
print("RESPONSIVE RULES:              UPDATED")
print("APP.JS MODIFIED:               FALSE")
print("INDEX.HTML MODIFIED:           FALSE")
print("BACKEND MODIFIED:              FALSE")
print("FROZEN RUNTIME MODIFIED:       FALSE")
print()

# ------------------------------------------------------------
# Final validation
# ------------------------------------------------------------

style_after = STYLE.read_text(encoding="utf-8")

print("[4] FINAL VALIDATION")
print("-" * 66)

checks = {
    "OP051_MARKER_PRESENT":
        "DEPLOY-OP-051" in style_after,

    "WORKSPACE_HOME_PRESENT":
        ".workspace-home" in style_after,

    "ENTRY_GRID_PRESENT":
        ".workspace-entry-grid" in style_after,

    "ENTRY_CARD_PRESENT":
        ".workspace-entry" in style_after,

    "SHARED_ACTION_PRESENT":
        ".workspace-entry-shared-action" in style_after,

    "SHARED_BUTTON_PRESENT":
        ".workspace-entry-action-primary" in style_after,

    "INFO_GRID_PRESENT":
        ".workspace-information-grid" in style_after,

    "RESPONSIVE_RULES_PRESENT":
        "@media (max-width: 900px)" in style_after,

    "INDEX_UNCHANGED":
        sha256(
            FRONTEND / "index.html"
        ) == index_before_hash,

    "APP_UNCHANGED":
        sha256(
            FRONTEND / "app.js"
        ) == app_before_hash,
}

for name, passed in checks.items():
    print(
        f"{name:<34}: "
        f"{'PASS' if passed else 'FAIL'}"
    )

if not all(checks.values()):
    # Restore stylesheet only.
    shutil.copy2(BACKUP, STYLE)

    raise RuntimeError(
        "FAIL: final validation failed. "
        "style.css automatically restored."
    )

# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

METRICS.mkdir(parents=True, exist_ok=True)

evidence = {
    "operation": "DEPLOY-OP-051",
    "title": "Workspace Visual Redesign",
    "status": "PASS",
    "scope": "CSS-only workspace presentation layer",
    "modified_files": [
        str(STYLE),
    ],
    "untouched_files": [
        str(FRONTEND / "index.html"),
        str(FRONTEND / "app.js"),
        str(
            ROOT
            / "deployment"
            / "backend"
            / "app.py"
        ),
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
    "backup": str(BACKUP),
    "checks": checks,
    "sha256": {
        "style_before": style_before_hash,
        "style_after": sha256(STYLE),
        "index_unchanged": sha256(
            FRONTEND / "index.html"
        ),
        "app_unchanged": sha256(
            FRONTEND / "app.js"
        ),
    },
}

evidence_path = (
    METRICS /
    "deploy_op051_workspace_visual_redesign.json"
)

evidence_path.write_text(
    json.dumps(evidence, indent=2),
    encoding="utf-8",
)

print()
print("[5] EVIDENCE")
print("-" * 66)
print(f"EVIDENCE_WRITTEN: {evidence_path}")

print()
print("=" * 66)
print("DEPLOY-OP-051 — WORKSPACE VISUAL REDESIGN")
print("STATUS: PASS")
print("=" * 66)
