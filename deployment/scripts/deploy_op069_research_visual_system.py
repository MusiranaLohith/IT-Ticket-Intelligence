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
INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"

BACKUP = (
    FRONTEND
    / "style.css.before-deploy-op069"
)

EVIDENCE = (
    METRICS
    / "deploy_op069_research_visual_system.json"
)

MARKER = (
    "DEPLOY-OP-069 — RESEARCH VIEW VISUAL SYSTEM"
)


def sha256(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


CSS_LAYER = r"""
/* ============================================================
   DEPLOY-OP-069 — RESEARCH VIEW VISUAL SYSTEM
   ------------------------------------------------------------
   CSS ONLY.
   Research presentation styling.
   Does not modify ticket analysis semantics.
   Does not modify application logic.
   ============================================================ */


/* ============================================================
   01 — RESEARCH VIEW / VIEWPORT
   ============================================================ */

body.app-view-research {

    overflow-x: hidden;
    overflow-y: auto;

    background:
        radial-gradient(
            circle at 8% 4%,
            rgba(
                33,
                103,
                232,
                0.10
            ),
            transparent 28rem
        ),
        radial-gradient(
            circle at 92% 18%,
            rgba(
                22,
                118,
                74,
                0.055
            ),
            transparent 26rem
        ),
        linear-gradient(
            180deg,
            #f5f8fc 0%,
            #edf3f9 48%,
            #e9f0f7 100%
        );
}


body.app-view-research .research-overview {

    width:
        min(
            1240px,
            calc(100% - 48px)
        );

    margin:
        0 auto;

    padding:
        58px 0 84px;
}


body.app-view-research
.research-overview-inner {

    width:
        min(
            1120px,
            100%
        );

    margin:
        0 auto;
}


/* ============================================================
   02 — RESEARCH HEADER
   ============================================================ */

.research-overview-header {

    position: relative;

    margin-bottom:
        28px;

    padding:
        42px 44px 38px;

    border:
        1px solid
        rgba(
            23,
            79,
            183,
            0.22
        );

    border-radius:
        18px;

    background:
        linear-gradient(
            135deg,
            rgba(
                255,
                255,
                255,
                0.82
            ),
            rgba(
                237,
                246,
                255,
                0.70
            )
        );

    box-shadow:
        0 22px 60px
        rgba(
            20,
            47,
            78,
            0.11
        );

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);

    overflow:
        hidden;
}


.research-overview-header::before {

    content:
        "";

    position:
        absolute;

    top:
        0;

    left:
        0;

    width:
        100%;

    height:
        4px;

    background:
        linear-gradient(
            90deg,
            #174fb7 0%,
            #2167e8 55%,
            #16764a 100%
        );
}


.research-overview-header::after {

    content:
        "";

    position:
        absolute;

    width:
        260px;

    height:
        260px;

    right:
        -120px;

    top:
        -150px;

    border-radius:
        50%;

    background:
        rgba(
            33,
            103,
            232,
            0.08
        );

    pointer-events:
        none;
}


.research-overview-header .project-kicker {

    display:
        inline-flex;

    align-items:
        center;

    min-height:
        28px;

    padding:
        0 11px;

    border:
        1px solid
        rgba(
            33,
            103,
            232,
            0.22
        );

    border-radius:
        999px;

    background:
        rgba(
            33,
            103,
            232,
            0.07
        );

    color:
        #174fb7;

    font-size:
        0.68rem;

    font-weight:
        800;

    letter-spacing:
        0.16em;
}


.research-overview-header h2 {

    position:
        relative;

    z-index:
        1;

    max-width:
        820px;

    margin:
        18px 0 12px;

    color:
        #162033;

    font-size:
        clamp(
            2.1rem,
            4vw,
            3.45rem
        );

    line-height:
        1.03;

    letter-spacing:
        -0.045em;
}


.research-overview-header p {

    position:
        relative;

    z-index:
        1;

    max-width:
        820px;

    margin:
        0 0 24px;

    color:
        #526176;

    font-size:
        1.05rem;

    line-height:
        1.7;
}


/* ============================================================
   03 — NAVIGATION
   ============================================================ */

.research-home-button {

    position:
        relative;

    z-index:
        2;

    min-height:
        42px;

    padding:
        0 18px;

    border:
        1px solid
        #2167e8;

    border-radius:
        8px;

    background:
        rgba(
            255,
            255,
            255,
            0.72
        );

    color:
        #174fb7;

    font-size:
        0.72rem;

    font-weight:
        800;

    letter-spacing:
        0.10em;

    cursor:
        pointer;

    box-shadow:
        0 8px 22px
        rgba(
            23,
            79,
            183,
            0.10
        );

    transition:
        transform 160ms ease,
        background 160ms ease,
        color 160ms ease,
        box-shadow 160ms ease;
}


.research-home-button:hover {

    transform:
        translateY(-2px);

    background:
        #2167e8;

    color:
        #ffffff;

    box-shadow:
        0 12px 28px
        rgba(
            23,
            79,
            183,
            0.18
        );
}


#research-home-button-footer {

    min-height:
        48px;

    padding:
        0 24px;

    background:
        linear-gradient(
            135deg,
            #174fb7,
            #2167e8
        );

    color:
        #ffffff;

    box-shadow:
        0 12px 28px
        rgba(
            23,
            79,
            183,
            0.20
        );
}


#research-home-button-footer:hover {

    background:
        linear-gradient(
            135deg,
            #0d47b5,
            #174fb7
        );
}


/* ============================================================
   04 — RESEARCH SECTIONS
   ============================================================ */

.research-section {

    position:
        relative;

    margin:
        18px 0;

    padding:
        32px 36px 34px;

    border:
        1px solid
        rgba(
            74,
            126,
            181,
            0.18
        );

    border-left:
        4px solid
        #2167e8;

    border-radius:
        14px;

    background:
        rgba(
            255,
            255,
            255,
            0.70
        );

    box-shadow:
        0 14px 38px
        rgba(
            20,
            47,
            78,
            0.065
        );

    backdrop-filter:
        blur(14px);

    -webkit-backdrop-filter:
        blur(14px);
}


.research-section-label {

    display:
        inline-flex;

    align-items:
        center;

    min-height:
        26px;

    padding:
        0 10px;

    margin-bottom:
        12px;

    border:
        1px solid
        rgba(
            33,
            103,
            232,
            0.18
        );

    border-radius:
        5px;

    background:
        rgba(
            33,
            103,
            232,
            0.065
        );

    color:
        #174fb7;

    font-size:
        0.67rem;

    font-weight:
        850;

    letter-spacing:
        0.13em;
}


.research-section h3 {

    margin:
        0 0 16px;

    color:
        #162033;

    font-size:
        clamp(
            1.25rem,
            2vw,
            1.65rem
        );

    line-height:
        1.2;

    letter-spacing:
        -0.025em;
}


.research-section p {

    max-width:
        980px;

    margin:
        0 0 16px;

    color:
        #26364d;

    font-size:
        0.98rem;

    line-height:
        1.72;
}


.research-section p:last-child {

    margin-bottom:
        0;
}


/* ============================================================
   05 — SECTION SEMANTIC ACCENTS
   ============================================================ */

/* 01 — Problem */
.research-section:nth-of-type(1) {

    border-left-color:
        #2167e8;
}


/* 02 — Objective */
.research-section:nth-of-type(2) {

    border-left-color:
        #174fb7;

    background:
        linear-gradient(
            135deg,
            rgba(
                234,
                242,
                255,
                0.80
            ),
            rgba(
                255,
                255,
                255,
                0.70
            )
        );
}


/* 03 — Workflow */
.research-section:nth-of-type(3) {

    border-left-color:
        #2167e8;
}


.research-section:nth-of-type(3) ol {

    margin:
        18px 0 0;

    padding:
        20px 24px 20px 46px;

    border:
        1px solid
        rgba(
            33,
            103,
            232,
            0.14
        );

    border-radius:
        10px;

    background:
        rgba(
            234,
            242,
            255,
            0.55
        );

    color:
        #233651;
}


.research-section:nth-of-type(3) li {

    margin:
        7px 0;

    padding-left:
        5px;
}


/* 04 — Dataset Investigation */
.research-section:nth-of-type(4) {

    border-left-color:
        #16764a;

    background:
        linear-gradient(
            135deg,
            rgba(
                237,
                249,
                243,
                0.78
            ),
            rgba(
                255,
                255,
                255,
                0.72
            )
        );
}


.research-section:nth-of-type(4) p {

    padding:
        14px 16px;

    margin:
        10px 0;

    border:
        1px solid
        rgba(
            22,
            118,
            74,
            0.14
        );

    border-radius:
        9px;

    background:
        rgba(
            255,
            255,
            255,
            0.62
        );
}


.research-section:nth-of-type(4) p strong {

    color:
        #16764a;

    font-weight:
        800;
}


/* 05 — T1–T11 Task Map */
.research-section:nth-of-type(5) {

    border-left-color:
        #2167e8;
}


.research-section:nth-of-type(5) h3 {

    margin-top:
        20px;

    margin-bottom:
        7px;

    padding:
        11px 14px;

    border:
        1px solid
        rgba(
            33,
            103,
            232,
            0.14
        );

    border-radius:
        8px;

    background:
        rgba(
            234,
            242,
            255,
            0.58
        );

    color:
        #174fb7;

    font-size:
        1rem;

    letter-spacing:
        -0.01em;
}


.research-section:nth-of-type(5) h3:first-of-type {

    margin-top:
        0;
}


/* 06 — Controlled Results */
.research-section:nth-of-type(6) {

    border-left-color:
        #16764a;

    background:
        linear-gradient(
            135deg,
            rgba(
                237,
                249,
                243,
                0.84
            ),
            rgba(
                255,
                255,
                255,
                0.72
            )
        );
}


.research-section:nth-of-type(6) h3 {

    padding:
        12px 16px;

    margin-top:
        20px;

    margin-bottom:
        8px;

    border:
        1px solid
        rgba(
            22,
            118,
            74,
            0.16
        );

    border-radius:
        8px;

    background:
        rgba(
            255,
            255,
            255,
            0.68
        );

    color:
        #16613f;

    font-size:
        1.05rem;
}


.research-section:nth-of-type(6) h3:first-of-type {

    margin-top:
        0;

    border:
        0;

    background:
        transparent;

    padding:
        0;

    color:
        #162033;

    font-size:
        1.65rem;
}


.research-section:nth-of-type(6) p {

    display:
        inline-block;

    width:
        calc(50% - 14px);

    box-sizing:
        border-box;

    margin:
        5px 10px 5px 0;

    padding:
        10px 13px;

    border:
        1px solid
        rgba(
            22,
            118,
            74,
            0.12
        );

    border-radius:
        7px;

    background:
        rgba(
            255,
            255,
            255,
            0.58
        );
}


.research-section:nth-of-type(6) p:nth-last-child(1) {

    margin-bottom:
        0;
}


/* 07 — Evidence Integration */
.research-section:nth-of-type(7) {

    border-left-color:
        #2167e8;
}


.research-section:nth-of-type(7) h3 {

    margin-top:
        18px;

    padding:
        11px 14px;

    border:
        1px solid
        rgba(
            33,
            103,
            232,
            0.14
        );

    border-radius:
        8px;

    background:
        rgba(
            234,
            242,
            255,
            0.52
        );

    color:
        #174fb7;

    font-size:
        1.02rem;
}


.research-section:nth-of-type(7) h3:first-of-type {

    margin-top:
        0;

    border:
        0;

    background:
        transparent;

    padding:
        0;

    color:
        #162033;

    font-size:
        1.65rem;
}


/* 08 — Limitations */
.research-section:nth-of-type(8) {

    border-left-color:
        #b66a00;

    background:
        linear-gradient(
            135deg,
            rgba(
                255,
                250,
                240,
                0.90
            ),
            rgba(
                255,
                255,
                255,
                0.72
            )
        );
}


.research-section:nth-of-type(8) h3 {

    color:
        #945300;
}


.research-limitations-list {

    margin:
        18px 0 0;

    padding:
        20px 24px 20px 46px;

    border:
        1px solid
        rgba(
            182,
            106,
            0,
            0.20
        );

    border-radius:
        10px;

    background:
        rgba(
            255,
            245,
            220,
            0.68
        );

    color:
        #5c421b;
}


.research-limitations-list li {

    margin:
        9px 0;

    line-height:
        1.55;
}


.research-limitations-list li::marker {

    color:
        #b66a00;
}


/* 09 — Conclusion */
.research-section:nth-of-type(9) {

    border-left-color:
        #16764a;

    background:
        linear-gradient(
            135deg,
            rgba(
                237,
                249,
                243,
                0.86
            ),
            rgba(
                255,
                255,
                255,
                0.74
            )
        );
}


.research-section:nth-of-type(9) h3 {

    color:
        #16613f;
}


/* ============================================================
   06 — RESEARCH FOOTER
   ============================================================ */

.research-overview-footer {

    display:
        flex;

    justify-content:
        center;

    align-items:
        center;

    padding:
        30px 0 8px;
}


.research-overview-footer::before {

    content:
        "RESEARCH / EVIDENCE-FIRST DECISION SUPPORT";

    display:
        block;

    margin-right:
        18px;

    color:
        #526176;

    font-size:
        0.67rem;

    font-weight:
        800;

    letter-spacing:
        0.12em;
}


/* ============================================================
   07 — RESEARCH SECTION RHYTHM
   ============================================================ */

.research-section + .research-section {

    margin-top:
        22px;
}


.research-section:first-of-type {

    margin-top:
        0;
}


.research-section:last-of-type {

    margin-bottom:
        0;
}


/* ============================================================
   08 — RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    body.app-view-research .research-overview {

        width:
            min(
                calc(100% - 32px),
                1240px
            );

        padding:
            40px 0 64px;
    }


    .research-overview-header {

        padding:
            34px 30px;
    }


    .research-section {

        padding:
            28px 28px 30px;
    }


    .research-section:nth-of-type(6) p {

        width:
            100%;

        margin:
            5px 0;
    }


    .research-overview-footer {

        flex-direction:
            column;

        gap:
            16px;
    }


    .research-overview-footer::before {

        margin-right:
            0;

        order:
            2;

        text-align:
            center;
    }


    #research-home-button-footer {

        order:
            1;
    }
}


@media (max-width: 620px) {

    body.app-view-research .research-overview {

        width:
            calc(100% - 24px);

        padding:
            26px 0 48px;
    }


    .research-overview-header {

        padding:
            30px 22px 26px;

        border-radius:
            14px;
    }


    .research-overview-header h2 {

        font-size:
            clamp(
                2rem,
                10vw,
                3rem
            );

        line-height:
            1.06;
    }


    .research-overview-header p {

        font-size:
            0.92rem;

        line-height:
            1.6;
    }


    .research-section {

        padding:
            24px 20px 26px;

        border-left-width:
            3px;

        border-radius:
            11px;
    }


    .research-section h3 {

        font-size:
            1.18rem;
    }


    .research-section p {

        font-size:
            0.92rem;

        line-height:
            1.65;
    }


    .research-section:nth-of-type(3) ol {

        padding:
            16px 18px 16px 36px;
    }


    .research-section:nth-of-type(4) p {

        padding:
            12px 13px;
    }


    .research-limitations-list {

        padding:
            16px 18px 16px 34px;
    }


    .research-home-button {

        width:
            100%;

        min-height:
            46px;
    }


    .research-overview-footer {

        padding-top:
            24px;
    }


    #research-home-button-footer {

        width:
            100%;
    }
}


/* ============================================================
   END DEPLOY-OP-069
   ============================================================ */
"""


def main():

    print("=" * 72)
    print(MARKER)
    print("=" * 72)

    # =========================================================
    # 1. SOURCE CONTRACT
    # =========================================================

    print("\n[1] SOURCE CONTRACT")
    print("-" * 72)

    for path in [
        STYLE,
        INDEX,
        APP,
    ]:

        if not path.exists():
            raise RuntimeError(
                f"BLOCKED: missing file: {path}"
            )

        print(f"FOUND: {path}")

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    index_before = INDEX.read_text(
        encoding="utf-8"
    )

    app_before = APP.read_text(
        encoding="utf-8"
    )

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-069 already exists."
        )

    required_index = [
        'id="research-overview"',
        'class="research-overview-inner"',
        'class="research-overview-header"',
        'class="research-section"',
        'class="research-section-label"',
        'class="research-home-button"',
    ]

    for marker in required_index:

        if marker not in index_before:
            raise RuntimeError(
                f"FAIL: required Research View marker "
                f"missing: {marker}"
            )

        print(
            f"{marker:42} FOUND"
        )

    # =========================================================
    # 2. HASHES BEFORE
    # =========================================================

    print("\n[2] SOURCE HASHES")
    print("-" * 72)

    hashes_before = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    for name, digest in hashes_before.items():
        print(
            f"{name:16} {digest}"
        )

    # =========================================================
    # 3. BACKUP
    # =========================================================

    print("\n[3] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        if sha256(BACKUP) != hashes_before["style.css"]:
            raise RuntimeError(
                "FAIL: existing OP-069 backup does not "
                "match current style.css."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            BACKUP
        )

        if sha256(BACKUP) != hashes_before["style.css"]:
            raise RuntimeError(
                "FAIL: OP-069 backup integrity mismatch."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 4. WRITE CSS
    # =========================================================

    print("\n[4] WRITING RESEARCH CSS")
    print("-" * 72)

    STYLE.write_text(
        style_before
        + "\n\n"
        + CSS_LAYER,
        encoding="utf-8"
    )

    print("style.css UPDATED")
    print("index.html UNTOUCHED")
    print("app.js UNTOUCHED")

    # =========================================================
    # 5. VALIDATION
    # =========================================================

    print("\n[5] VALIDATION")
    print("-" * 72)

    style_after = STYLE.read_text(
        encoding="utf-8"
    )

    index_after = INDEX.read_text(
        encoding="utf-8"
    )

    app_after = APP.read_text(
        encoding="utf-8"
    )

    checks = {

        "OP069_MARKER":
            style_after.count(MARKER) == 1,

        "RESEARCH_VIEW_STATE":
            "body.app-view-research"
            in style_after,

        "RESEARCH_OVERVIEW":
            ".research-overview"
            in style_after,

        "RESEARCH_HEADER":
            ".research-overview-header"
            in style_after,

        "RESEARCH_SECTION":
            ".research-section"
            in style_after,

        "RESEARCH_LABEL":
            ".research-section-label"
            in style_after,

        "RESEARCH_NAVIGATION":
            ".research-home-button"
            in style_after,

        "RESEARCH_FOOTER":
            ".research-overview-footer"
            in style_after,

        "GREEN_RESULT_ACCENT":
            "#16764a"
            in style_after,

        "AMBER_BOUNDARY_ACCENT":
            "#b66a00"
            in style_after,

        "BLUE_RESEARCH_ACCENT":
            "#2167e8"
            in style_after,

        "RESEARCH_RESPONSIVE":
            "@media (max-width: 620px)"
            in style_after
            and
            "body.app-view-research"
            in style_after,

        "INDEX_UNCHANGED":
            sha256(INDEX)
            == hashes_before["index.html"],

        "APP_UNCHANGED":
            sha256(APP)
            == hashes_before["app.js"],

        "RESEARCH_HTML_PRESERVED":
            'id="research-overview"'
            in index_after,

        "RESEARCH_JS_PRESERVED":
            "showResearchOverview"
            in app_after,

        "API_PRESERVED":
            "/tickets/analyze"
            in app_after
            and
            "/tickets/analyze-batch"
            in app_after,

        "NO_TICKET_PIPELINE_FRONTEND":
            "TicketPipeline"
            not in app_after,

        "NO_SKLEARN_FRONTEND":
            "sklearn"
            not in app_after.lower(),
    }

    for name, passed in checks.items():

        print(
            f"{name:42} "
            f"{'PASS' if passed else 'FAIL'}"
        )

    # =========================================================
    # 6. HASH / SAFETY
    # =========================================================

    print("\n[6] INTEGRITY")
    print("-" * 72)

    hashes_after = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    style_changed = (
        hashes_after["style.css"]
        != hashes_before["style.css"]
    )

    print(
        "STYLE.CSS CHANGED: "
        f"{'PASS' if style_changed else 'FAIL'}"
    )

    print(
        "INDEX.HTML UNCHANGED: "
        f"{'PASS' if hashes_after['index.html'] == hashes_before['index.html'] else 'FAIL'}"
    )

    print(
        "APP.JS UNCHANGED: "
        f"{'PASS' if hashes_after['app.js'] == hashes_before['app.js'] else 'FAIL'}"
    )

    if not all(checks.values()) or not style_changed:

        print(
            "\nVALIDATION FAILED — RESTORING style.css"
        )

        shutil.copy2(
            BACKUP,
            STYLE
        )

        print(
            "STYLE RESTORED FROM OP-069 BACKUP"
        )

        print("STATUS: FAIL")

        raise SystemExit(1)

    # =========================================================
    # 7. EVIDENCE
    # =========================================================

    evidence = {

        "operation":
            "DEPLOY-OP-069",

        "title":
            "Research View Visual System",

        "status":
            "PASS",

        "modified_files": [
            str(STYLE)
        ],

        "untouched_files": [
            str(INDEX),
            str(APP),
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

        "scope": [
            "Research View viewport",
            "Research View header",
            "Research section hierarchy",
            "blue research accents",
            "green result accents",
            "amber limitation accents",
            "Research navigation controls",
            "Research footer",
            "responsive Research View styling",
        ],

        "excluded": [
            "HTML changes",
            "JavaScript changes",
            "API changes",
            "backend changes",
            "frozen runtime changes",
            "model changes",
            "T1-T11 semantic changes",
        ],

        "hashes_before":
            hashes_before,

        "hashes_after":
            hashes_after,

        "checks":
            checks,
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True
    )

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
    print("DEPLOY-OP-069")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
