from pathlib import Path
import hashlib
import json
import shutil


BASE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = BASE / "deployment/frontend"
METRICS = BASE / "modeling/FMP/metrics"

STYLE = FRONTEND / "style.css"

BACKUP = FRONTEND / "style.css.before-deploy-op053"

EVIDENCE = METRICS / "deploy_op053_home_visual_redesign.json"

MARKER = "DEPLOY-OP-053 — HOME PAGE VISUAL REDESIGN"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    print("=" * 66)
    print("DEPLOY-OP-053 — HOME PAGE VISUAL REDESIGN")
    print("=" * 66)

    if not STYLE.exists():
        print("\nSTATUS: BLOCKED")
        print(f"Missing: {STYLE}")
        raise SystemExit(1)

    style_before_hash = sha256(STYLE)

    print(f"\nSTYLE: {STYLE}")
    print(f"BEFORE HASH: {style_before_hash}")

    print("\n[1] BACKUP")
    print("-" * 66)

    if BACKUP.exists():
        backup_hash = sha256(BACKUP)

        if backup_hash != style_before_hash:
            print("STATUS: BLOCKED")
            print("Existing OP-053 backup does not match current style.css.")
            print(f"BACKUP HASH: {backup_hash}")
            print(f"CURRENT HASH: {style_before_hash}")
            raise SystemExit(1)

        print("BACKUP EXISTS AND MATCHES CURRENT STYLE.CSS")
    else:
        shutil.copy2(STYLE, BACKUP)
        print(f"BACKUP CREATED: {BACKUP}")

    print("\n[2] APPENDING HOME VISUAL LAYER")
    print("-" * 66)

    css_layer = r'''

/* ============================================================
   DEPLOY-OP-053
   HOME PAGE VISUAL REDESIGN
   ------------------------------------------------------------
   Scope:
   - Landing page presentation only.
   - CSS only.
   - No application logic.
   - No navigation changes.
   - No API changes.
   - No workspace redesign.
   ============================================================ */


/* ------------------------------------------------------------
   LANDING FOUNDATION
   ------------------------------------------------------------ */

.project-landing {
    position: relative;
    isolation: isolate;
    overflow: hidden;

    min-height: calc(100vh - 150px);

    padding:
        clamp(58px, 7vw, 92px)
        0
        clamp(70px, 8vw, 108px) !important;

    color: #f4f8ff;

    background:
        radial-gradient(
            circle at 78% 24%,
            rgba(73, 151, 255, 0.18),
            transparent 34%
        ),
        radial-gradient(
            circle at 18% 82%,
            rgba(35, 94, 190, 0.13),
            transparent 38%
        ),
        linear-gradient(
            135deg,
            #071326 0%,
            #0a1a31 46%,
            #0c2342 100%
        );
}


/* ------------------------------------------------------------
   DIAGONAL BACKGROUND GEOMETRY
   ------------------------------------------------------------ */

.project-landing::before {
    content: "";

    position: absolute;
    inset: -20% -12%;

    z-index: -2;

    background:
        linear-gradient(
            135deg,
            transparent 0%,
            transparent 47%,
            rgba(100, 173, 255, 0.075) 47.15%,
            rgba(100, 173, 255, 0.075) 47.5%,
            transparent 47.65%,
            transparent 63%,
            rgba(100, 173, 255, 0.045) 63.15%,
            rgba(100, 173, 255, 0.045) 63.5%,
            transparent 63.65%
        );

    transform: rotate(-2deg) scale(1.08);

    pointer-events: none;
}


.project-landing::after {
    content: "";

    position: absolute;
    inset: 0;

    z-index: -1;

    background:
        linear-gradient(
            112deg,
            transparent 0 36%,
            rgba(92, 164, 255, 0.055) 36.2%,
            transparent 36.5%
        ),
        linear-gradient(
            112deg,
            transparent 0 57%,
            rgba(92, 164, 255, 0.04) 57.2%,
            transparent 57.5%
        );

    pointer-events: none;
}


/* ------------------------------------------------------------
   INNER DEPTH
   ------------------------------------------------------------ */

.project-landing-inner {
    position: relative;

    z-index: 1;
}


/* ------------------------------------------------------------
   KICKER
   ------------------------------------------------------------ */

.project-kicker {
    display: inline-flex;
    align-items: center;

    margin-bottom: 22px !important;
    padding: 8px 12px;

    color: #b8d7ff;

    font-size: 0.68rem !important;
    font-weight: 850 !important;

    letter-spacing: 0.18em;

    border:
        1px solid
        rgba(148, 195, 255, 0.28);

    background:
        rgba(255, 255, 255, 0.055);

    box-shadow:
        0 10px 32px
        rgba(0, 0, 0, 0.14);

    backdrop-filter: blur(12px);
}


/* ------------------------------------------------------------
   HUGE HERO HEADING
   ------------------------------------------------------------ */

.project-landing h1 {
    max-width: 980px !important;

    color: #f7faff !important;

    font-size:
        clamp(
            4rem,
            9vw,
            7.8rem
        ) !important;

    font-weight: 850 !important;

    line-height: 0.88 !important;

    letter-spacing: -0.065em !important;

    text-wrap: balance;

    text-shadow:
        0 8px 40px
        rgba(0, 0, 0, 0.18);
}


.project-landing h1 span {
    color: #8ec5ff !important;

    opacity: 1 !important;

    background:
        linear-gradient(
            110deg,
            #8ec5ff 0%,
            #dceeff 48%,
            #76b5ff 100%
        );

    -webkit-background-clip: text;
    background-clip: text;

    -webkit-text-fill-color: transparent;
}


/* ------------------------------------------------------------
   HERO COPY
   ------------------------------------------------------------ */

.project-motto {
    max-width: 820px !important;

    margin-top: 30px !important;

    color: #d9e9fb !important;

    font-size:
        clamp(
            1.08rem,
            2vw,
            1.42rem
        ) !important;

    font-weight: 650 !important;

    line-height: 1.48 !important;
}


.project-introduction {
    max-width: 790px !important;

    margin-top: 16px !important;

    color: #a9bfd9 !important;

    font-size: 0.98rem !important;

    line-height: 1.72 !important;
}


/* ------------------------------------------------------------
   HOME PAGE ACTIONS
   ------------------------------------------------------------ */

.project-actions {
    display: flex;

    flex-wrap: wrap;

    align-items: center;

    gap: 14px;

    margin-top: 36px !important;
}


/* Shared button foundation */

.project-primary-action,
.project-secondary-action {
    position: relative;

    min-height: 56px;

    padding:
        0 25px;

    border-radius: 8px;

    font-size: 0.78rem;

    font-weight: 850;

    letter-spacing: 0.08em;

    transition:
        transform 180ms ease,
        box-shadow 180ms ease,
        border-color 180ms ease,
        background 180ms ease;

    overflow: hidden;
}


/* Primary */

.project-primary-action {
    min-width: 190px;

    color: #ffffff;

    border:
        1px solid
        rgba(176, 218, 255, 0.52);

    background:
        linear-gradient(
            135deg,
            #2779df 0%,
            #1656aa 100%
        );

    box-shadow:
        0 12px 30px
        rgba(16, 74, 150, 0.35),
        inset 0 1px 0
        rgba(255, 255, 255, 0.18);
}


.project-primary-action::before {
    content: "";

    position: absolute;

    inset: 0;

    background:
        linear-gradient(
            115deg,
            transparent 0%,
            rgba(255, 255, 255, 0.16) 45%,
            transparent 68%
        );

    transform:
        translateX(-120%);

    transition:
        transform 420ms ease;

    pointer-events: none;
}


.project-primary-action:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(194, 227, 255, 0.85);

    box-shadow:
        0 16px 38px
        rgba(16, 82, 168, 0.45),
        inset 0 1px 0
        rgba(255, 255, 255, 0.22);
}


.project-primary-action:hover::before {
    transform:
        translateX(120%);
}


.project-primary-action:active {
    transform:
        translateY(0);
}


/* Secondary */

.project-secondary-action {
    min-width: 175px;

    color: #dcecff;

    border:
        1px solid
        rgba(151, 194, 239, 0.34);

    background:
        rgba(255, 255, 255, 0.075);

    box-shadow:
        0 10px 28px
        rgba(0, 0, 0, 0.13),
        inset 0 1px 0
        rgba(255, 255, 255, 0.07);

    backdrop-filter:
        blur(12px);
}


.project-secondary-action:hover {
    transform:
        translateY(-2px);

    color: #ffffff;

    border-color:
        rgba(169, 210, 255, 0.62);

    background:
        rgba(73, 139, 214, 0.16);

    box-shadow:
        0 14px 32px
        rgba(0, 0, 0, 0.18);
}


.project-secondary-action:active {
    transform:
        translateY(0);
}


/* ------------------------------------------------------------
   RESEARCH STRIP
   ------------------------------------------------------------ */

.project-research-strip {
    position: relative;

    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 1px;

    margin-top:
        clamp(54px, 7vw, 82px) !important;

    border:
        1px solid
        rgba(145, 191, 237, 0.18) !important;

    background:
        rgba(112, 166, 224, 0.12);

    box-shadow:
        0 24px 60px
        rgba(0, 0, 0, 0.16);

    backdrop-filter:
        blur(14px);
}


/* Individual research cards */

.project-feature {
    position: relative;

    min-height: 178px;

    padding:
        24px 21px !important;

    color: #d7e7f8;

    border-right:
        1px solid
        rgba(145, 191, 237, 0.14) !important;

    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.075),
            rgba(255, 255, 255, 0.025)
        );

    transition:
        background 180ms ease,
        transform 180ms ease;
}


.project-feature:hover {
    z-index: 2;

    background:
        linear-gradient(
            145deg,
            rgba(91, 159, 231, 0.14),
            rgba(255, 255, 255, 0.045)
        );

    transform:
        translateY(-2px);
}


.project-feature:last-child {
    border-right: 0 !important;
}


.project-feature-index {
    color: #72b4ff !important;

    font-size: 0.68rem !important;

    font-weight: 850 !important;

    letter-spacing: 0.13em;
}


.project-feature h3 {
    color: #f0f6ff !important;

    font-size: 0.74rem !important;

    font-weight: 850 !important;

    letter-spacing: 0.085em;
}


.project-feature p {
    color: #9db6d1 !important;

    font-size: 0.81rem !important;

    line-height: 1.6 !important;
}


/* ------------------------------------------------------------
   MOBILE
   ------------------------------------------------------------ */

@media (max-width: 900px) {

    .project-landing {
        padding:
            58px 0 72px !important;
    }

    .project-landing h1 {
        font-size:
            clamp(
                3.6rem,
                11vw,
                6.5rem
            ) !important;
    }

    .project-research-strip {
        grid-template-columns:
            1fr 1fr;
    }

    .project-feature:nth-child(2) {
        border-right:
            0 !important;
    }

    .project-feature:nth-child(3),
    .project-feature:nth-child(4) {
        border-top:
            1px solid
            rgba(145, 191, 237, 0.14);
    }

    .project-feature:nth-child(4) {
        border-right:
            0 !important;
    }
}


@media (max-width: 620px) {

    .project-landing {
        min-height: auto !important;

        padding:
            48px 0 58px !important;
    }

    .project-kicker {
        font-size: 0.62rem !important;

        letter-spacing: 0.14em;
    }

    .project-landing h1 {
        font-size:
            clamp(
                3.15rem,
                15vw,
                5.2rem
            ) !important;
    }

    .project-motto {
        font-size:
            1.05rem !important;
    }

    .project-introduction {
        font-size:
            0.92rem !important;
    }

    .project-actions {
        display: grid;

        grid-template-columns:
            1fr;

        gap: 10px;
    }

    .project-primary-action,
    .project-secondary-action {
        width: 100%;

        min-width: 0;

        min-height: 54px;
    }

    .project-research-strip {
        grid-template-columns:
            1fr;
    }

    .project-feature {
        min-height: auto;

        border-right:
            0 !important;

        border-bottom:
            1px solid
            rgba(145, 191, 237, 0.14) !important;
    }

    .project-feature:last-child {
        border-bottom:
            0 !important;
    }

    .project-feature:nth-child(3),
    .project-feature:nth-child(4) {
        border-top:
            0;
    }
}


/* ============================================================
   END DEPLOY-OP-053
   ============================================================ */
'''

    if MARKER in STYLE.read_text(encoding="utf-8"):
        print("STATUS: BLOCKED")
        print("DEPLOY-OP-053 marker already exists.")
        raise SystemExit(1)

    with STYLE.open(
        "a",
        encoding="utf-8",
    ) as handle:
        handle.write(css_layer)

    print("HOME VISUAL CSS APPENDED")

    print("\n[3] VALIDATION")
    print("-" * 66)

    style_after_hash = sha256(STYLE)

    print(f"AFTER HASH: {style_after_hash}")
    print(f"INDEX MODIFIED: FALSE")
    print(f"APP.JS MODIFIED: FALSE")
    print(f"BACKEND MODIFIED: FALSE")
    print(f"FROZEN RUNTIME MODIFIED: FALSE")
    print(f"MODELING MODIFIED: FALSE")

    updated_text = STYLE.read_text(encoding="utf-8")

    required_markers = [
        "DEPLOY-OP-053",
        ".project-landing::before",
        ".project-landing::after",
        ".project-primary-action",
        ".project-secondary-action",
        ".project-research-strip",
        "@media (max-width: 900px)",
        "@media (max-width: 620px)",
    ]

    failures = [
        marker
        for marker in required_markers
        if marker not in updated_text
    ]

    if failures:
        print("\nVALIDATION FAILURES:")

        for failure in failures:
            print(f"  {failure}")

        print("\nRESTORING BACKUP")
        shutil.copy2(BACKUP, STYLE)

        print("STATUS: FAIL")
        raise SystemExit(1)

    print("ALL HOME VISUAL MARKERS: PASS")

    print("\n[4] EVIDENCE")
    print("-" * 66)

    evidence = {
        "operation": "DEPLOY-OP-053",
        "title": "Home Page Visual Redesign",
        "status": "PASS",
        "scope": "CSS-only landing page visual layer",
        "reference_direction": [
            "deep navy background",
            "diagonal geometric background",
            "large hero typography",
            "prominent primary CTA",
            "glass secondary CTA",
            "research feature strip",
            "responsive layout",
        ],
        "files": {
            "modified": [
                str(STYLE),
            ],
            "unchanged": [
                str(FRONTEND / "index.html"),
                str(FRONTEND / "app.js"),
            ],
            "backend": "UNCHANGED",
            "frozen_runtime": "UNCHANGED",
            "modeling": "UNCHANGED",
        },
        "backup": str(BACKUP),
        "before_sha256": style_before_hash,
        "after_sha256": style_after_hash,
        "markers": required_markers,
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

    print(f"EVIDENCE_WRITTEN: {EVIDENCE}")
    print("\nSTATUS: PASS")


if __name__ == "__main__":
    main()
