from pathlib import Path
from hashlib import sha256
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

STYLE = ROOT / "deployment/frontend/style.css"

BACKUP = ROOT / (
    "deployment/frontend/"
    "style.css.before-deploy-op060"
)

METRICS = ROOT / (
    "modeling/FMP/metrics/"
    "deploy_op060_glass_transparency_sharp_ui.json"
)

MARKER = "DEPLOY-OP-060 — GLASS TRANSPARENCY + SHARP UI"


CSS_LAYER = r"""

/* ============================================================
   DEPLOY-OP-060 — GLASS TRANSPARENCY + SHARP UI
   ------------------------------------------------------------
   Application UI refinement only.

   Goals:
   - transparent glass surfaces
   - sharper rectangular geometry
   - stronger text contrast
   - consistent single + multi ticket treatment
   - preserve existing application structure
   ============================================================ */


/* ============================================================
   01 — SHARED GLASS SURFACE
   ============================================================ */

body:not(.app-view-landing)
.single-ticket-panel,

body:not(.app-view-landing)
.batch-file,

body:not(.app-view-landing)
.batch-results-panel,

body:not(.app-view-landing)
.workspace-entry,

body:not(.app-view-landing)
.workspace-information-grid,

body:not(.app-view-landing)
.workspace-information {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.30),
            rgba(255, 255, 255, 0.13)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.52) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 18px 45px
        rgba(31, 78, 121, 0.08),

        inset 0 1px 0
        rgba(255, 255, 255, 0.48) !important;

    backdrop-filter:
        blur(16px)
        saturate(125%);

    -webkit-backdrop-filter:
        blur(16px)
        saturate(125%);
}


/* ============================================================
   02 — WORKSPACE ENTRY CARDS
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.34),
            rgba(235, 245, 255, 0.16)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.60) !important;

    border-radius:
        2px !important;

    transition:
        transform 180ms ease,
        background 180ms ease,
        border-color 180ms ease,
        box-shadow 180ms ease;
}

body:not(.app-view-landing)
.workspace-entry:hover {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.42),
            rgba(235, 245, 255, 0.22)
        ) !important;

    border-color:
        rgba(37, 99, 235, 0.42) !important;

    box-shadow:
        0 20px 50px
        rgba(31, 78, 121, 0.13),

        inset 0 1px 0
        rgba(255, 255, 255, 0.60) !important;
}


/* ============================================================
   03 — WORKSPACE TEXT CONTRAST
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry h3,

body:not(.app-view-landing)
.workspace-entry p,

body:not(.app-view-landing)
.workspace-information h3,

body:not(.app-view-landing)
.workspace-information p,

body:not(.app-view-landing)
.workspace-entry-label {

    color:
        #17385f !important;
}

body:not(.app-view-landing)
.workspace-entry h3 {

    font-weight:
        800 !important;
}

body:not(.app-view-landing)
.workspace-entry p {

    font-weight:
        560 !important;
}


/* ============================================================
   04 — SINGLE TICKET FORM GLASS
   ============================================================ */

body:not(.app-view-landing)
#single-ticket-panel {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.24),
            rgba(235, 245, 255, 0.10)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.50) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 20px 55px
        rgba(31, 78, 121, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.50) !important;

    backdrop-filter:
        blur(18px)
        saturate(125%);

    -webkit-backdrop-filter:
        blur(18px)
        saturate(125%);
}


/* ============================================================
   05 — TICKET FORM CONTAINER
   ============================================================ */

body:not(.app-view-landing)
#ticket-form {

    background:
        rgba(255, 255, 255, 0.18) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.44) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.42) !important;

    backdrop-filter:
        blur(14px);

    -webkit-backdrop-filter:
        blur(14px);
}


/* ============================================================
   06 — INPUT CONTROLS
   ============================================================ */

body:not(.app-view-landing)
#ticket-form input,

body:not(.app-view-landing)
#ticket-form textarea,

body:not(.app-view-landing)
#ticket-form select {

    background:
        rgba(255, 255, 255, 0.30) !important;

    border:
        1px solid
        rgba(70, 125, 181, 0.36) !important;

    border-radius:
        2px !important;

    color:
        #17385f !important;

    box-shadow:
        inset 0 1px 2px
        rgba(31, 78, 121, 0.035),

        0 1px 0
        rgba(255, 255, 255, 0.30) !important;

    backdrop-filter:
        blur(10px);

    -webkit-backdrop-filter:
        blur(10px);
}


body:not(.app-view-landing)
#ticket-form input::placeholder,

body:not(.app-view-landing)
#ticket-form textarea::placeholder {

    color:
        #57799d !important;

    opacity:
        0.88 !important;
}


body:not(.app-view-landing)
#ticket-form input:focus,

body:not(.app-view-landing)
#ticket-form textarea:focus,

body:not(.app-view-landing)
#ticket-form select:focus {

    background:
        rgba(255, 255, 255, 0.42) !important;

    border-color:
        rgba(37, 99, 235, 0.62) !important;

    box-shadow:
        0 0 0 3px
        rgba(37, 99, 235, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.45) !important;

    outline:
        none !important;
}


/* ============================================================
   07 — FORM LABEL CONTRAST
   ============================================================ */

body:not(.app-view-landing)
#ticket-form label {

    color:
        #16375d !important;

    font-weight:
        750 !important;
}


/* ============================================================
   08 — MULTI-TICKET INPUT AREA
   ============================================================ */

body:not(.app-view-landing)
.batch-file {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.27),
            rgba(235, 245, 255, 0.12)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.50) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 16px 42px
        rgba(31, 78, 121, 0.08),

        inset 0 1px 0
        rgba(255, 255, 255, 0.45) !important;

    backdrop-filter:
        blur(16px)
        saturate(120%);

    -webkit-backdrop-filter:
        blur(16px)
        saturate(120%);
}


/* File input itself */

body:not(.app-view-landing)
.batch-file input[type="file"] {

    background:
        rgba(255, 255, 255, 0.24) !important;

    border:
        1px solid
        rgba(74, 126, 181, 0.32) !important;

    border-radius:
        2px !important;

    color:
        #17385f !important;
}


/* Multi-ticket explanatory panel */

body:not(.app-view-landing)
.batch-file + * {

    border-radius:
        2px !important;
}


/* ============================================================
   09 — BATCH RESULTS SURFACES
   ============================================================ */

body:not(.app-view-landing)
.batch-results-panel,

body:not(.app-view-landing)
.results-panel {

    background:
        rgba(255, 255, 255, 0.22) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.48) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 16px 42px
        rgba(31, 78, 121, 0.08),

        inset 0 1px 0
        rgba(255, 255, 255, 0.45) !important;

    backdrop-filter:
        blur(15px);

    -webkit-backdrop-filter:
        blur(15px);
}


/* ============================================================
   10 — LANDING RESEARCH STRIP
   ============================================================ */

body.app-view-landing
.project-research-strip {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.30),
            rgba(255, 255, 255, 0.12)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.58) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 18px 48px
        rgba(31, 78, 121, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.58) !important;

    backdrop-filter:
        blur(18px)
        saturate(125%);

    -webkit-backdrop-filter:
        blur(18px)
        saturate(125%);
}


body.app-view-landing
.project-feature {

    border-radius:
        0 !important;

    background:
        rgba(255, 255, 255, 0.06) !important;
}


body.app-view-landing
.project-feature h3,

body.app-view-landing
.project-feature p {

    color:
        #173d68 !important;
}


/* ============================================================
   11 — SHARP GEOMETRY
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry,

body:not(.app-view-landing)
.workspace-information,

body:not(.app-view-landing)
.single-ticket-panel,

body:not(.app-view-landing)
#ticket-form,

body:not(.app-view-landing)
.batch-file,

body:not(.app-view-landing)
.batch-results-panel,

body:not(.app-view-landing)
.results-panel,

body.app-view-landing
.project-research-strip {

    border-radius:
        2px !important;
}


/* ============================================================
   12 — PRESERVE EXISTING NAVIGATION
   ============================================================ */

.workspace-home-button,
.workspace-entry-action,
.workspace-entry-action-primary {

    border-radius:
        2px !important;
}


/* ============================================================
   13 — RESPONSIVE SAFETY
   ============================================================ */

@media (max-width: 980px) {

    body:not(.app-view-landing)
    .workspace-entry-grid {

        grid-template-columns:
            1fr !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-action-primary {

        min-width:
            280px !important;
    }
}


@media (max-width: 620px) {

    body:not(.app-view-landing)
    #ticket-form {

        padding:
            20px !important;
    }

    body:not(.app-view-landing)
    .batch-file {

        padding:
            18px !important;
    }

    body.app-view-landing
    .project-research-strip {

        border-radius:
            2px !important;
    }
}


/* ============================================================
   END DEPLOY-OP-060
   ============================================================ */
"""


