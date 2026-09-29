from pathlib import Path
from hashlib import sha256
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
    / "style.css.before-deploy-op064"
)

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
    / "deploy_op064_workspace_batch_glass.json"
)

MARKER = (
    "DEPLOY-OP-064 — WORKSPACE + BATCH GLASS REFINEMENT"
)


CSS_LAYER = r'''

/* ============================================================
   DEPLOY-OP-064 — WORKSPACE + BATCH GLASS REFINEMENT
   ============================================================
   CSS presentation only.

   Purpose:
   - extend the Research Workspace surface across the viewport
   - remove opaque batch-input surfaces
   - create transparent glass input areas
   - preserve sharp rectangular geometry
   - strengthen text contrast
   - preserve all application behaviour
   ============================================================ */


/* ------------------------------------------------------------
   01 — FULL RESEARCH WORKSPACE SURFACE
   ------------------------------------------------------------ */

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

    background:
        linear-gradient(
            135deg,
            rgba(170, 202, 230, 0.72) 0%,
            rgba(143, 181, 215, 0.58) 48%,
            rgba(119, 160, 198, 0.48) 100%
        ) !important;

    position:
        relative;

    isolation:
        isolate;

    overflow:
        visible !important;
}


/* ------------------------------------------------------------
   02 — WORKSPACE INNER CONTENT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-home-inner {

    position:
        relative;

    z-index:
        1;

    background:
        transparent !important;
}


/* ------------------------------------------------------------
   03 — SINGLE-TICKET PANEL GLASS
   ------------------------------------------------------------ */

body:not(.app-view-landing)
#single-ticket-panel {

    background:
        rgba(
            255,
            255,
            255,
            0.10
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
        0 18px 45px
        rgba(31, 78, 121, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.32) !important;

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);
}


/* ------------------------------------------------------------
   04 — MULTI-TICKET PANEL
   ------------------------------------------------------------ */

body:not(.app-view-landing)
#batch-input-panel {

    background:
        rgba(
            255,
            255,
            255,
            0.10
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
        0 18px 45px
        rgba(31, 78, 121, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.30) !important;

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);
}


/* ------------------------------------------------------------
   05 — BATCH INPUT LAYOUT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.batch-input-layout {

    background:
        transparent !important;
}


/* ------------------------------------------------------------
   06 — BATCH FILE AREA
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.batch-file-area {

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
            0.28
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.22),

        0 10px 24px
        rgba(31, 78, 121, 0.07) !important;

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);
}


/* ------------------------------------------------------------
   07 — FILE INPUT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.batch-file-area
input[type="file"] {

    width:
        100%;

    background:
        rgba(
            255,
            255,
            255,
            0.08
        ) !important;

    border:
        1px solid
        rgba(
            67,
            117,
            170,
            0.34
        ) !important;

    border-radius:
        2px !important;

    color:
        #173b63 !important;

    box-shadow:
        inset 0 1px 2px
        rgba(31, 78, 121, 0.04) !important;

    backdrop-filter:
        blur(10px);

    -webkit-backdrop-filter:
        blur(10px);
}


/* ------------------------------------------------------------
   08 — BATCH INFORMATION PANEL
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.batch-input-information {

    background:
        rgba(
            255,
            255,
            255,
            0.065
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.28
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.20),

        0 10px 24px
        rgba(31, 78, 121, 0.06) !important;

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);
}


/* ------------------------------------------------------------
   09 — BATCH INFORMATION TEXT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.batch-input-information p {

    color:
        #173b63 !important;

    font-weight:
        650 !important;
}

body:not(.app-view-landing)
.batch-input-information p strong {

    color:
        #102f53 !important;

    font-weight:
        800 !important;
}


/* ------------------------------------------------------------
   10 — FILE NAME
   ------------------------------------------------------------ */

body:not(.app-view-landing)
#batch-file-name {

    color:
        #174f8c !important;

    font-weight:
        800 !important;
}


/* ------------------------------------------------------------
   11 — BATCH PANEL TEXT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
#batch-input-panel h2,
body:not(.app-view-landing)
#batch-input-panel h3 {

    color:
        #102f53 !important;
}

body:not(.app-view-landing)
#batch-input-panel label {

    color:
        #173b63 !important;

    font-weight:
        750 !important;
}


/* ------------------------------------------------------------
   12 — SHARP BUTTON GEOMETRY
   ------------------------------------------------------------ */

body:not(.app-view-landing)
#batch-input-panel button {

    border-radius:
        2px !important;
}


/* ------------------------------------------------------------
   13 — WORKSPACE INFORMATION STRIP
   ------------------------------------------------------------ */

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
            0.075
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.28
        ) !important;

    border-radius:
        2px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.22) !important;

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);
}


/* ------------------------------------------------------------
   14 — WORKSPACE RESPONSIVE SAFETY
   ------------------------------------------------------------ */

@media (max-width: 980px) {

    body:not(.app-view-landing)
    .workspace-home {

        width:
            100vw !important;

        margin-left:
            calc(50% - 50vw) !important;

        margin-right:
            calc(50% - 50vw) !important;

        min-height:
            calc(100dvh - 80px) !important;

        max-height:
            none !important;

        overflow:
            visible !important;
    }
}


@media (max-width: 620px) {

    body:not(.app-view-landing)
    .workspace-home {

        width:
            100vw !important;

        margin-left:
            calc(50% - 50vw) !important;

        margin-right:
            calc(50% - 50vw) !important;

        padding:
            20px 0 !important;
    }

    body:not(.app-view-landing)
    #batch-input-panel {

        border-radius:
            2px !important;
    }

    body:not(.app-view-landing)
    .batch-file-area,
    body:not(.app-view-landing)
    .batch-input-information {

        border-radius:
            2px !important;
    }
}


/* ============================================================
   END DEPLOY-OP-064
   ============================================================ */
'''


