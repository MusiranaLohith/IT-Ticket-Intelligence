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
    FRONTEND / "style.css.before-deploy-op058"
)

EVIDENCE = (
    METRICS / "deploy_op058_landing_contrast_fix.json"
)

MARKER = (
    "DEPLOY-OP-058 — LANDING CONTRAST + VISUAL CORRECTION"
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


def require_once(text, marker, name):
    count = text.count(marker)

    if count != 1:
        raise RuntimeError(
            f"FAIL: {name}: expected exactly 1 match, "
            f"found {count}"
        )


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

    print(f"FOUND: {STYLE}")

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    style_hash_before = sha256(STYLE)

    required_markers = [
        ".project-landing",
        ".project-landing h1",
        ".project-motto",
        ".project-introduction",
        ".project-landing-inner",
        ".project-primary-action",
        ".project-secondary-action",
        ".project-research-strip",
        ".project-feature",
        "body.app-view-landing",
        "DEPLOY-OP-057",
    ]

    for marker in required_markers:

        present = marker in style_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required marker missing: {marker}"
            )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-058 is already present."
        )

    # =========================================================
    # 2. BACKUP
    # =========================================================

    print("\n[2] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        backup_hash = sha256(BACKUP)

        if backup_hash != style_hash_before:
            raise RuntimeError(
                "FAIL: existing OP-058 backup differs "
                "from current style.css."
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
    # 3. FINAL LANDING VISUAL LAYER
    # =========================================================

    print("\n[3] LANDING VISUAL CORRECTION")
    print("-" * 72)

    css_layer = r'''

/* ============================================================
   DEPLOY-OP-058 — LANDING CONTRAST + VISUAL CORRECTION
   ------------------------------------------------------------
   Purpose:
   - Correct legacy !important typography conflicts.
   - Restore strong landing-page readability.
   - Preserve OP-057 architectural background.
   - Preserve existing navigation and actions.
   - CSS presentation only.
   ============================================================ */


/* ------------------------------------------------------------
   LANDING BASE SURFACE
   ------------------------------------------------------------ */

body.app-view-landing {

    background:
        radial-gradient(
            circle at 16% 28%,
            rgba(255, 255, 255, 0.98) 0%,
            rgba(255, 255, 255, 0.00) 36%
        ),
        radial-gradient(
            circle at 82% 18%,
            rgba(96, 165, 250, 0.16) 0%,
            rgba(96, 165, 250, 0.00) 40%
        ),
        linear-gradient(
            135deg,
            #f7fbff 0%,
            #eaf3fc 48%,
            #dceaf8 100%
        ) !important;

    color: #102a4c !important;
}


/* ------------------------------------------------------------
   LANDING ARCHITECTURAL SURFACE
   ------------------------------------------------------------ */

body.app-view-landing .project-landing {

    background:
        linear-gradient(
            126deg,
            rgba(255, 255, 255, 0.86) 0%,
            rgba(255, 255, 255, 0.42) 22%,
            rgba(255, 255, 255, 0.00) 22.5%,
            rgba(255, 255, 255, 0.00) 45%,
            rgba(255, 255, 255, 0.32) 45.4%,
            rgba(255, 255, 255, 0.00) 46.2%
        ),
        linear-gradient(
            118deg,
            transparent 0%,
            transparent 48%,
            rgba(37, 99, 235, 0.09) 48.3%,
            rgba(255, 255, 255, 0.72) 48.7%,
            rgba(255, 255, 255, 0.00) 49.2%,
            transparent 100%
        ),
        linear-gradient(
            132deg,
            transparent 0%,
            transparent 67%,
            rgba(255, 255, 255, 0.74) 67.3%,
            rgba(96, 165, 250, 0.15) 67.8%,
            rgba(255, 255, 255, 0.00) 68.2%,
            transparent 100%
        ),
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.24),
            rgba(255, 255, 255, 0.00)
        ) !important;

    color: #102a4c !important;
}


/* ------------------------------------------------------------
   HERO CONTENT LAYER
   ------------------------------------------------------------ */

body.app-view-landing .project-landing-inner {

    position: relative;

    z-index: 2;

    color: #102a4c !important;
}


/* ------------------------------------------------------------
   KICKER
   ------------------------------------------------------------ */

body.app-view-landing .project-kicker {

    color: #173a62 !important;

    font-weight: 850 !important;

    letter-spacing: 0.16em;

    text-shadow:
        0 1px 0
        rgba(255, 255, 255, 0.72);
}


/* ------------------------------------------------------------
   MAIN HERO TITLE
   ------------------------------------------------------------ */

body.app-view-landing .project-landing h1 {

    color: #102a4c !important;

    -webkit-text-fill-color: #102a4c !important;

    text-shadow:
        0 6px 24px
        rgba(25, 59, 99, 0.08);

    opacity: 1 !important;
}


/* ------------------------------------------------------------
   INTELLIGENCE WORD
   ------------------------------------------------------------ */

body.app-view-landing .project-landing h1 span {

    display: inline-block;

    color: #2474d8 !important;

    background:
        linear-gradient(
            100deg,
            #155dcc 0%,
            #2d83e8 48%,
            #5aa8f4 100%
        );

    background-clip: text;
    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent !important;

    opacity: 1 !important;
}


/* ------------------------------------------------------------
   HERO MOTTO
   ------------------------------------------------------------ */

body.app-view-landing .project-motto {

    color: #193b63 !important;

    -webkit-text-fill-color: #193b63 !important;

    opacity: 1 !important;

    font-weight: 750 !important;

    text-shadow:
        0 1px 0
        rgba(255, 255, 255, 0.65);
}


/* ------------------------------------------------------------
   HERO DESCRIPTION
   ------------------------------------------------------------ */

body.app-view-landing .project-introduction {

    color: #496886 !important;

    -webkit-text-fill-color: #496886 !important;

    opacity: 1 !important;

    font-weight: 500 !important;

    text-shadow:
        0 1px 0
        rgba(255, 255, 255, 0.50);
}


/* ------------------------------------------------------------
   ACTION AREA
   ------------------------------------------------------------ */

body.app-view-landing .project-actions {

    position: relative;

    z-index: 3;
}


/* ------------------------------------------------------------
   PRIMARY ACTION
   ------------------------------------------------------------ */

body.app-view-landing .project-primary-action {

    opacity: 1 !important;

    color: #ffffff !important;

    -webkit-text-fill-color: #ffffff !important;

    background:
        linear-gradient(
            135deg,
            #1769df 0%,
            #2d83e8 100%
        ) !important;

    box-shadow:
        0 14px 32px
        rgba(37, 99, 235, 0.22);
}


/* ------------------------------------------------------------
   SECONDARY ACTION
   ------------------------------------------------------------ */

body.app-view-landing .project-secondary-action {

    opacity: 1 !important;

    color: #173a62 !important;

    -webkit-text-fill-color: #173a62 !important;

    background:
        rgba(255, 255, 255, 0.62) !important;

    border-color:
        rgba(37, 99, 235, 0.34) !important;

    box-shadow:
        0 12px 28px
        rgba(25, 59, 99, 0.08);
}


/* ------------------------------------------------------------
   RESEARCH STRIP
   ------------------------------------------------------------ */

body.app-view-landing .project-research-strip {

    position: relative;

    z-index: 2;

    color: #173a62 !important;

    border-top-color:
        rgba(37, 99, 235, 0.22) !important;

    border-bottom-color:
        rgba(37, 99, 235, 0.22) !important;
}


/* ------------------------------------------------------------
   RESEARCH FEATURE TEXT
   ------------------------------------------------------------ */

body.app-view-landing .project-feature {

    color: #173a62 !important;

    border-color:
        rgba(37, 99, 235, 0.20) !important;
}

body.app-view-landing .project-feature span {

    color: #173a62 !important;

    -webkit-text-fill-color: #173a62 !important;

    opacity: 1 !important;
}

body.app-view-landing .project-feature strong {

    color: #102a4c !important;

    -webkit-text-fill-color: #102a4c !important;

    opacity: 1 !important;
}

body.app-view-landing .project-feature p {

    color: #496886 !important;

    -webkit-text-fill-color: #496886 !important;

    opacity: 1 !important;
}


/* ------------------------------------------------------------
   TECHNICAL DOT FIELD
   ------------------------------------------------------------ */

body.app-view-landing .project-landing::before {

    opacity: 0.24;
}


/* ------------------------------------------------------------
   OP-058 RESPONSIVE CONTRAST
   ------------------------------------------------------------ */

@media (max-width: 620px) {

    body.app-view-landing .project-landing h1 {

        text-shadow:
            0 4px 18px
            rgba(25, 59, 99, 0.07);
    }

    body.app-view-landing .project-motto {

        font-weight: 720 !important;
    }
}


/* ============================================================
   END DEPLOY-OP-058
   ============================================================ */
'''

    if css_layer.count(MARKER) != 1:
        raise RuntimeError(
            "FAIL: generated CSS layer marker invalid."
        )

    style_after_text = style_before + css_layer

    STYLE.write_text(
        style_after_text,
        encoding="utf-8"
    )

    print("STYLE.CSS: UPDATED")

    # =========================================================
    # 4. POST-WRITE VALIDATION
    # =========================================================

    print("\n[4] POST-WRITE VALIDATION")
    print("-" * 72)

    style_after = STYLE.read_text(
        encoding="utf-8"
    )

    checks = {

        "op058_marker_present":
            style_after.count(MARKER) == 1,

        "landing_background_present":
            "body.app-view-landing" in style_after,

        "landing_title_override":
            "body.app-view-landing .project-landing h1"
            in style_after,

        "landing_title_fill_override":
            "-webkit-text-fill-color: #102a4c !important"
            in style_after,

        "intelligence_override":
            "body.app-view-landing .project-landing h1 span"
            in style_after,

        "motto_override":
            "body.app-view-landing .project-motto"
            in style_after,

        "introduction_override":
            "body.app-view-landing .project-introduction"
            in style_after,

        "primary_action_preserved":
            "body.app-view-landing .project-primary-action"
            in style_after,

        "secondary_action_preserved":
            "body.app-view-landing .project-secondary-action"
            in style_after,

        "research_strip_preserved":
            "body.app-view-landing .project-research-strip"
            in style_after,

        "feature_text_preserved":
            "body.app-view-landing .project-feature"
            in style_after,

        "op057_preserved":
            "DEPLOY-OP-057 — PREMIUM LANDING REDESIGN"
            in style_after,
    }

    for name, passed in checks.items():

        print(
            f"{name:42}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):

        print(
            "\nVALIDATION FAILED — RESTORING "
            "PRE-OP-058 STYLESHEET"
        )

        shutil.copy2(
            BACKUP,
            STYLE
        )

        print("RESTORE COMPLETE")
        print("STATUS: FAIL")

        raise SystemExit(1)

    style_hash_after = sha256(STYLE)

    # =========================================================
    # 5. EVIDENCE
    # =========================================================

    evidence = {

        "operation":
            "DEPLOY-OP-058",

        "title":
            "Landing Contrast and Visual Correction",

        "status":
            "PASS",

        "scope": [
            "landing typography contrast",
            "legacy !important conflict resolution",
            "hero title readability",
            "hero motto readability",
            "hero introduction readability",
            "research feature readability",
            "light architectural background preservation",
            "CSS-only presentation correction",
        ],

        "modified_files": [
            str(STYLE),
        ],

        "backups": [
            str(BACKUP),
        ],

        "unchanged": [
            "deployment/frontend/index.html",
            "deployment/frontend/app.js",
            "deployment/backend/app.py",
            "modeling/FMP/deployment/runtime/ticket_pipeline.py",
            "modeling/FMP/deployment/runtime/ticket_explanation.py",
            "frozen modeling artifacts",
            "T1–T11 runtime semantics",
        ],

        "hashes": {
            "style_before": style_hash_before,
            "style_after": style_hash_after,
        },

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

    print("\n" + "=" * 72)
    print("DEPLOY-OP-058")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