def sha256(path: Path) -> str:
    digest = sha256_bytes(path.read_bytes())
    return digest


def sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def main():

    print("=" * 72)
    print("DEPLOY-OP-060 — GLASS TRANSPARENCY + SHARP UI")
    print("=" * 72)

    if not STYLE.exists():
        raise RuntimeError(
            f"FAIL: style.css not found: {STYLE}"
        )

    print("\n[1] SOURCE")
    print("-" * 72)
    print(f"STYLE.CSS: {STYLE}")
    print("FOUND")

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-060 already exists. "
            "No duplicate write performed."
        )

    style_hash_before = sha256(STYLE)

    print("\n[2] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        backup_hash = sha256(BACKUP)

        if backup_hash != style_hash_before:
            raise RuntimeError(
                "FAIL: existing OP-060 backup does not match "
                "current style.css. Refusing to overwrite."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            BACKUP
        )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    print("\n[3] CSS REFINEMENT")
    print("-" * 72)

    STYLE.write_text(
        style_before + CSS_LAYER,
        encoding="utf-8"
    )

    print("STYLE.CSS UPDATED")

    print("\n[4] VALIDATION")
    print("-" * 72)

    style_after = STYLE.read_text(
        encoding="utf-8"
    )

    checks = {

        "OP060_MARKER":
            style_after.count(MARKER) == 1,

        "GLASS_SINGLE_PANEL":
            "#single-ticket-panel" in style_after,

        "GLASS_TICKET_FORM":
            "#ticket-form" in style_after,

        "GLASS_FORM_CONTROLS":
            "#ticket-form input" in style_after,

        "GLASS_MULTI_TICKET":
            ".batch-file" in style_after,

        "GLASS_BATCH_RESULTS":
            ".batch-results-panel" in style_after,

        "GLASS_WORKSPACE":
            ".workspace-entry" in style_after,

        "GLASS_INFORMATION":
            ".workspace-information" in style_after,

        "GLASS_LANDING_STRIP":
            ".project-research-strip" in style_after,

        "SHARP_EDGES":
            "border-radius:\n        2px !important;" in style_after,

        "TRANSPARENT_SURFACES":
            "rgba(255, 255, 255, 0.30)" in style_after,

        "STRONG_TEXT_CONTRAST":
            "#17385f" in style_after,

        "FOCUS_STYLE":
            "#ticket-form input:focus" in style_after,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)" in style_after,

        "OP057_PRESERVED":
            "DEPLOY-OP-057" in style_after,

        "OP058_PRESERVED":
            "DEPLOY-OP-058" in style_after,

        "OP059_PRESERVED":
            "DEPLOY-OP-059" in style_after,
    }

    for name, passed in checks.items():

        print(
            f"{name:40}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):

        print(
            "\nVALIDATION FAILED — RESTORING"
        )

        shutil.copy2(
            BACKUP,
            STYLE
        )

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    style_hash_after = sha256(STYLE)

    METRICS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-060",

        "title":
            "Glass Transparency + Sharp UI",

        "status":
            "PASS",

        "scope": [
            "single-ticket glass surface",
            "multi-ticket glass surface",
            "batch results glass surface",
            "workspace glass surfaces",
            "landing research strip",
            "sharp rectangular geometry",
            "text contrast",
            "responsive safety",
        ],

        "modified_files": [
            str(STYLE)
        ],

        "backup": [
            str(BACKUP)
        ],

        "untouched": [
            "deployment/frontend/index.html",
            "deployment/frontend/app.js",
            "deployment/backend/app.py",
            "frozen deployment runtime",
            "frozen modeling artifacts",
            "T1-T11 semantics",
            "single-ticket API contract",
            "batch API contract",
        ],

        "hashes": {
            "before":
                style_hash_before,
            "after":
                style_hash_after,
        },

        "checks":
            checks,
    }

    METRICS.write_text(
        json.dumps(
            evidence,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"\nEVIDENCE_WRITTEN: {METRICS}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-060")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