def sha256(path: Path) -> str:

    digest = sha256_file(path)

    return digest


def sha256_file(path: Path) -> str:

    import hashlib

    h = hashlib.sha256()

    with path.open("rb") as handle:

        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):

            h.update(chunk)

    return h.hexdigest()


def main():

    print("=" * 72)
    print(
        "DEPLOY-OP-064 — WORKSPACE + BATCH GLASS REFINEMENT"
    )
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

        "workspace-home":
            ".workspace-home" in style_before,

        "workspace-home-inner":
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

        ".batch-input-information":
            ".batch-input-information" in style_before,

        ".workspace-information":
            ".workspace-information" in style_before,
    }

    for name, passed in required.items():

        print(
            f"{name:40}: "
            f"{'FOUND' if passed else 'MISSING'}"
        )

    missing = [
        name
        for name, passed in required.items()
        if not passed
    ]

    if missing:

        raise RuntimeError(
            "FAIL: required existing selector(s) missing: "
            + ", ".join(missing)
        )

    # =========================================================
    # 2. BACKUP
    # =========================================================

    print("\n[2] BACKUP")
    print("-" * 72)

    style_hash_before = sha256_file(STYLE)

    if BACKUP.exists():

        backup_hash = sha256_file(BACKUP)

        if backup_hash != style_hash_before:

            raise RuntimeError(
                "FAIL: existing OP-064 backup does not match "
                "current style.css. No write performed."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            BACKUP
        )

        if sha256_file(BACKUP) != style_hash_before:

            raise RuntimeError(
                "FAIL: backup integrity mismatch."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 3. WRITE
    # =========================================================

    print("\n[3] WORKSPACE + BATCH GLASS")
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

        "OP064_MARKER":
            style_after.count(MARKER) == 1,

        "FULL_VIEWPORT_WORKSPACE":
            "width:\n        100vw !important;"
            in style_after,

        "WORKSPACE_GLASS":
            "rgba(170, 202, 230, 0.72)"
            in " ".join(style_after.split()),

        "BATCH_PANEL_GLASS":
            "#batch-input-panel"
            in style_after
            and "rgba(\n            255,\n            255,\n            255,\n            0.10"
            in style_after,

        "BATCH_FILE_GLASS":
            ".batch-file-area"
            in style_after
            and "rgba(\n            255,\n            255,\n            255,\n            0.07"
            in style_after,

        "FILE_INPUT_GLASS":
            ".batch-file-area"
            in style_after
            and 'input[type="file"]'
            in style_after
            and "rgba(\n            255,\n            255,\n            255,\n            0.08"
            in style_after,

        "BATCH_INFORMATION_GLASS":
            ".batch-input-information"
            in style_after
            and "rgba(\n            255,\n            255,\n            255,\n            0.065"
            in style_after,

        "SHARP_BATCH_PANEL":
            "border-radius:\n        2px !important;"
            in style_after,

        "STRONG_BATCH_TEXT":
            "#173b63"
            in style_after
            and "#102f53"
            in style_after,

        "INFORMATION_GLASS":
            ".workspace-information"
            in style_after,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)"
            in style_after,

        "OP057_PRESERVED":
            "DEPLOY-OP-057"
            in style_after,

        "OP058_PRESERVED":
            "DEPLOY-OP-058"
            in style_after,

        "OP059_PRESERVED":
            "DEPLOY-OP-059"
            in style_after,

        "OP060_PRESERVED":
            "DEPLOY-OP-060"
            in style_after,

        "OP061_PRESERVED":
            "DEPLOY-OP-061"
            in style_after,
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

        print(
            "RESTORE COMPLETE"
        )

        print(
            "STATUS: FAIL"
        )

        raise SystemExit(1)

    # =========================================================
    # 5. INTEGRITY
    # =========================================================

    style_hash_after = sha256_file(STYLE)

    # The operation must actually change style.css.
    if style_hash_after == style_hash_before:

        shutil.copy2(
            BACKUP,
            STYLE
        )

        raise RuntimeError(
            "FAIL: style.css hash did not change."
        )

    # =========================================================
    # 6. EVIDENCE
    # =========================================================

    METRICS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-064",

        "title":
            "Workspace + Batch Glass Refinement",

        "status":
            "PASS",

        "scope": [

            "full viewport Research Workspace surface",

            "transparent single-ticket panel",

            "transparent multi-ticket panel",

            "transparent batch file area",

            "transparent file input",

            "transparent batch information panel",

            "sharp rectangular geometry",

            "stronger batch text contrast",

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
    print("DEPLOY-OP-064")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
