from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

STYLE = (
    ROOT
    / "deployment"
    / "frontend"
    / "style.css"
)

BACKUP = (
    ROOT
    / "deployment"
    / "frontend"
    / "style.css.before-deploy-op062"
)

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "deploy_op062_full_page_glass_surfaces.json"
)

MARKER = (
    "DEPLOY-OP-062 — FULL-PAGE GLASS APPLICATION SURFACES"
)


CSS_LAYER = r'''

/* ============================================================
   DEPLOY-OP-062 — FULL-PAGE GLASS APPLICATION SURFACES
   ============================================================

   Scope:
   - full Research Workspace surface
   - single-ticket input surface
   - multi-ticket input surface
   - batch file area
   - batch information area
   - sharp geometry
   - stronger text contrast
   - presentation only

   No HTML / JS / backend / runtime changes.
   ============================================================ */


/* ============================================================
   01 — FULL RESEARCH WORKSPACE SURFACE
   ============================================================ */

body:not(.app-view-landing)
.workspace-home {

    width:
        100vw !important;

    max-width:
        none !important;

    margin-left:
        calc(50% - 50vw) !important;

    margin-right:
        calc(50% - 50vw) !important;

    min-height:
        calc(100dvh - 80px) !important;

    height:
        auto !important;

    overflow:
        visible !important;

    box-sizing:
        border-box;

    background:
        linear-gradient(
            135deg,
            rgba(157, 190, 220, 0.94) 0%,
            rgba(174, 204, 231, 0.90) 42%,
            rgba(142, 178, 211, 0.92) 100%
        ) !important;

    color:
        #102d50 !important;
}


/* Keep the actual workspace content centred. */

body:not(.app-view-landing)
.workspace-home-inner {

    width:
        min(
            1180px,
            calc(100% - 48px)
        ) !important;

    margin:
        0 auto !important;

    background:
        transparent !important;
}


/* ============================================================
   02 — WORKSPACE HEADING
   ============================================================ */

body:not(.app-view-landing)
.workspace-heading {

    background:
        transparent !important;

    border-bottom:
        1px solid
        rgba(
            43,
            91,
            137,
            0.28
        ) !important;
}

body:not(.app-view-landing)
.workspace-heading h1 {

    color:
        #10294a !important;
}

body:not(.app-view-landing)
.workspace-heading p {

    color:
        #294f76 !important;

    font-weight:
        650 !important;
}


/* ============================================================
   03 — WORKSPACE ENTRY CARDS
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.20),
            rgba(255, 255, 255, 0.08)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.52
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 20px 44px
        rgba(
            38,
            77,
            112,
            0.12
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.48
        ) !important;

    backdrop-filter:
        blur(18px)
        saturate(125%);

    -webkit-backdrop-filter:
        blur(18px)
        saturate(125%);
}


body:not(.app-view-landing)
.workspace-entry h3 {

    color:
        #12345d !important;

    font-weight:
        850 !important;
}


body:not(.app-view-landing)
.workspace-entry p {

    color:
        #214d77 !important;

    font-weight:
        650 !important;
}


/* ============================================================
   04 — SHARED WORKSPACE ACTION
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry-action-primary {

    background:
        linear-gradient(
            135deg,
            rgba(37, 99, 235, 0.98),
            rgba(35, 91, 205, 0.94)
        ) !important;

    color:
        #ffffff !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.34
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 14px 30px
        rgba(
            37,
            99,
            235,
            0.24
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.24
        ) !important;

    backdrop-filter:
        blur(10px);
}


body:not(.app-view-landing)
.workspace-entry-action-primary:hover {

    filter:
        brightness(1.06);

    transform:
        translateY(-1px);
}


/* ============================================================
   05 — WORKSPACE INFORMATION STRIP
   ============================================================ */

body:not(.app-view-landing)
.workspace-information-grid {

    background:
        transparent !important;
}


body:not(.app-view-landing)
.workspace-information {

    background:
        rgba(
            255,
            255,
            255,
            0.13
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.46
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.34
        ) !important;

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);
}


body:not(.app-view-landing)
.workspace-information strong {

    color:
        #12365e !important;

    font-weight:
        850 !important;
}


body:not(.app-view-landing)
.workspace-information p {

    color:
        #2b557d !important;

    font-weight:
        620 !important;
}


/* ============================================================
   06 — SINGLE-TICKET INPUT SURFACE
   ============================================================ */

body:not(.app-view-landing)
#single-ticket-panel {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.15),
            rgba(255, 255, 255, 0.055)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.44
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 20px 48px
        rgba(
            31,
            78,
            121,
            0.10
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.40
        ) !important;

    backdrop-filter:
        blur(18px)
        saturate(120%);

    -webkit-backdrop-filter:
        blur(18px)
        saturate(120%);
}


/* ============================================================
   07 — SINGLE-TICKET FORM
   ============================================================ */

body:not(.app-view-landing)
#ticket-form {

    background:
        rgba(
            255,
            255,
            255,
            0.07
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.30
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.28
        ) !important;

    backdrop-filter:
        blur(14px);

    -webkit-backdrop-filter:
        blur(14px);
}


/* ============================================================
   08 — FORM CONTROLS
   ============================================================ */

body:not(.app-view-landing)
#ticket-form input,
body:not(.app-view-landing)
#ticket-form textarea,
body:not(.app-view-landing)
#ticket-form select {

    background:
        rgba(
            255,
            255,
            255,
            0.16
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.48
        ) !important;

    border-radius:
        2px !important;

    color:
        #153b64 !important;

    box-shadow:
        inset 0 1px 2px
        rgba(
            24,
            60,
            96,
            0.035
        ) !important;

    backdrop-filter:
        blur(10px);
}


body:not(.app-view-landing)
#ticket-form input:focus,
body:not(.app-view-landing)
#ticket-form textarea:focus,
body:not(.app-view-landing)
#ticket-form select:focus {

    border-color:
        rgba(
            37,
            99,
            235,
            0.70
        ) !important;

    box-shadow:
        0 0 0 3px
        rgba(
            37,
            99,
            235,
            0.12
        ) !important;

    outline:
        none !important;
}


/* ============================================================
   09 — MULTI-TICKET PANEL
   ============================================================ */

body:not(.app-view-landing)
#batch-input-panel {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.15),
            rgba(255, 255, 255, 0.055)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.44
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 20px 48px
        rgba(
            31,
            78,
            121,
            0.10
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.40
        ) !important;

    backdrop-filter:
        blur(18px)
        saturate(120%);

    -webkit-backdrop-filter:
        blur(18px)
        saturate(120%);
}


/* ============================================================
   10 — MULTI-TICKET INNER AREAS
   ============================================================ */

body:not(.app-view-landing)
#batch-input-panel
.batch-input-layout {

    background:
        transparent !important;
}


body:not(.app-view-landing)
#batch-input-panel
.batch-file-area,

body:not(.app-view-landing)
#batch-input-panel
.batch-input-layout > div {

    background:
        rgba(
            255,
            255,
            255,
            0.09
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.34
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.28
        ) !important;

    backdrop-filter:
        blur(14px);

    -webkit-backdrop-filter:
        blur(14px);
}


/* ============================================================
   11 — FILE INPUT
   ============================================================ */

body:not(.app-view-landing)
#batch-input-panel
input[type="file"] {

    background:
        rgba(
            255,
            255,
            255,
            0.12
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.42
        ) !important;

    border-radius:
        2px !important;

    color:
        #173b62 !important;
}


body:not(.app-view-landing)
#batch-input-panel
input[type="file"]::file-selector-button {

    background:
        linear-gradient(
            180deg,
            #1d4f80,
            #12385e
        ) !important;

    color:
        #ffffff !important;

    border:
        0 !important;

    border-right:
        1px solid
        rgba(
            255,
            255,
            255,
            0.18
        ) !important;

    border-radius:
        0 !important;

    font-weight:
        750 !important;
}


/* ============================================================
   12 — MULTI-TICKET TEXT
   ============================================================ */

body:not(.app-view-landing)
#batch-input-panel h2 {

    color:
        #12345a !important;

    font-weight:
        850 !important;
}


body:not(.app-view-landing)
#batch-input-panel p,

body:not(.app-view-landing)
#batch-input-panel label {

    color:
        #234d75 !important;

    font-weight:
        650 !important;
}


body:not(.app-view-landing)
#batch-input-panel strong {

    color:
        #153a61 !important;

    font-weight:
        850 !important;
}


/* ============================================================
   13 — BATCH ACTION
   ============================================================ */

body:not(.app-view-landing)
#batch-validate-button {

    border-radius:
        2px !important;

    box-shadow:
        0 10px 22px
        rgba(
            37,
            99,
            235,
            0.16
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.22
        ) !important;
}


/* ============================================================
   14 — SHARP GEOMETRY
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry,
body:not(.app-view-landing)
.workspace-information,
body:not(.app-view-landing)
#single-ticket-panel,
body:not(.app-view-landing)
#ticket-form,
body:not(.app-view-landing)
#batch-input-panel,
body:not(.app-view-landing)
#batch-input-panel .batch-file-area,
body:not(.app-view-landing)
#batch-input-panel .batch-input-layout > div {

    border-radius:
        2px !important;
}


/* ============================================================
   15 — RESPONSIVE SAFETY
   ============================================================ */

@media (max-width: 980px) {

    body:not(.app-view-landing)
    .workspace-home {

        min-height:
            calc(100dvh - 80px) !important;

        height:
            auto !important;

        overflow:
            visible !important;
    }

    body:not(.app-view-landing)
    .workspace-home-inner {

        width:
            calc(100% - 36px) !important;
    }

    body:not(.app-view-landing)
    #batch-input-panel
    .batch-input-layout {

        grid-template-columns:
            1fr !important;
    }
}


@media (max-width: 620px) {

    body:not(.app-view-landing)
    .workspace-home-inner {

        width:
            calc(100% - 28px) !important;
    }

    body:not(.app-view-landing)
    #single-ticket-panel,
    body:not(.app-view-landing)
    #batch-input-panel {

        padding:
            20px !important;
    }

    body:not(.app-view-landing)
    #ticket-form {

        padding:
            20px !important;
    }

    body:not(.app-view-landing)
    #batch-input-panel
    .batch-file-area {

        padding:
            18px !important;
    }
}


/* ============================================================
   END DEPLOY-OP-062
   ============================================================ */
'''


