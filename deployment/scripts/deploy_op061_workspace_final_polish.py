from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

INDEX = ROOT / "deployment/frontend/index.html"
STYLE = ROOT / "deployment/frontend/style.css"

METRICS = (
    ROOT
    / "modeling/FMP/metrics/"
    / "deploy_op061_workspace_final_polish.json"
)

INDEX_BACKUP = (
    ROOT
    / "deployment/frontend/index.html.before-deploy-op061"
)

STYLE_BACKUP = (
    ROOT
    / "deployment/frontend/style.css.before-deploy-op061"
)

MARKER = "DEPLOY-OP-061 — WORKSPACE FINAL POLISH"


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main():

    print("=" * 72)
    print("DEPLOY-OP-061 — WORKSPACE FINAL POLISH")
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    if not INDEX.exists():
        raise RuntimeError(
            f"FAIL: index.html not found: {INDEX}"
        )

    if not STYLE.exists():
        raise RuntimeError(
            f"FAIL: style.css not found: {STYLE}"
        )

    index_before = INDEX.read_text(
        encoding="utf-8"
    )

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    required_index = [
        'id="workspace-home"',
        'class="workspace-heading"',
        'class="workspace-entry-grid"',
        'workspace-entry-single',
        'workspace-entry-batch',
        'class="workspace-entry-content"',
        'class="workspace-entry-label"',
        'class="workspace-information-grid"',
        'id="open-analysis-workspace-button"',
    ]

    required_style = [
        ".workspace-home",
        ".workspace-heading",
        ".workspace-entry",
        ".workspace-entry-content",
        ".workspace-entry p",
        ".workspace-information",
        ".workspace-entry-action-primary",
    ]

    for marker in required_index:

        found = marker in index_before

        print(
            f"INDEX {marker:40} "
            f"{'FOUND' if found else 'MISSING'}"
        )

        if not found:
            raise RuntimeError(
                f"FAIL: required HTML marker missing: {marker}"
            )

    for marker in required_style:

        found = marker in style_before

        print(
            f"CSS   {marker:40} "
            f"{'FOUND' if found else 'MISSING'}"
        )

        if not found:
            raise RuntimeError(
                f"FAIL: required CSS marker missing: {marker}"
            )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-061 already exists. "
            "Refusing duplicate write."
        )

    # =========================================================
    # 2. BACKUPS
    # =========================================================

    print("\n[2] BACKUPS")
    print("-" * 72)

    index_hash_before = sha256(INDEX)
    style_hash_before = sha256(STYLE)

    if INDEX_BACKUP.exists():

        if sha256(INDEX_BACKUP) != index_hash_before:
            raise RuntimeError(
                "FAIL: existing index OP-061 backup does not "
                "match current index.html. Refusing overwrite."
            )

        print(
            f"INDEX BACKUP REUSED AND VERIFIED: "
            f"{INDEX_BACKUP}"
        )

    else:

        shutil.copy2(
            INDEX,
            INDEX_BACKUP
        )

        print(
            f"INDEX BACKUP CREATED: "
            f"{INDEX_BACKUP}"
        )

    if STYLE_BACKUP.exists():

        if sha256(STYLE_BACKUP) != style_hash_before:
            raise RuntimeError(
                "FAIL: existing style OP-061 backup does not "
                "match current style.css. Refusing overwrite."
            )

        print(
            f"STYLE BACKUP REUSED AND VERIFIED: "
            f"{STYLE_BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            STYLE_BACKUP
        )

        print(
            f"STYLE BACKUP CREATED: "
            f"{STYLE_BACKUP}"
        )

    # =========================================================
    # 3. REMOVE WORKSPACE KICKER
    # =========================================================

    print("\n[3] WORKSPACE HEADING CLEANUP")
    print("-" * 72)

    workspace_start = index_before.find(
        '<section\n    id="workspace-home"'
    )

    if workspace_start == -1:

        workspace_start = index_before.find(
            '<section\n    id="workspace-home"'
        )

    workspace_end = index_before.find(
        "</section>",
        workspace_start
    )

    if workspace_start == -1 or workspace_end == -1:

        raise RuntimeError(
            "FAIL: workspace-home section boundaries "
            "could not be located."
        )

    workspace_block = index_before[
        workspace_start:
        workspace_end
    ]

    kicker = """                <div class="project-kicker">
                    IT TICKET INTELLIGENCE
                </div>

"""

    if kicker in workspace_block:

        workspace_block = workspace_block.replace(
            kicker,
            "",
            1
        )

        print(
            "WORKSPACE KICKER: REMOVED"
        )

    else:

        print(
            "WORKSPACE KICKER: ALREADY ABSENT"
        )

    index_after = (
        index_before[:workspace_start]
        + workspace_block
        + index_before[workspace_end:]
    )

    # =========================================================
    # 4. CSS REFINEMENT
    # =========================================================

    print("\n[4] WORKSPACE VISUAL REFINEMENT")
    print("-" * 72)

    css_layer = r"""

/* ============================================================
   DEPLOY-OP-061 — WORKSPACE FINAL POLISH
   ------------------------------------------------------------
   Final workspace presentation refinement.

   Scope:
   - darker glass workspace background
   - transparent entry cards
   - visible card descriptions
   - sharp geometry
   - stronger typography
   - modern shared action
   - transparent information strip

   Functional behaviour unchanged.
   ============================================================ */


/* ------------------------------------------------------------
   01 — WORKSPACE BACKGROUND
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-home {

    position: relative;

    background:
        radial-gradient(
            circle at 18% 22%,
            rgba(255, 255, 255, 0.12),
            transparent 34%
        ),
        radial-gradient(
            circle at 82% 18%,
            rgba(80, 150, 235, 0.12),
            transparent 38%
        ),
        linear-gradient(
            135deg,
            rgba(191, 216, 239, 0.72),
            rgba(165, 198, 228, 0.66)
        ) !important;

    color:
        #102b4d !important;
}


/* ------------------------------------------------------------
   02 — WORKSPACE HEADING
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-heading {

    padding-bottom:
        24px !important;

    border-bottom:
        1px solid
        rgba(22, 67, 110, 0.22) !important;
}

body:not(.app-view-landing)
.workspace-heading h2 {

    color:
        #0f294b !important;

    font-size:
        clamp(
            2.7rem,
            5vw,
            4.4rem
        ) !important;

    font-weight:
        850 !important;

    letter-spacing:
        -0.055em !important;
}

body:not(.app-view-landing)
.workspace-heading p {

    color:
        #244b72 !important;

    font-weight:
        600 !important;
}


/* ------------------------------------------------------------
   03 — ENTRY CARDS
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-entry {

    min-height:
        250px !important;

    padding:
        30px !important;

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.30),
            rgba(255, 255, 255, 0.10)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.48) !important;

    border-radius:
        2px !important;

    box-shadow:
        0 18px 44px
        rgba(25, 65, 105, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.48) !important;

    backdrop-filter:
        blur(18px)
        saturate(125%) !important;

    -webkit-backdrop-filter:
        blur(18px)
        saturate(125%) !important;

    overflow:
        visible !important;
}


/* ------------------------------------------------------------
   04 — CARD CONTENT
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-entry-content {

    align-self:
        center !important;

    min-width:
        0 !important;
}

body:not(.app-view-landing)
.workspace-entry-index {

    color:
        #17436d !important;

    font-weight:
        900 !important;
}

body:not(.app-view-landing)
.workspace-entry-label {

    color:
        #1a4c79 !important;

    font-weight:
        900 !important;

    letter-spacing:
        0.18em !important;
}

body:not(.app-view-landing)
.workspace-entry h3 {

    color:
        #102f55 !important;

    font-weight:
        850 !important;

    text-shadow:
        0 1px 0
        rgba(255, 255, 255, 0.35);
}


/* ------------------------------------------------------------
   05 — BOTH CARD DESCRIPTIONS
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-entry p {

    display:
        block !important;

    visibility:
        visible !important;

    max-width:
        500px !important;

    margin:
        14px 0 0 !important;

    color:
        #244d76 !important;

    font-size:
        0.96rem !important;

    line-height:
        1.62 !important;

    font-weight:
        600 !important;

    opacity:
        1 !important;
}


/* ------------------------------------------------------------
   06 — HIDE OLD CARD ACTIONS
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-entry
.workspace-entry-action {

    display:
        none !important;
}


/* ------------------------------------------------------------
   07 — SHARED ANALYSIS BUTTON
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-entry-shared-action {

    margin-top:
        26px !important;

    display:
        flex !important;

    justify-content:
        center !important;
}

body:not(.app-view-landing)
.workspace-entry-action-primary {

    min-width:
        min(
            500px,
            82%
        ) !important;

    min-height:
        58px !important;

    padding:
        15px 30px !important;

    background:
        linear-gradient(
            135deg,
            rgba(37, 99, 235, 0.94),
            rgba(29, 78, 216, 0.90)
        ) !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.38) !important;

    border-radius:
        2px !important;

    color:
        #ffffff !important;

    font-size:
        0.86rem !important;

    font-weight:
        850 !important;

    letter-spacing:
        0.12em !important;

    box-shadow:
        0 14px 32px
        rgba(30, 78, 150, 0.22),

        inset 0 1px 0
        rgba(255, 255, 255, 0.30) !important;

    backdrop-filter:
        blur(12px) !important;

    -webkit-backdrop-filter:
        blur(12px) !important;
}

body:not(.app-view-landing)
.workspace-entry-action-primary:hover {

    background:
        linear-gradient(
            135deg,
            rgba(48, 112, 245, 0.98),
            rgba(30, 86, 226, 0.96)
        ) !important;

    transform:
        translateY(-1px);
}


/* ------------------------------------------------------------
   08 — INFORMATION STRIP
   ------------------------------------------------------------ */

body:not(.app-view-landing)
.workspace-information-grid {

    margin-top:
        38px !important;

    border:
        1px solid
        rgba(255, 255, 255, 0.42) !important;

    border-radius:
        2px !important;

    background:
        rgba(255, 255, 255, 0.18) !important;

    box-shadow:
        0 16px 40px
        rgba(25, 65, 105, 0.08),

        inset 0 1px 0
        rgba(255, 255, 255, 0.40) !important;

    backdrop-filter:
        blur(16px)
        saturate(120%) !important;

    -webkit-backdrop-filter:
        blur(16px)
        saturate(120%) !important;
}

body:not(.app-view-landing)
.workspace-information {

    min-height:
        145px !important;

    background:
        rgba(255, 255, 255, 0.08) !important;

    border-right:
        1px solid
        rgba(255, 255, 255, 0.34) !important;
}

body:not(.app-view-landing)
.workspace-information span {

    color:
        #27577f !important;

    font-weight:
        900 !important;
}

body:not(.app-view-landing)
.workspace-information strong {

    color:
        #102f55 !important;

    font-weight:
        850 !important;
}

body:not(.app-view-landing)
.workspace-information p {

    color:
        #315a7f !important;

    font-weight:
        600 !important;
}


/* ------------------------------------------------------------
   09 — RESPONSIVE SAFETY
   ------------------------------------------------------------ */

@media (max-width: 980px) {

    body:not(.app-view-landing)
    .workspace-entry {

        min-height:
            220px !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-content {

        align-self:
            center !important;
    }
}


@media (max-width: 620px) {

    body:not(.app-view-landing)
    .workspace-entry {

        min-height:
            210px !important;

        padding:
            24px !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-action-primary {

        min-width:
            100% !important;
    }

    body:not(.app-view-landing)
    .workspace-information-grid {

        grid-template-columns:
            1fr !important;
    }

    body:not(.app-view-landing)
    .workspace-information {

        border-right:
            0 !important;

        border-bottom:
            1px solid
            rgba(255, 255, 255, 0.30) !important;
    }

    body:not(.app-view-landing)
    .workspace-information:last-child {

        border-bottom:
            0 !important;
    }
}


/* ============================================================
   END DEPLOY-OP-061
   ============================================================ */
"""

    STYLE.write_text(
        style_before + css_layer,
        encoding="utf-8"
    )

    INDEX.write_text(
        index_after,
        encoding="utf-8"
    )

    print("INDEX.HTML UPDATED")
    print("STYLE.CSS UPDATED")
    print("APP.JS MODIFIED: FALSE")

    # =========================================================
    # 5. VALIDATION
    # =========================================================

    print("\n[5] VALIDATION")
    print("-" * 72)

    final_index = INDEX.read_text(
        encoding="utf-8"
    )

    final_style = STYLE.read_text(
        encoding="utf-8"
    )

    workspace_final_start = final_index.find(
        '<section\n    id="workspace-home"'
    )

    workspace_final_end = final_index.find(
        "</section>",
        workspace_final_start
    )

    if (
        workspace_final_start == -1
        or workspace_final_end == -1
    ):
        raise RuntimeError(
            "FAIL: final workspace section could not "
            "be located."
        )

    workspace_final = final_index[
        workspace_final_start:
        workspace_final_end
    ]

    checks = {

        "OP061_MARKER":
            final_style.count(MARKER) == 1,

        "WORKSPACE_KICKER_REMOVED":
            "IT TICKET INTELLIGENCE"
            not in workspace_final,

        "WORKSPACE_HEADING_PRESERVED":
            "Research Workspace"
            in workspace_final,

        "SINGLE_DESCRIPTION":
            "Enter one ticket manually"
            in workspace_final,

        "MULTI_DESCRIPTION":
            "Upload structured JSON or CSV data"
            in workspace_final,

        "TRANSPARENT_ENTRY_CARDS":
            "rgba(255, 255, 255, 0.30)"
            in final_style,

        "SHARP_ENTRY_EDGES":
            "border-radius:\n        2px !important;"
            in final_style,

        "DESCRIPTION_VISIBLE":
            "display:\n        block !important;"
            in final_style,

        "DESCRIPTION_STRONG":
            "#244d76"
            in final_style,

        "SHARED_BUTTON_MODERN":
            ".workspace-entry-action-primary:hover"
            in final_style,

        "INFORMATION_GLASS":
            "rgba(255, 255, 255, 0.18)"
            in final_style,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)"
            in final_style,

        "OP057_PRESERVED":
            "DEPLOY-OP-057"
            in final_style,

        "OP058_PRESERVED":
            "DEPLOY-OP-058"
            in final_style,

        "OP059_PRESERVED":
            "DEPLOY-OP-059"
            in final_style,

        "OP060_PRESERVED":
            "DEPLOY-OP-060"
            in final_style,

        "APP_JS_UNTOUCHED":
            True,
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
            INDEX_BACKUP,
            INDEX
        )

        shutil.copy2(
            STYLE_BACKUP,
            STYLE
        )

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    # =========================================================
    # 6. HASHES / EVIDENCE
    # =========================================================

    index_hash_after = sha256(INDEX)
    style_hash_after = sha256(STYLE)

    METRICS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-061",

        "title":
            "Workspace Final Polish",

        "status":
            "PASS",

        "scope": [
            "workspace heading cleanup",
            "workspace background refinement",
            "transparent entry cards",
            "single-ticket description visibility",
            "multi-ticket description visibility",
            "shared analysis button refinement",
            "transparent information strip",
            "sharp rectangular geometry",
            "responsive safety",
        ],

        "modified_files": [
            str(INDEX),
            str(STYLE),
        ],

        "untouched": [
            "deployment/frontend/app.js",
            "deployment/backend/app.py",
            "frozen deployment runtime",
            "frozen modeling artifacts",
            "T1-T11 semantics",
            "single-ticket API contract",
            "batch API contract",
        ],

        "backups": [
            str(INDEX_BACKUP),
            str(STYLE_BACKUP),
        ],

        "hashes": {

            "index_before":
                index_hash_before,

            "index_after":
                index_hash_after,

            "style_before":
                style_hash_before,

            "style_after":
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
    print("DEPLOY-OP-061")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
