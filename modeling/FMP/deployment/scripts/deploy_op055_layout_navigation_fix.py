from pathlib import Path
import hashlib
import json
import re
import shutil


BASE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = BASE / "deployment/frontend"
METRICS = BASE / "modeling/FMP/metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

INDEX_BACKUP = FRONTEND / "index.html.before-deploy-op055"
APP_BACKUP = FRONTEND / "app.js.before-deploy-op055"
STYLE_BACKUP = FRONTEND / "style.css.before-deploy-op055"

EVIDENCE = METRICS / "deploy_op055_layout_navigation_fix.json"

MARKER = "DEPLOY-OP-055 — LANDING WIDTH + WORKSPACE HOME NAVIGATION"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_file(path):
    if not path.exists():
        raise RuntimeError(f"Required file missing: {path}")


def create_or_verify_backup(source, backup):
    source_hash = sha256(source)

    if backup.exists():
        backup_hash = sha256(backup)

        if backup_hash != source_hash:
            raise RuntimeError(
                f"Existing backup mismatch:\n"
                f"  {backup}\n"
                f"  backup={backup_hash}\n"
                f"  source={source_hash}"
            )

        print(f"BACKUP VERIFIED: {backup}")
        return

    shutil.copy2(source, backup)

    if sha256(backup) != source_hash:
        raise RuntimeError(
            f"Backup integrity failure: {backup}"
        )

    print(f"BACKUP CREATED: {backup}")