def sha256(path: Path) -> str:

    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main():

    print("=" * 72)
    print("DEPLOY-OP-062 — FULL-PAGE GLASS APPLICATION SURFACES")
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    if not STYLE.exists():
        raise RuntimeError(
            f"FAIL: style.css not found: {STYLE}"
        )

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    required = {
        "DEPLOY-OP-057":
            "DEPLOY-OP-057" in style_before,

        "DEPLOY-OP-058":
            "DEPLOY-OP-058" in style_before,

        "DEPLOY-OP-059":
            "DEPLOY-OP-059" in style_before,

        "DEPLOY-OP-060":
            "DEPLOY-OP-060" in style_before,

        "DEPLOY-OP-061":
            "DEPLOY-OP-061" in style_before,

        ".workspace-home":
            ".workspace-home" in style_before,

        ".workspace-home-inner":
            ".workspace-home-inner" in style_before,

        "#single-ticket-panel":
            "#single-ticket-panel" in style_before,

        "#ticket-form":
            "#ticket-form" in style_before,

        "#batch-input-panel":
            "#batch-input-panel" in style_before,

        ".batch-input-layout":
            ".batch-input-layout" in style_before,

        ".batch-file-area":
            ".batch-file-area" in style_before,

        ".workspace-entry":
            ".workspace-entry" in style_before,

        ".workspace-information":
            ".workspace-information" in style_before,
    }

    for name, passed in required.items():

        print(
            f"{name:40}: "
            f"{'FOUND' if passed else 'MISSING'}"
        )

    if not all(required.values()):

        missing = [
            name
            for name, passed in required.items()
            if not passed
        ]

        raise RuntimeError(
            "FAIL: required existing CSS/source markers missing:\n"
            + "\n".join(
                f"  - {item}"
                for item in missing
            )
        )

    if MARKER in style_before:

        raise RuntimeError(
            "FAIL: DEPLOY-OP-062 already exists. "
            "Refusing duplicate write."
        )

    style_hash_before = sha256(STYLE)

    # =========================================================
    # 2. BACKUP
    # =========================================================

    print("\n[2] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        backup_hash = sha256(BACKUP)

        if backup_hash != style_hash_before:

            raise RuntimeError(
                "FAIL: existing OP-062 backup does not match "
                "current style.css. Refusing overwrite."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            BACKUP
        )

        if sha256(BACKUP) != style_hash_before:

            raise RuntimeError(
                "FAIL: backup integrity mismatch."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 3. WRITE
    # =========================================================

    print("\n[3] FULL-PAGE GLASS UI")
    print("-" * 72)

    STYLE.write_text(
        style_before + CSS_LAYER,
        encoding="utf-8"
    )

    print("STYLE.CSS UPDATED")

    # =========================================================
    # 4. VALIDATION
    # =========================================================

    print("\n[4] VALIDATION")
    print("-" * 72)

    style_after = STYLE.read_text(
        encoding="utf-8"
    )

    checks = {

        "OP062_MARKER":
            style_after.count(MARKER) == 1,

        "FULL_PAGE_WORKSPACE":
            "width:\n        100vw !important;" in style_after,

        "WORKSPACE_DARKER_SURFACE":
            "rgba(157, 190, 220, 0.94)" in style_after,

        "SINGLE_PANEL_GLASS":
            "#single-ticket-panel" in style_after
            and "rgba(255, 255, 255, 0.15)" in style_after,

        "TICKET_FORM_GLASS":
            "#ticket-form" in style_after
            and "rgba(255, 255, 255, 0.07)" in style_after,

        "MULTI_PANEL_GLASS":
            "#batch-input-panel" in style_after,

        "MULTI_FILE_AREA_GLASS":
            ".batch-file-area" in style_after
            and "rgba(255, 255, 255, 0.09)" in style_after,

        "FILE_INPUT_GLASS":
            '#batch-input-panel\ninput[type="file"]'
            in style_after,

        "SHARP_GEOMETRY":
            "border-radius:\n        2px !important;"
            in style_after,

        "STRONG_TEXT":
            "#12345a" in style_after
            and "#234d75" in style_after,

        "WORKSPACE_INFORMATION_GLASS":
            ".workspace-information" in style_after,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)" in style_after,

        "OP057_PRESERVED":
            "DEPLOY-OP-057" in style_after,

        "OP058_PRESERVED":
            "DEPLOY-OP-058" in style_after,

        "OP059_PRESERVED":
            "DEPLOY-OP-059" in style_after,

        "OP060_PRESERVED":
            "DEPLOY-OP-060" in style_after,

        "OP061_PRESERVED":
            "DEPLOY-OP-061" in style_after,
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

    # =========================================================
    # 5. EVIDENCE
    # =========================================================

    style_hash_after = sha256(STYLE)

    METRICS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-062",

        "title":
            "Full-Page Glass Application Surfaces",

        "status":
            "PASS",

        "scope": [
            "full Research Workspace surface",
            "single-ticket glass input surface",
            "multi-ticket glass input surface",
            "batch file area",
            "batch information area",
            "sharp rectangular geometry",
            "stronger text contrast",
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
    print("DEPLOY-OP-062")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
