from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

STYLE = (
    ROOT
    / "deployment/frontend/style.css"
)

BACKUP = (
    ROOT
    / "deployment/frontend/style.css.before-deploy-op065"
)

METRICS = (
    ROOT
    / "modeling/FMP/metrics/"
    "deploy_op065_landing_hero_polish.json"
)

MARKER = (
    "DEPLOY-OP-065 — LANDING HERO + "
    "RESEARCH STRIP POLISH"
)


CSS_LAYER = r'''

/* ============================================================
   DEPLOY-OP-065 — LANDING HERO + RESEARCH STRIP POLISH
   ============================================================ */

/*
 * LANDING HERO
 *
 * The hero heading is intentionally large.
 * Prevent the second line ("Intelligence") from being
 * visually clipped by line-box height or overflow rules.
 */

.project-landing,
.project-landing-inner {

    overflow:
        visible !important;
}


.project-landing h1 {

    line-height:
        0.94 !important;

    padding-bottom:
        0.10em !important;

    overflow:
        visible !important;

    display:
        block !important;
}


/*
 * RESEARCH STRIP
 *
 * Keep the glass/translucent character while giving
 * the four research blocks a clearer outer boundary.
 */

.project-research-strip {

    border:
        2px solid
        rgba(
            255,
            255,
            255,
            0.46
        ) !important;

    box-shadow:

        0 14px 34px
        rgba(
            31,
            78,
            121,
            0.09
        ),

        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.34
        ) !important;
}


/*
 * Keep the internal research divisions visible without
 * making the panel look heavy.
 */

.project-research-strip > * {

    border-color:
        rgba(
            74,
            126,
            181,
            0.22
        ) !important;
}


/*
 * Responsive safety.
 */

@media (max-width: 620px) {

    .project-landing h1 {

        line-height:
            0.96 !important;

        padding-bottom:
            0.12em !important;
    }

    .project-research-strip {

        border-width:
            2px !important;
    }
}


/* ============================================================
   END DEPLOY-OP-065
   ============================================================ */
'''


def sha256(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as handle:

        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def normalise(text: str) -> str:

    return " ".join(text.split())


def main():

    print("=" * 72)
    print(
        "DEPLOY-OP-065 — LANDING HERO + "
        "RESEARCH STRIP POLISH"
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

    required_history = [
        "DEPLOY-OP-057",
        "DEPLOY-OP-058",
        "DEPLOY-OP-059",
        "DEPLOY-OP-060",
        "DEPLOY-OP-061",
        "DEPLOY-OP-064",
    ]

    for marker in required_history:

        found = marker in style_before

        print(
            f"{marker:40}: "
            f"{'FOUND' if found else 'MISSING'}"
        )

        if not found:

            raise RuntimeError(
                f"FAIL: required previous operation "
                f"marker missing: {marker}"
            )

    required_selectors = [
        ".project-landing",
        ".project-landing-inner",
        ".project-landing h1",
        ".project-research-strip",
    ]

    for selector in required_selectors:

        found = selector in style_before

        print(
            f"{selector:40}: "
            f"{'FOUND' if found else 'MISSING'}"
        )

        if not found:

            raise RuntimeError(
                f"FAIL: required existing CSS "
                f"selector missing: {selector}"
            )

    if MARKER in style_before:

        raise RuntimeError(
            "FAIL: DEPLOY-OP-065 marker already exists. "
            "Refusing duplicate application."
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
                "FAIL: existing OP-065 backup does not "
                "match current style.css. Refusing overwrite."
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
                "FAIL: backup integrity verification failed."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 3. WRITE
    # =========================================================

    print("\n[3] LANDING HERO + RESEARCH STRIP POLISH")
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

    compact = normalise(style_after)

    checks = {

        "OP065_MARKER":
            style_after.count(MARKER) == 1,

        "LANDING_OVERFLOW_SAFE":
            ".project-landing" in style_after
            and "overflow:" in style_after
            and "visible !important" in style_after,

        "LANDING_INNER_OVERFLOW_SAFE":
            ".project-landing-inner" in style_after,

        "HERO_LINE_HEIGHT":
            "line-height: 0.94 !important;" in compact,

        "HERO_PADDING":
            "padding-bottom: 0.10em !important;" in compact,

        "HERO_OVERFLOW":
            ".project-landing h1" in style_after
            and "overflow:" in style_after,

        "RESEARCH_STRIP_BORDER":
            ".project-research-strip" in style_after
            and "2px solid" in style_after,

        "RESEARCH_STRIP_TRANSPARENCY":
            "255, 255, 255, 0.46"
            in compact,

        "RESEARCH_STRIP_DEPTH":
            "0 14px 34px" in compact,

        "RESEARCH_INTERNAL_DIVIDERS":
            ".project-research-strip > *" in style_after,

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

        "OP064_PRESERVED":
            "DEPLOY-OP-064" in style_after,
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
    # 5. INTEGRITY
    # =========================================================

    style_hash_after = sha256(STYLE)

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
            "DEPLOY-OP-065",

        "title":
            "Landing Hero + Research Strip Polish",

        "status":
            "PASS",

        "scope": [

            "hero heading clipping prevention",

            "landing hero overflow safety",

            "research strip stronger boundary",

            "research strip translucent border",

            "research strip depth",

            "research strip internal dividers",

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
    print("DEPLOY-OP-065")
    print("STATUS: PASS")
    print("=" * 72)


if __name__ == "__main__":
    main()