def main():
    print("=" * 68)
    print("DEPLOY-OP-055 — LANDING WIDTH + WORKSPACE HOME NAVIGATION")
    print("=" * 68)

    for path in (INDEX, APP, STYLE):
        require_file(path)

    index_before = INDEX.read_text(encoding="utf-8")
    app_before = APP.read_text(encoding="utf-8")
    style_before = STYLE.read_text(encoding="utf-8")

    hashes_before = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    print("\n[1] SOURCE CONTRACT")
    print("-" * 68)

    required_html = [
        'id="project-landing"',
        'id="workspace-home"',
        'class="workspace-heading"',
        'id="open-analysis-workspace-button"',
    ]

    required_js = [
        "function showProjectLanding",
        "function showWorkspaceHome",
        "function showAnalysisWorkspace",
        "initializeProjectNavigation",
    ]

    required_css = [
        ".project-view",
        ".project-landing",
        ".project-landing-inner",
        ".workspace-heading",
        ".workspace-home",
    ]

    for marker in required_html:
        if marker not in index_before:
            raise RuntimeError(
                f"Required HTML marker missing: {marker}"
            )

        print(f"HTML {marker:<42}: FOUND")

    for marker in required_js:
        if marker not in app_before:
            raise RuntimeError(
                f"Required JS marker missing: {marker}"
            )

        print(f"JS   {marker:<42}: FOUND")

    for marker in required_css:
        if marker not in style_before:
            raise RuntimeError(
                f"Required CSS marker missing: {marker}"
            )

        print(f"CSS  {marker:<42}: FOUND")

    if MARKER in index_before or MARKER in app_before or MARKER in style_before:
        raise RuntimeError(
            "DEPLOY-OP-055 marker already exists."
        )

    print("\n[2] BACKUPS")
    print("-" * 68)

    create_or_verify_backup(INDEX, INDEX_BACKUP)
    create_or_verify_backup(APP, APP_BACKUP)
    create_or_verify_backup(STYLE, STYLE_BACKUP)

    # ==========================================================
    # HTML
    # ==========================================================

    print("\n[3] HTML UPDATE")
    print("-" * 68)

    workspace_heading_pattern = re.compile(
        r'''        <div class="workspace-heading">\s*'''
        r'''<div>\s*'''
        r'''<div class="project-kicker">\s*'''
        r'''IT TICKET INTELLIGENCE\s*'''
        r'''</div>\s*'''
        r'''<h2>\s*'''
        r'''Research Workspace\s*'''
        r'''</h2>\s*'''
        r'''<p>\s*'''
        r'''Select how you want to investigate ticket data\.\s*'''
        r'''The same evidence-first T1–T11 pipeline is used\s*'''
        r'''for both input modes\.\s*'''
        r'''</p>\s*'''
        r'''</div>\s*'''
        r'''</div>''',
        re.MULTILINE,
    )

    workspace_heading_replacement = """        <div class="workspace-heading">

            <div class="workspace-heading-copy">

                <div class="project-kicker">
                    IT TICKET INTELLIGENCE
                </div>

                <h2>
                    Research Workspace
                </h2>

                <p>
                    Select how you want to investigate ticket data.
                    The same evidence-first T1–T11 pipeline is used
                    for both input modes.
                </p>

            </div>


            <button
                type="button"
                id="workspace-home-button"
                class="workspace-home-button"
            >
                BACK TO HOME
            </button>

        </div>"""

    index_after, heading_count = (
        workspace_heading_pattern.subn(
            workspace_heading_replacement,
            index_before,
            count=1,
        )
    )

    if heading_count != 1:
        raise RuntimeError(
            "Workspace heading contract was not matched exactly once."
        )

    if 'id="workspace-home-button"' not in index_after:
        raise RuntimeError(
            "Workspace home button was not inserted."
        )

    print("WORKSPACE HEADING PRESERVED: PASS")
    print("BACK TO HOME BUTTON INSERTED: PASS")

    # ==========================================================
    # APP.JS
    # ==========================================================

    print("\n[4] APP.JS UPDATE")
    print("-" * 68)

    navigation_anchor = """    const openAnalysisWorkspaceButton =
        document.getElementById(
            "open-analysis-workspace-button"
        );

"""

    if navigation_anchor not in app_before:
        raise RuntimeError(
            "Shared analysis workspace navigation anchor not found."
        )

    home_declaration = """    const workspaceHomeButton =
        document.getElementById(
            "workspace-home-button"
        );

"""

    app_after = app_before.replace(
        navigation_anchor,
        navigation_anchor + home_declaration,
        1,
    )

    home_listener_anchor = """    if (openAnalysisWorkspaceButton) {
        openAnalysisWorkspaceButton.addEventListener(
            "click",
            showAnalysisWorkspace
        );
    }

"""

    if home_listener_anchor not in app_after:
        raise RuntimeError(
            "Shared analysis workspace listener not found."
        )

    home_listener = """    if (workspaceHomeButton) {
        workspaceHomeButton.addEventListener(
            "click",
            showProjectLanding
        );
    }

"""

    app_after = app_after.replace(
        home_listener_anchor,
        home_listener_anchor + home_listener,
        1,
    )

    if (
        'document.getElementById(\n'
        '            "workspace-home-button"\n'
        '        )'
        not in app_after
    ):
        raise RuntimeError(
            "Workspace home button JS reference missing."
        )

    if "workspaceHomeButton.addEventListener" not in app_after:
        raise RuntimeError(
            "Workspace home button listener missing."
        )

    print("WORKSPACE HOME BUTTON DECLARATION: PASS")
    print("WORKSPACE HOME BUTTON LISTENER: PASS")
    print("DESTINATION: showProjectLanding(): PASS")

    # ==========================================================
    # CSS
    # ==========================================================

    print("\n[5] CSS UPDATE")
    print("-" * 68)

    css_layer = r'''

/* ============================================================
   DEPLOY-OP-055
   LANDING WIDTH + WORKSPACE HOME NAVIGATION
   ------------------------------------------------------------
   Scope:
   - Full-width landing presentation.
   - Preserve centred landing content.
   - Workspace home navigation.
   - Workspace kicker visibility.
   - No analysis/model/runtime changes.
   ============================================================ */


/* ------------------------------------------------------------
   FULL-WIDTH LANDING BACKGROUND
   ------------------------------------------------------------ */

.project-landing {
    width: 100vw !important;

    max-width: none !important;

    margin-left:
        calc(50% - 50vw) !important;

    margin-right:
        calc(50% - 50vw) !important;
}


/* Keep actual landing content centred */

.project-landing-inner {
    width:
        min(
            1180px,
            calc(100% - 48px)
        ) !important;

    margin:
        0 auto !important;
}


/* ------------------------------------------------------------
   WORKSPACE HEADING LAYOUT
   ------------------------------------------------------------ */

.workspace-heading {
    position: relative !important;

    display: flex !important;

    align-items: flex-start !important;

    justify-content: center !important;

    max-width: 1180px !important;

    min-height: 150px !important;

    margin:
        0 auto 30px !important;

    padding:
        0 150px 30px !important;

    border-bottom:
        1px solid
        rgba(44, 83, 124, 0.28) !important;
}


.workspace-heading-copy {
    width: 100% !important;

    max-width: 920px !important;

    text-align: left !important;
}


/* ------------------------------------------------------------
   WORKSPACE KICKER VISIBILITY
   ------------------------------------------------------------ */

.workspace-heading .project-kicker {
    display: inline-flex !important;

    align-items: center !important;

    margin-bottom:
        16px !important;

    padding:
        7px 11px !important;

    color:
        #214f82 !important;

    font-size:
        0.68rem !important;

    font-weight:
        850 !important;

    letter-spacing:
        0.18em !important;

    border:
        1px solid
        rgba(53, 113, 176, 0.32) !important;

    background:
        rgba(222, 239, 255, 0.72) !important;

    box-shadow:
        0 8px 22px
        rgba(41, 92, 143, 0.10) !important;
}


/* ------------------------------------------------------------
   BACK TO HOME
   ------------------------------------------------------------ */

.workspace-home-button {
    position: absolute !important;

    top: 2px !important;

    right: 0 !important;

    min-height:
        46px !important;

    padding:
        0 18px !important;

    color:
        #234c78 !important;

    font-family:
        inherit !important;

    font-size:
        0.70rem !important;

    font-weight:
        850 !important;

    letter-spacing:
        0.075em !important;

    border:
        1px solid
        rgba(63, 113, 163, 0.34) !important;

    border-radius:
        7px !important;

    background:
        rgba(255, 255, 255, 0.56) !important;

    box-shadow:
        0 8px 22px
        rgba(37, 80, 124, 0.10),
        inset 0 1px 0
        rgba(255, 255, 255, 0.72) !important;

    cursor:
        pointer !important;

    backdrop-filter:
        blur(10px);

    transition:
        transform 180ms ease,
        color 180ms ease,
        border-color 180ms ease,
        background 180ms ease,
        box-shadow 180ms ease;
}


.workspace-home-button:hover {
    transform:
        translateY(-2px) !important;

    color:
        #123e6d !important;

    border-color:
        rgba(42, 102, 165, 0.56) !important;

    background:
        rgba(238, 248, 255, 0.84) !important;

    box-shadow:
        0 12px 28px
        rgba(37, 80, 124, 0.15) !important;
}


.workspace-home-button:active {
    transform:
        translateY(0) !important;
}


/* ------------------------------------------------------------
   RESPONSIVE
   ------------------------------------------------------------ */

@media (max-width: 900px) {

    .project-landing-inner {
        width:
            min(
                calc(100% - 36px),
                1180px
            ) !important;
    }

    .workspace-heading {
        padding:
            0 120px 26px 0 !important;
    }

}


@media (max-width: 620px) {

    .project-landing-inner {
        width:
            calc(100% - 28px) !important;
    }

    .workspace-heading {
        display:
            block !important;

        min-height:
            auto !important;

        padding:
            0 0 24px !important;

        text-align:
            left !important;
    }

    .workspace-heading-copy {
        max-width:
            none !important;
    }

    .workspace-home-button {
        position:
            static !important;

        width:
            100% !important;

        margin-top:
            20px !important;
    }

}


/* ============================================================
   END DEPLOY-OP-055
   ============================================================ */
'''

    if MARKER in style_before:
        raise RuntimeError(
            "DEPLOY-OP-055 marker already exists in style.css."
        )

    style_after = style_before + css_layer

    # ==========================================================
    # PRE-WRITE VALIDATION
    # ==========================================================

    print("\n[6] PRE-WRITE VALIDATION")
    print("-" * 68)

    if (
        "id=\"workspace-home-button\"" not in index_after
    ):
        raise RuntimeError(
            "HTML validation failed."
        )

    if (
        "workspaceHomeButton.addEventListener" not in app_after
    ):
        raise RuntimeError(
            "JavaScript validation failed."
        )

    css_required = [
        "DEPLOY-OP-055",
        ".project-landing",
        "width: 100vw !important",
        ".project-landing-inner",
        ".workspace-home-button",
        ".workspace-heading .project-kicker",
        "@media (max-width: 620px)",
    ]

    for marker in css_required:
        if marker not in style_after:
            raise RuntimeError(
                f"CSS validation failed: {marker}"
            )

        print(f"{marker:<42}: PASS")

    # ==========================================================
    # WRITE
    # ==========================================================

    INDEX.write_text(
        index_after,
        encoding="utf-8",
    )

    APP.write_text(
        app_after,
        encoding="utf-8",
    )

    STYLE.write_text(
        style_after,
        encoding="utf-8",
    )

    print("\n[7] FILE UPDATE")
    print("-" * 68)
    print("INDEX.HTML: UPDATED")
    print("APP.JS:     UPDATED")
    print("STYLE.CSS:  UPDATED")

    # ==========================================================
    # FINAL VALIDATION
    # ==========================================================

    index_final = INDEX.read_text(encoding="utf-8")
    app_final = APP.read_text(encoding="utf-8")
    style_final = STYLE.read_text(encoding="utf-8")

    checks = {
        "LANDING_FULL_WIDTH":
            "width: 100vw !important" in style_final,

        "LANDING_CONTENT_CENTRED":
            ".project-landing-inner" in style_final
            and "1180px" in style_final,

        "WORKSPACE_HOME_BUTTON_HTML":
            'id="workspace-home-button"' in index_final,

        "WORKSPACE_HOME_BUTTON_JS":
            "workspaceHomeButton" in app_final,

        "WORKSPACE_HOME_BUTTON_LISTENER":
            "workspaceHomeButton.addEventListener" in app_final,

        "HOME_DESTINATION":
            "showProjectLanding" in app_final,

        "KICKER_VISIBILITY":
            ".workspace-heading .project-kicker" in style_final,

        "RESPONSIVE_HOME_BUTTON":
            "@media (max-width: 620px)" in style_final,

        "TICKET_PIPELINE_UNTOUCHED":
            "TicketPipeline" not in app_final,

        "SKLEARN_UNTOUCHED":
            "sklearn" not in app_final.lower(),
    }

    print("\n[8] FINAL VALIDATION")
    print("-" * 68)

    for name, passed in checks.items():
        print(
            f"{name:<38}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):
        print("\nVALIDATION FAILED — RESTORING ALL FILES")

        shutil.copy2(INDEX_BACKUP, INDEX)
        shutil.copy2(APP_BACKUP, APP)
        shutil.copy2(STYLE_BACKUP, STYLE)

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    hashes_after = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    # ==========================================================
    # EVIDENCE
    # ==========================================================

    evidence = {
        "operation": "DEPLOY-OP-055",
        "title": "Landing Width and Workspace Home Navigation Fix",
        "status": "PASS",
        "scope": [
            "full-width landing visual background",
            "centred landing content preservation",
            "workspace back-to-home navigation",
            "workspace kicker visibility",
            "responsive navigation",
        ],
        "modified_files": [
            str(INDEX),
            str(APP),
            str(STYLE),
        ],
        "backups": [
            str(INDEX_BACKUP),
            str(APP_BACKUP),
            str(STYLE_BACKUP),
        ],
        "unchanged": [
            "deployment/backend/app.py",
            "modeling/FMP/deployment/runtime/ticket_pipeline.py",
            "modeling/FMP/deployment/runtime/ticket_explanation.py",
            "frozen modeling artifacts",
            "T1–T11 runtime semantics",
        ],
        "hashes_before": hashes_before,
        "hashes_after": hashes_after,
        "checks": checks,
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVIDENCE.write_text(
        json.dumps(
            evidence,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nEVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 68)
    print("DEPLOY-OP-055")
    print("STATUS: PASS")
    print("=" * 68)


if __name__ == "__main__":
    main()
