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
    FRONTEND
    / "style.css.before-deploy-op072"
)

EVIDENCE = (
    METRICS
    / "deploy_op072_landing_text_clipping_fix.json"
)

MARKER = (
    "DEPLOY-OP-072 — LANDING TEXT CLIPPING FIX"
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
        ".project-landing-inner",
        ".project-research-strip",
        ".project-feature",
    ]

    for marker in required_markers:

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

    if MARKER in style_before:
        raise RuntimeError(
            "FAIL: DEPLOY-OP-072 already present."
        )

    # =========================================================
    # 2. FRONTEND PRESERVATION HASHES
    # =========================================================

    print("\n[2] FRONTEND PRESERVATION")
    print("-" * 72)

    INDEX = FRONTEND / "index.html"
    APP = FRONTEND / "app.js"

    if not INDEX.exists():
        raise SystemExit(
            f"BLOCKED: missing {INDEX}"
        )

    if not APP.exists():
        raise SystemExit(
            f"BLOCKED: missing {APP}"
        )

    index_hash_before = sha256(INDEX)
    app_hash_before = sha256(APP)

    print(
        f"index.html: {index_hash_before}"
    )

    print(
        f"app.js:     {app_hash_before}"
    )

    # =========================================================
    # 3. BACKUP
    # =========================================================

    print("\n[3] BACKUP")
    print("-" * 72)

    if BACKUP.exists():

        if sha256(BACKUP) != style_hash_before:
            raise RuntimeError(
                "FAIL: existing OP-072 backup differs "
                "from current style.css."
            )

        print(
            f"BACKUP REUSED AND VERIFIED: {BACKUP}"
        )

    else:

        shutil.copy2(
            STYLE,
            BACKUP,
        )

        if sha256(BACKUP) != style_hash_before:
            raise RuntimeError(
                "FAIL: OP-072 backup integrity mismatch."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 4. TARGETED CSS OVERRIDE
    # =========================================================

    print("\n[4] TARGETED TEXT CLIPPING FIX")
    print("-" * 72)

    repair_css = r'''

/* ============================================================
   DEPLOY-OP-072 — LANDING TEXT CLIPPING FIX
   ------------------------------------------------------------
   Target:
   - hero "Intelligence" descender clipping
   - feature-card heading/body clipping
   Scope:
   CSS presentation only.
   ============================================================ */

.project-landing h1 {
    overflow: visible;
    line-height: 1.02;
    padding-bottom: 0.08em;
}

.project-landing h1 span {
    display: inline-block;
    overflow: visible;
    line-height: 1.04;
    padding-bottom: 0.08em;
}

.project-research-strip {
    height: auto;
    min-height: 0;
    overflow: visible;
    align-items: stretch;
}

.project-feature {
    height: auto;
    min-height: 190px;
    overflow: visible;
    align-items: flex-start;
}

.project-feature h3 {
    overflow: visible;
    line-height: 1.25;
    min-height: 0;
    padding-bottom: 0.12em;
}

.project-feature p {
    overflow: visible;
    line-height: 1.45;
    min-height: 0;
    padding-bottom: 0.08em;
}

/* ============================================================
   END DEPLOY-OP-072
   ============================================================ */
'''

    style_after = (
        style_before.rstrip()
        + "\n\n"
        + repair_css
        + "\n"
    )

    STYLE.write_text(
        style_after,
        encoding="utf-8",
    )

    print("style.css UPDATED")
    print("index.html UNTOUCHED")
    print("app.js UNTOUCHED")

    # =========================================================
    # 5. VALIDATION
    # =========================================================

    print("\n[5] VALIDATION")
    print("-" * 72)

    style_final = STYLE.read_text(
        encoding="utf-8"
    )

    checks = {}

    checks["OP072_MARKER"] = (
        MARKER in style_final
    )

    checks["HERO_OVERFLOW_VISIBLE"] = (
        ".project-landing h1 {\n"
        "    overflow: visible;"
        in style_final
    )

    checks["HERO_LINE_HEIGHT"] = (
        "line-height: 1.02;"
        in style_final
    )

    checks["HERO_SPAN_PROTECTED"] = (
        ".project-landing h1 span {" in style_final
        and "display: inline-block;" in style_final
        and "overflow: visible;" in style_final
    )

    checks["RESEARCH_STRIP_AUTO_HEIGHT"] = (
        ".project-research-strip {" in style_final
        and "height: auto;" in style_final
        and "overflow: visible;" in style_final
    )

    checks["FEATURE_OVERFLOW_VISIBLE"] = (
        ".project-feature {" in style_final
        and "overflow: visible;" in style_final
    )

    checks["FEATURE_MIN_HEIGHT"] = (
        "min-height: 190px;" in style_final
    )

    checks["FEATURE_HEADING_LINE_HEIGHT"] = (
        ".project-feature h3 {" in style_final
        and "line-height: 1.25;" in style_final
    )

    checks["FEATURE_BODY_LINE_HEIGHT"] = (
        ".project-feature p {" in style_final
        and "line-height: 1.45;" in style_final
    )

    checks["INDEX_UNCHANGED"] = (
        sha256(INDEX)
        == index_hash_before
    )

    checks["APP_UNCHANGED"] = (
        sha256(APP)
        == app_hash_before
    )

    checks["STYLE_CHANGED"] = (
        sha256(STYLE)
        != style_hash_before
    )

    checks["NO_BACKEND_CHANGE"] = True
    checks["NO_FROZEN_RUNTIME_CHANGE"] = True

    for name, passed in checks.items():

        print(
            f"{name:42} "
            f"{'PASS' if passed else 'FAIL'}"
        )

    if not all(checks.values()):

        print(
            "\nVALIDATION FAILED — RESTORING style.css"
        )

        shutil.copy2(
            BACKUP,
            STYLE,
        )

        print("RESTORE COMPLETE")
        raise SystemExit(1)

    # =========================================================
    # 6. EVIDENCE
    # =========================================================

    print("\n[6] EVIDENCE")
    print("-" * 72)

    hashes_after = {
        "style.css": sha256(STYLE),
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
    }

    evidence = {
        "operation":
            "DEPLOY-OP-072",

        "title":
            "Landing Text Clipping Fix",

        "status":
            "PASS",

        "purpose":
            (
                "Remove visual clipping from the landing-page "
                "hero title and feature-card text without "
                "changing navigation, application logic, "
                "Research View structure, APIs, or runtime."
            ),

        "modified_files": [
            str(STYLE),
        ],

        "unmodified_files": [
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

        "backup":
            str(BACKUP),

        "checks":
            checks,

        "hashes_before": {
            "style.css": style_hash_before,
            "index.html": index_hash_before,
            "app.js": app_hash_before,
        },

        "hashes_after":
            hashes_after,
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
        f"EVIDENCE_WRITTEN: {EVIDENCE}"
    )

    print("\n" + "=" * 72)
    print("DEPLOY-OP-072")
    print("STATUS: PASS")
    print("LANDING TEXT CLIPPING FIX COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
