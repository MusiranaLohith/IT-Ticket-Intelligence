from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

STYLE = FRONTEND / "style.css"

BACKUP = (
    FRONTEND / "style.css.before-deploy-op059"
)

EVIDENCE = (
    METRICS
    / "deploy_op059_application_glass_ui.json"
)

MARKER = (
    "DEPLOY-OP-059 — APPLICATION GLASS UI"
)


def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def main():

    print("=" * 72)
    print(MARKER)
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    if not STYLE.exists():
        raise SystemExit(
            f"BLOCKED: missing stylesheet: {STYLE}"
        )

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    print(f"FOUND: {STYLE}")

    required = [
        "DEPLOY-OP-057",
        "DEPLOY-OP-058",
        ".project-landing",
        ".project-landing h1",
        ".workspace-home",
        ".workspace-entry",
        ".workspace-information",
        "#single-ticket-panel",
        ]

    for marker in required:

        present = marker in style_before

        print(
            f"{marker:40} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required CSS marker missing: "
                f"{marker}"
            )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: OP-059 already exists."
        )

    style_hash_before = sha256(STYLE)

    # =========================================================
    # 2. BACKUP
    # =========================================================

    print("\n[2] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        if sha256(BACKUP) != style_hash_before:
            raise RuntimeError(
                "FAIL: existing OP-059 backup does "
                "not match current style.css."
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

    # =========================================================
    # 3. FINAL APPLICATION UI LAYER
    # =========================================================

    print("\n[3] APPLICATION UI REDESIGN")
    print("-" * 72)

    css_layer = r'''

/* ============================================================
   DEPLOY-OP-059 — APPLICATION GLASS UI
   ------------------------------------------------------------
   Final application visual layer.

   Scope:
   - landing hero scale
   - research workspace composition
   - glass input surfaces
   - modern application cards
   - compact fixed-view composition

   No application logic is changed.
   ============================================================ */


/* ============================================================
   01 — LANDING HERO SCALE
   ============================================================ */

body.app-view-landing .project-landing h1 {

    max-width: 720px !important;

    font-size:
        clamp(
            52px,
            5.25vw,
            78px
        ) !important;

    line-height: 0.92 !important;

    letter-spacing:
        -0.052em !important;
}


/* Keep the hero visually centred and breathable. */

body.app-view-landing
.project-landing-inner {

    padding:
        34px 0 28px !important;
}


/* Slightly tighten the supporting copy. */

body.app-view-landing
.project-motto {

    margin-top: 18px !important;

    font-size:
        clamp(
            18px,
            1.55vw,
            23px
        ) !important;
}


body.app-view-landing
.project-introduction {

    margin-top: 12px !important;

    max-width: 720px !important;

    line-height: 1.55 !important;
}


/* Compact evidence strip. */

body.app-view-landing
.project-research-strip {

    margin-top: 24px !important;
}


body.app-view-landing
.project-feature {

    min-height: 142px !important;

    padding:
        20px 22px 18px !important;
}


/* ============================================================
   02 — APPLICATION SURFACES
   ============================================================ */

body:not(.app-view-landing) {

    background:
        linear-gradient(
            135deg,
            #e9f3fc 0%,
            #dbeaf8 48%,
            #cbdff1 100%
        ) !important;
}


/* ============================================================
   03 — SYSTEM WORKSPACE
   ============================================================ */

body:not(.app-view-landing)
.workspace-home {

    position: relative;

    box-sizing: border-box;

    height: calc(100dvh - 80px) !important;

    min-height: calc(100dvh - 80px) !important;

    max-height: calc(100dvh - 80px) !important;

    overflow: hidden !important;

    padding:
        28px 0 24px !important;

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.16),
            rgba(255, 255, 255, 0.02)
        );
}


body:not(.app-view-landing)
.workspace-home::before {

    content: "";

    position: absolute;

    inset: 0;

    pointer-events: none;

    opacity: 0.24;

    background:
        linear-gradient(
            124deg,
            transparent 0%,
            transparent 28%,
            rgba(255, 255, 255, 0.55) 28.4%,
            rgba(255, 255, 255, 0.00) 29%
        ),
        linear-gradient(
            132deg,
            transparent 0%,
            transparent 64%,
            rgba(255, 255, 255, 0.52) 64.4%,
            rgba(255, 255, 255, 0.00) 65%
        );

    z-index: 0;
}


body:not(.app-view-landing)
.workspace-home-inner {

    position: relative;

    z-index: 1;

    width:
        min(
            1120px,
            calc(100% - 48px)
        ) !important;

    height: 100%;

    margin: 0 auto;

    display: flex;

    flex-direction: column;

    box-sizing: border-box;
}


/* ============================================================
   04 — WORKSPACE HEADING
   ============================================================ */

body:not(.app-view-landing)
.workspace-heading {

    flex:
        0 0 auto;

    padding:
        0 0 18px !important;

    margin: 0 !important;

    border-bottom:
        1px solid
        rgba(
            55,
            110,
            168,
            0.24
        ) !important;
}


body:not(.app-view-landing)
.workspace-heading h1 {

    font-size:
        clamp(
            42px,
            4.5vw,
            64px
        ) !important;

    line-height: 0.96 !important;

    letter-spacing:
        -0.045em !important;

    color:
        #102a4c !important;
}


body:not(.app-view-landing)
.workspace-heading p {

    max-width: 760px;

    margin-top: 8px !important;

    color:
        #496886 !important;

    line-height: 1.45 !important;
}


/* ============================================================
   05 — INPUT MODE CARDS
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry-grid {

    flex:
        0 0 auto;

    margin-top: 20px !important;

    gap: 16px !important;
}


body:not(.app-view-landing)
.workspace-entry {

    min-height: 218px !important;

    padding:
        25px !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.82
        ) !important;

    border-radius:
        16px !important;

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.76),
            rgba(244, 249, 255, 0.46)
        ) !important;

    box-shadow:
        0 18px 40px
        rgba(31, 78, 121, 0.10),

        inset 0 1px 0
        rgba(255, 255, 255, 0.95) !important;

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);
}


body:not(.app-view-landing)
.workspace-entry:hover {

    border-color:
        rgba(
            37,
            99,
            235,
            0.42
        ) !important;

    box-shadow:
        0 22px 46px
        rgba(31, 78, 121, 0.14),

        inset 0 1px 0
        rgba(255, 255, 255, 0.98) !important;
}


body:not(.app-view-landing)
.workspace-entry h3 {

    color:
        #132e52 !important;

    letter-spacing:
        -0.025em !important;
}


body:not(.app-view-landing)
.workspace-entry p {

    color:
        #4e6b88 !important;

    line-height:
        1.48 !important;
}


/* ============================================================
   06 — SHARED ANALYSIS BUTTON
   ============================================================ */

body:not(.app-view-landing)
.workspace-entry-shared-action {

    flex:
        0 0 auto;

    display: flex;

    justify-content: center;

    padding:
        14px 0 16px !important;
}


body:not(.app-view-landing)
.workspace-entry-action-primary {

    min-width:
        440px !important;

    min-height:
        54px !important;

    border-radius:
        10px !important;

    box-shadow:
        0 14px 30px
        rgba(37, 99, 235, 0.20),

        inset 0 1px 0
        rgba(255, 255, 255, 0.32) !important;
}


/* ============================================================
   07 — WORKSPACE INFORMATION STRIP
   ============================================================ */

body:not(.app-view-landing)
.workspace-information-grid {

    flex:
        1 1 auto;

    min-height:
        108px !important;

    margin-top: 0 !important;

    overflow: hidden;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.72
        ) !important;

    border-radius:
        12px !important;

    background:
        rgba(
            255,
            255,
            255,
            0.34
        ) !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.78),

        0 14px 32px
        rgba(31, 78, 121, 0.07) !important;

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);
}


body:not(.app-view-landing)
.workspace-information {

    padding:
        16px 20px !important;

    background:
        rgba(
            255,
            255,
            255,
            0.12
        ) !important;

    border-color:
        rgba(
            55,
            110,
            168,
            0.16
        ) !important;
}


body:not(.app-view-landing)
.workspace-information h4 {

    color:
        #244a70 !important;

    font-size:
        11px !important;

    letter-spacing:
        0.13em !important;
}


body:not(.app-view-landing)
.workspace-information p {

    color:
        #526f8b !important;
}


/* ============================================================
   08 — SINGLE TICKET APPLICATION PANEL
   ============================================================ */

body:not(.app-view-landing)
#single-ticket-panel {

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;
}


body:not(.app-view-landing)
#single-ticket-panel > *,
body:not(.app-view-landing)
#ticket-form {

    border-radius:
        16px !important;
}


/* Main white application surface becomes glass. */

body:not(.app-view-landing)
#ticket-form {

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.68),
            rgba(246, 250, 255, 0.40)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.82
        ) !important;

    box-shadow:
        0 20px 48px
        rgba(31, 78, 121, 0.11),

        inset 0 1px 0
        rgba(255, 255, 255, 0.94) !important;

    backdrop-filter:
        blur(20px);

    -webkit-backdrop-filter:
        blur(20px);
}


/* ============================================================
   09 — FORM CONTROLS
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
            0.48
        ) !important;

    border:
        1px solid
        rgba(
            74,
            126,
            181,
            0.30
        ) !important;

    border-radius:
        8px !important;

    box-shadow:
        inset 0 1px 2px
        rgba(31, 78, 121, 0.035) !important;

    color:
        #183a60 !important;

    backdrop-filter:
        blur(8px);
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
            0.64
        ) !important;

    box-shadow:
        0 0 0 3px
        rgba(
            37,
            99,
            235,
            0.10
        ) !important;

    outline:
        none !important;
}


/* ============================================================
   10 — FORM LABELS
   ============================================================ */

body:not(.app-view-landing)
#ticket-form label {

    color:
        #193b63 !important;

    font-weight:
        750 !important;
}


/* ============================================================
   11 — ANALYZE BUTTON
   ============================================================ */

body:not(.app-view-landing)
#ticket-form button {

    border-radius:
        9px !important;

    box-shadow:
        0 12px 26px
        rgba(37, 99, 235, 0.18),

        inset 0 1px 0
        rgba(255, 255, 255, 0.28) !important;
}


/* ============================================================
   12 — RESPONSIVE SAFETY
   ============================================================ */

@media (max-width: 980px) {

    body:not(.app-view-landing)
    .workspace-home {

        height: auto !important;

        min-height:
            calc(100dvh - 80px) !important;

        max-height: none !important;

        overflow: visible !important;
    }

    body:not(.app-view-landing)
    .workspace-home-inner {

        height: auto !important;
    }

    body:not(.app-view-landing)
    .workspace-information-grid {

        min-height: 120px !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-action-primary {

        min-width:
            320px !important;
    }
}


@media (max-width: 620px) {

    body:not(.app-view-landing)
    .workspace-home {

        padding:
            20px 0 !important;
    }

    body:not(.app-view-landing)
    .workspace-home-inner {

        width:
            calc(100% - 28px) !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-grid {

        grid-template-columns:
            1fr !important;
    }

    body:not(.app-view-landing)
    .workspace-entry-action-primary {

        min-width:
            100% !important;
    }

    body:not(.app-view-landing)
    .ticket-form {

        padding:
            20px !important;
    }
}


/* ============================================================
   END DEPLOY-OP-059
   ============================================================ */
'''

    STYLE.write_text(
        style_before + css_layer,
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

        "OP059_MARKER":
            style_after.count(MARKER) == 1,

        "LANDING_TITLE_SCALE":
            "5.25vw" in style_after,

        "WORKSPACE_FIXED_VIEW":
            "height: calc(100dvh - 80px)" in style_after,

        "WORKSPACE_COMPACT_PADDING":
            "padding:\n        28px 0 24px" in style_after,

        "WORKSPACE_GLASS_CARD":
            "workspace-entry" in style_after
            and "backdrop-filter" in style_after,

        "WORKSPACE_INFO_STRIP":
            ".workspace-information-grid" in style_after,

        "SHARED_ACTION":
            ".workspace-entry-action-primary" in style_after,

        "TICKET_FORM_GLASS":
            "#ticket-form" in style_after
            and "rgba(255, 255, 255, 0.68)" in style_after,

        "FORM_CONTROL_GLASS":
            "#ticket-form input" in style_after,

        "FORM_FOCUS_STYLE":
            "#ticket-form input:focus" in style_after,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)" in style_after,

        "OP057_PRESERVED":
            "DEPLOY-OP-057" in style_after,

        "OP058_PRESERVED":
            "DEPLOY-OP-058" in style_after,
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

    METRICS.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-059",

        "title":
            "Application Glass UI",

        "status":
            "PASS",

        "scope": [
            "landing hero scale",
            "research workspace composition",
            "workspace information visibility",
            "glass input-mode cards",
            "glass single-ticket form",
            "glass form controls",
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
            "T1–T11 semantics",
            "single-ticket API contract",
            "batch API contract",
        ],

        "hashes": {
            "before":
                style_hash_before,
            "after":
                style_hash_after,
        },

        "checks": checks,
    }

    EVIDENCE.write_text(
        json.dumps(
            evidence,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"\nEVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-059")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
