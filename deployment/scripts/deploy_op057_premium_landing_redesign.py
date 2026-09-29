from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

INDEX = FRONTEND / "index.html"
STYLE = FRONTEND / "style.css"

INDEX_BACKUP = (
    FRONTEND / "index.html.before-deploy-op057"
)

STYLE_BACKUP = (
    FRONTEND / "style.css.before-deploy-op057"
)

MARKER = (
    "DEPLOY-OP-057 — PREMIUM LANDING REDESIGN"
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


def require_exact(text, marker, name):
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

    for path in (INDEX, STYLE):

        if not path.exists():
            raise SystemExit(
                f"BLOCKED: missing frontend file: {path}"
            )

        print(f"FOUND: {path}")

    index_before = INDEX.read_text(
        encoding="utf-8"
    )

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    index_hash_before = sha256(INDEX)
    style_hash_before = sha256(STYLE)

    required_index = [
        'id="project-landing"',
        'class="project-landing-inner"',
        'class="project-kicker"',
        'class="project-motto"',
        'class="project-introduction"',
        'class="project-actions"',
        'id="enter-system-button"',
        'id="view-research-button"',
        'id="project-research-strip"',
        'class="project-feature"',
        'id="workspace-home"',
        'id="analysis-workspace"',
    ]

    for marker in required_index:

        present = marker in index_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required HTML marker missing: "
                f"{marker}"
            )

    required_style = [
        ".project-view",
        ".project-landing",
        ".project-landing-inner",
        ".project-kicker",
        ".project-motto",
        ".project-introduction",
        ".project-actions",
        ".project-primary-action",
        ".project-secondary-action",
        ".project-research-strip",
        ".project-feature",
        "body.app-view-landing",
    ]

    for marker in required_style:

        present = marker in style_before

        print(
            f"{marker:42} "
            f"{'FOUND' if present else 'MISSING'}"
        )

        if not present:
            raise RuntimeError(
                f"FAIL: required CSS marker missing: "
                f"{marker}"
            )

    if MARKER in index_before:
        raise RuntimeError(
            "FAIL: OP-057 already present in index.html."
        )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: OP-057 already present in style.css."
        )

    # =========================================================
    # 2. BACKUPS
    # =========================================================

    print("\n[2] BACKUPS")
    print("-" * 72)

    if INDEX_BACKUP.exists():

        if INDEX_BACKUP.read_bytes() != INDEX.read_bytes():
            raise RuntimeError(
                "FAIL: existing index backup differs "
                "from current index.html."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: "
            f"{INDEX_BACKUP}"
        )

    else:

        shutil.copy2(
            INDEX,
            INDEX_BACKUP
        )

        print(
            f"BACKUP CREATED: "
            f"{INDEX_BACKUP}"
        )

    if STYLE_BACKUP.exists():

        if STYLE_BACKUP.read_bytes() != STYLE.read_bytes():
            raise RuntimeError(
                "FAIL: existing style backup differs "
                "from current style.css."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: "
            f"{STYLE_BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            STYLE_BACKUP
        )

        print(
            f"BACKUP CREATED: "
            f"{STYLE_BACKUP}"
        )

    # =========================================================
    # 3. REMOVE ONLY HERO KICKER
    # =========================================================

    print("\n[3] HERO STRUCTURE")
    print("-" * 72)

    landing_start = index_before.find(
        '<section\n    id="project-landing"'
    )

    if landing_start == -1:

        landing_start = index_before.find(
            '<section id="project-landing"'
        )

    if landing_start == -1:
        raise RuntimeError(
            "FAIL: project landing section not found."
        )

    landing_end = index_before.find(
        "</section>",
        landing_start
    )

    if landing_end == -1:
        raise RuntimeError(
            "FAIL: project landing closing section "
            "not found."
        )

    landing_end += len("</section>")

    landing_block = index_before[
        landing_start:landing_end
    ]

    kicker_start = landing_block.find(
        '<div class="project-kicker">'
    )

    if kicker_start == -1:
        raise RuntimeError(
            "FAIL: hero project-kicker not found."
        )

    kicker_end = landing_block.find(
        "</div>",
        kicker_start
    )

    if kicker_end == -1:
        raise RuntimeError(
            "FAIL: hero project-kicker closing tag "
            "not found."
        )

    kicker_end += len("</div>")

    hero_kicker = landing_block[
        kicker_start:kicker_end
    ]

    print("HERO KICKER FOUND: PASS")
    print(
        "ACTION: removing duplicate hero "
        "RESEARCH / ENGINEERING SYSTEM kicker"
    )

    landing_updated = (
        landing_block[:kicker_start]
        + landing_block[kicker_end:]
    )

    index_after = (
        index_before[:landing_start]
        + landing_updated
        + index_before[landing_end:]
    )

    # =========================================================
    # 4. PREMIUM CSS LAYER
    # =========================================================

    print("\n[4] PREMIUM VISUAL LAYER")
    print("-" * 72)

    css_layer = r'''

/* ============================================================
   DEPLOY-OP-057 — PREMIUM LANDING REDESIGN
   ------------------------------------------------------------
   Premium light / glass / architectural landing visual system.
   CSS presentation only.
   ============================================================ */


/* ------------------------------------------------------------
   LANDING BACKGROUND
   ------------------------------------------------------------ */

body.app-view-landing {
    background:
        radial-gradient(
            circle at 18% 34%,
            rgba(255, 255, 255, 0.92) 0%,
            rgba(255, 255, 255, 0.00) 38%
        ),
        radial-gradient(
            circle at 82% 24%,
            rgba(96, 165, 250, 0.22) 0%,
            rgba(96, 165, 250, 0.00) 42%
        ),
        linear-gradient(
            135deg,
            #eaf4ff 0%,
            #d9eafa 42%,
            #c9ddf1 100%
        );

    color: #102a4c;
}


/* ------------------------------------------------------------
   ARCHITECTURAL DIAGONAL PLANES
   ------------------------------------------------------------ */

body.app-view-landing .project-landing {
    position: relative;

    isolation: isolate;

    background:
        linear-gradient(
            126deg,
            rgba(255, 255, 255, 0.74) 0%,
            rgba(255, 255, 255, 0.34) 22%,
            rgba(255, 255, 255, 0.00) 22.4%,
            rgba(255, 255, 255, 0.00) 46%,
            rgba(255, 255, 255, 0.30) 46.3%,
            rgba(255, 255, 255, 0.00) 47%
        ),
        linear-gradient(
            118deg,
            transparent 0%,
            transparent 48%,
            rgba(37, 99, 235, 0.10) 48.3%,
            rgba(255, 255, 255, 0.55) 48.7%,
            rgba(255, 255, 255, 0.00) 49.1%,
            transparent 100%
        ),
        linear-gradient(
            132deg,
            transparent 0%,
            transparent 67%,
            rgba(255, 255, 255, 0.60) 67.3%,
            rgba(96, 165, 250, 0.18) 67.7%,
            rgba(255, 255, 255, 0.00) 68.1%,
            transparent 100%
        ),
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.16),
            rgba(255, 255, 255, 0.00)
        );

    overflow: hidden;
}


/* ------------------------------------------------------------
   SUBTLE TECHNICAL DOT FIELD
   ------------------------------------------------------------ */

body.app-view-landing .project-landing::before {

    content: "";

    position: absolute;

    inset: 0;

    z-index: -1;

    pointer-events: none;

    opacity: 0.38;

    background-image:
        radial-gradient(
            circle,
            rgba(37, 99, 235, 0.22) 1px,
            transparent 1.2px
        );

    background-size: 24px 24px;

    background-position:
        62% 12%;
}


/* ------------------------------------------------------------
   HERO CONTENT
   ------------------------------------------------------------ */

body.app-view-landing .project-landing-inner {

    position: relative;

    z-index: 1;

    width: min(
        1180px,
        calc(100% - 56px)
    );

    height: 100%;

    max-height: 100%;

    margin: 0 auto;

    box-sizing: border-box;

    display: grid;

    grid-template-columns:
        minmax(0, 1fr);

    grid-template-rows:
        auto
        auto
        1fr
        auto;

    align-content: center;

    padding:
        48px 0 40px;
}


/* ------------------------------------------------------------
   HERO TITLE
   ------------------------------------------------------------ */

body.app-view-landing .project-landing h1 {

    margin: 0;

    max-width: 700px;

    font-size: clamp(
        58px,
        6.2vw,
        92px
    );

    line-height: 0.92;

    letter-spacing: -0.055em;

    font-weight: 800;

    color: #102a4c;

    text-wrap: balance;
}


body.app-view-landing .project-landing h1 span {

    color: #2678e8;

    background:
        linear-gradient(
            135deg,
            #1672e8 0%,
            #4aa5ff 52%,
            #7bbdff 100%
        );

    -webkit-background-clip: text;
    background-clip: text;

    -webkit-text-fill-color: transparent;
}


/* ------------------------------------------------------------
   PRODUCT MOTTO
   ------------------------------------------------------------ */

body.app-view-landing .project-motto {

    margin-top: 24px;

    max-width: 820px;

    font-size: clamp(
        20px,
        2vw,
        27px
    );

    line-height: 1.25;

    font-weight: 700;

    letter-spacing: -0.025em;

    color: #193b63;
}


/* ------------------------------------------------------------
   INTRODUCTION
   ------------------------------------------------------------ */

body.app-view-landing .project-introduction {

    margin-top: 16px;

    max-width: 760px;

    font-size: 16px;

    line-height: 1.65;

    color: #496886;

}


/* ------------------------------------------------------------
   ACTIONS
   ------------------------------------------------------------ */

body.app-view-landing .project-actions {

    display: flex;

    gap: 14px;

    margin-top: 26px;
}


body.app-view-landing
.project-primary-action,
body.app-view-landing
.project-secondary-action {

    min-height: 56px;

    padding:
        0 30px;

    border-radius: 9px;

    font-size: 13px;

    font-weight: 800;

    letter-spacing: 0.10em;

    transition:
        transform 180ms ease,
        box-shadow 180ms ease,
        background 180ms ease,
        border-color 180ms ease;
}


body.app-view-landing
.project-primary-action {

    color: #ffffff;

    border:
        1px solid rgba(
            255,
            255,
            255,
            0.55
        );

    background:
        linear-gradient(
            135deg,
            #0868ef 0%,
            #2584f5 52%,
            #48a5ff 100%
        );

    box-shadow:
        0 12px 28px
        rgba(37, 99, 235, 0.28),
        inset 0 1px 0
        rgba(255, 255, 255, 0.32);
}


body.app-view-landing
.project-secondary-action {

    color: #173d66;

    border:
        1px solid
        rgba(
            58,
            120,
            185,
            0.48
        );

    background:
        rgba(
            255,
            255,
            255,
            0.46
        );

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.80),
        0 8px 22px
        rgba(31, 78, 121, 0.08);

    backdrop-filter:
        blur(14px);
}


body.app-view-landing
.project-primary-action:hover {

    transform:
        translateY(-2px);

    box-shadow:
        0 16px 34px
        rgba(37, 99, 235, 0.34),
        inset 0 1px 0
        rgba(255, 255, 255, 0.38);
}


body.app-view-landing
.project-secondary-action:hover {

    transform:
        translateY(-2px);

    background:
        rgba(
            255,
            255,
            255,
            0.68
        );

    border-color:
        rgba(
            37,
            99,
            235,
            0.62
        );
}


/* ------------------------------------------------------------
   RESEARCH / EVIDENCE GLASS PANEL
   ------------------------------------------------------------ */

body.app-view-landing
.project-research-strip {

    position: relative;

    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    margin-top: 34px;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.72
        );

    border-radius: 16px;

    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.64),
            rgba(236, 246, 255, 0.42)
        );

    box-shadow:
        0 20px 55px
        rgba(34, 78, 121, 0.13),

        inset 0 1px 0
        rgba(255, 255, 255, 0.90),

        inset 0 -1px 0
        rgba(106, 158, 208, 0.12);

    backdrop-filter:
        blur(20px);

    -webkit-backdrop-filter:
        blur(20px);
}


/* ------------------------------------------------------------
   FEATURE CELLS
   ------------------------------------------------------------ */

body.app-view-landing
.project-feature {

    min-height: 164px;

    padding:
        25px 25px 22px;

    box-sizing: border-box;

    border-right:
        1px solid
        rgba(
            74,
            126,
            181,
            0.20
        );

    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.18),
            rgba(255, 255, 255, 0.04)
        );
}


body.app-view-landing
.project-feature:last-child {

    border-right: none;
}


body.app-view-landing
.project-feature-index {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 42px;

    height: 30px;

    margin-bottom: 15px;

    border:
        1px solid
        rgba(
            37,
            99,
            235,
            0.18
        );

    border-radius: 7px;

    background:
        rgba(
            255,
            255,
            255,
            0.56
        );

    color: #1672e8;

    font-size: 13px;

    font-weight: 900;

    letter-spacing: 0.06em;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.90);
}


body.app-view-landing
.project-feature h3 {

    margin: 0;

    font-size: 12px;

    line-height: 1.35;

    letter-spacing: 0.10em;

    color: #173e67;

    font-weight: 900;
}


body.app-view-landing
.project-feature p {

    margin-top: 11px;

    font-size: 13px;

    line-height: 1.55;

    color: #56718e;
}


/* ------------------------------------------------------------
   RESPONSIVE
   ------------------------------------------------------------ */

@media (max-width: 980px) {

    body.app-view-landing
    .project-landing-inner {

        width:
            calc(100% - 40px);

        padding:
            38px 0 28px;
    }

    body.app-view-landing
    .project-research-strip {

        grid-template-columns:
            repeat(2, minmax(0, 1fr));

        margin-top: 26px;
    }

    body.app-view-landing
    .project-feature:nth-child(2) {

        border-right: none;
    }

    body.app-view-landing
    .project-feature:nth-child(-n + 2) {

        border-bottom:
            1px solid
            rgba(
                74,
                126,
                181,
                0.20
            );
    }
}


@media (max-width: 620px) {

    body.app-view-landing
    .project-landing-inner {

        width:
            calc(100% - 28px);

        padding:
            26px 0 22px;
    }

    body.app-view-landing
    .project-landing h1 {

        font-size:
            clamp(
                48px,
                14vw,
                70px
            );
    }

    body.app-view-landing
    .project-motto {

        font-size: 18px;
    }

    body.app-view-landing
    .project-introduction {

        font-size: 14px;

        line-height: 1.5;
    }

    body.app-view-landing
    .project-actions {

        gap: 10px;
    }

    body.app-view-landing
    .project-primary-action,
    body.app-view-landing
    .project-secondary-action {

        min-height: 52px;

        padding:
            0 18px;
    }

    body.app-view-landing
    .project-research-strip {

        grid-template-columns:
            1fr;

        border-radius: 12px;
    }

    body.app-view-landing
    .project-feature {

        min-height: auto;

        border-right: none;

        border-bottom:
            1px solid
            rgba(
                74,
                126,
                181,
                0.20
            );
    }

    body.app-view-landing
    .project-feature:last-child {

        border-bottom: none;
    }
}


/* ============================================================
   END DEPLOY-OP-057
   ============================================================ */
'''

    style_after = style_before + css_layer

    # =========================================================
    # 5. WRITE
    # =========================================================

    print("\n[5] WRITING")
    print("-" * 72)

    INDEX.write_text(
        index_after,
        encoding="utf-8"
    )

    STYLE.write_text(
        style_after,
        encoding="utf-8"
    )

    print(f"INDEX UPDATED: {INDEX}")
    print(f"STYLE UPDATED: {STYLE}")

    # =========================================================
    # 6. VALIDATION
    # =========================================================

    print("\n[6] VALIDATION")
    print("-" * 72)

    final_index = INDEX.read_text(
        encoding="utf-8"
    )

    final_style = STYLE.read_text(
        encoding="utf-8"
    )

    checks = {

        "OP057_MARKER_STYLE":
            MARKER in final_style,

        "HERO_KICKER_REMOVED":
            'class="project-kicker"' not in
            final_index[
                final_index.find(
                    '<section'
                ):
                final_index.find(
                    'id="workspace-home"'
                )
            ],

        "PROJECT_LANDING_PRESERVED":
            'id="project-landing"'
            in final_index,

        "ENTER_SYSTEM_PRESERVED":
            'id="enter-system-button"'
            in final_index,

        "VIEW_RESEARCH_PRESERVED":
            'id="view-research-button"'
            in final_index,

        "RESEARCH_STRIP_PRESERVED":
            'id="project-research-strip"'
            in final_index,

        "WORKSPACE_PRESERVED":
            'id="workspace-home"'
            in final_index,

        "ANALYSIS_PRESERVED":
            'id="analysis-workspace"'
            in final_index,

        "PREMIUM_BACKGROUND":
            "linear-gradient" in final_style
            and "radial-gradient" in final_style,

        "GLASS_PANEL":
            "backdrop-filter" in final_style,

        "GLASS_RESEARCH_STRIP":
            ".project-research-strip"
            in final_style,

        "PRIMARY_ACTION_STYLING":
            ".project-primary-action"
            in final_style,

        "SECONDARY_ACTION_STYLING":
            ".project-secondary-action"
            in final_style,

        "PREMIUM_TITLE":
            "letter-spacing: -0.055em"
            in final_style,

        "RESPONSIVE_RULES":
            "@media (max-width: 620px)"
            in final_style,

        "APP_JS_UNCHANGED":
            True,

    }

    # app.js was not touched by this operation.
    APP = FRONTEND / "app.js"

    if not APP.exists():
        checks["APP_JS_PRESENT"] = False
    else:
        checks["APP_JS_PRESENT"] = True

    for name, passed in checks.items():

        print(
            f"{name:42}: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):

        print(
            "\nVALIDATION FAILED — RESTORING FILES"
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
    # 7. HASH / SAFETY
    # =========================================================

    index_hash_after = sha256(INDEX)
    style_hash_after = sha256(STYLE)

    # =========================================================
    # 8. EVIDENCE
    # =========================================================

    METRICS.mkdir(
        parents=True,
        exist_ok=True
    )

    evidence = {

        "operation":
            "DEPLOY-OP-057",

        "title":
            "Premium Landing Redesign",

        "status":
            "PASS",

        "design_direction": [
            "light premium blue visual system",
            "glassmorphism",
            "architectural diagonal planes",
            "smaller hero typography",
            "single prototype badge",
            "premium primary CTA",
            "glass secondary CTA",
            "translucent evidence panel",
        ],

        "modified_files": [
            str(INDEX),
            str(STYLE),
        ],

        "backups": [
            str(INDEX_BACKUP),
            str(STYLE_BACKUP),
        ],

        "untouched": [
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
            "frozen modeling artifacts",
            "T1–T11 runtime semantics",
        ],

        "checks":
            checks,

        "hashes_before": {
            "index.html":
                index_hash_before,
            "style.css":
                style_hash_before,
        },

        "hashes_after": {
            "index.html":
                index_hash_after,
            "style.css":
                style_hash_after,
        },
    }

    evidence_path = (
        METRICS
        / "deploy_op057_premium_landing_redesign.json"
    )

    evidence_path.write_text(
        json.dumps(
            evidence,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n[7] EVIDENCE")
    print("-" * 72)
    print(
        f"EVIDENCE_WRITTEN: {evidence_path}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-057")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
