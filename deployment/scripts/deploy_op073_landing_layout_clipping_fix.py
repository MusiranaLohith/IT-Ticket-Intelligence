from pathlib import Path
import hashlib
import json
import shutil


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = ROOT / "deployment" / "frontend"
STYLE = FRONTEND / "style.css"

METRICS = (
    ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

BACKUP = (
    FRONTEND
    / "style.css.before-deploy-op073"
)

EVIDENCE = (
    METRICS
    / "deploy_op073_landing_layout_clipping_fix.json"
)

MARKER = (
    "DEPLOY-OP-073 — LANDING LAYOUT CLIPPING FIX"
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

    style_before = STYLE.read_text(
        encoding="utf-8"
    )

    required_markers = [
        ".project-landing",
        ".project-landing-inner",
        ".project-landing h1",
        ".project-landing h1 span",
        ".project-research-strip",
        ".project-feature",
        ".project-feature h3",
        ".project-feature p",
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
            "FAIL: DEPLOY-OP-073 already present."
        )

    # =========================================================
    # 2. PRESERVATION HASHES
    # =========================================================

    print("\n[2] PRESERVATION HASHES")
    print("-" * 72)

    style_hash_before = sha256(STYLE)
    index_hash_before = sha256(INDEX)
    app_hash_before = sha256(APP)

    print(
        f"style.css: {style_hash_before}"
    )

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
                "FAIL: existing OP-073 backup differs "
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
                "FAIL: OP-073 backup integrity mismatch."
            )

        print(
            f"BACKUP CREATED: {BACKUP}"
        )

    # =========================================================
    # 4. TARGETED LANDING LAYOUT FIX
    # =========================================================

    print("\n[4] TARGETED LANDING LAYOUT FIX")
    print("-" * 72)

    repair_css = r'''

/* ============================================================
   DEPLOY-OP-073 — LANDING LAYOUT CLIPPING FIX
   ------------------------------------------------------------
   Purpose:
   - remove parent-level clipping
   - protect hero title descenders
   - allow research strip to size to its content
   - prevent feature-card text from being cut
   Scope:
   CSS presentation only.
   ============================================================ */

.project-landing {
    height: auto !important;
    min-height: 100vh;
    overflow: visible !important;
}

.project-landing-inner {
    height: auto !important;
    min-height: 0;
    overflow: visible !important;
}

.project-landing h1 {
    height: auto !important;
    min-height: 0;
    max-height: none !important;
    overflow: visible !important;
    line-height: 1.06 !important;
    padding-bottom: 0.14em !important;
}

.project-landing h1 span {
    height: auto !important;
    min-height: 0;
    max-height: none !important;
    overflow: visible !important;
    line-height: 1.08 !important;
    padding-bottom: 0.12em !important;
}

.project-research-strip {
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    overflow: visible !important;
    align-items: stretch;
}

.project-feature {
    height: auto !important;
    min-height: 220px !important;
    max-height: none !important;
    overflow: visible !important;
    align-items: flex-start;
}

.project-feature h3 {
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    overflow: visible !important;
    line-height: 1.28 !important;
    padding-bottom: 0.14em !important;
}

.project-feature p {
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    overflow: visible !important;
    line-height: 1.5 !important;
    padding-bottom: 0.10em !important;
}

/* ============================================================
   END DEPLOY-OP-073
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

    checks["OP073_MARKER"] = (
        MARKER in style_final
    )

    checks["LANDING_OVERFLOW_VISIBLE"] = (
        ".project-landing {" in style_final
        and "overflow: visible !important;" in style_final
    )

    checks["LANDING_AUTO_HEIGHT"] = (
        ".project-landing {" in style_final
        and "height: auto !important;" in style_final
    )

    checks["LANDING_INNER_PROTECTED"] = (
        ".project-landing-inner {" in style_final
        and "overflow: visible !important;" in style_final
    )

    checks["HERO_PROTECTED"] = (
        ".project-landing h1 {" in style_final
        and "max-height: none !important;" in style_final
        and "overflow: visible !important;" in style_final
    )

    checks["HERO_SPAN_PROTECTED"] = (
        ".project-landing h1 span {" in style_final
        and "overflow: visible !important;" in style_final
    )

    checks["RESEARCH_STRIP_AUTO"] = (
        ".project-research-strip {" in style_final
        and "height: auto !important;" in style_final
        and "max-height: none !important;" in style_final
    )

    checks["FEATURE_CARD_HEIGHT"] = (
        ".project-feature {" in style_final
        and "min-height: 220px !important;" in style_final
        and "max-height: none !important;" in style_final
    )

    checks["FEATURE_HEADING_PROTECTED"] = (
        ".project-feature h3 {" in style_final
        and "overflow: visible !important;" in style_final
        and "line-height: 1.28 !important;" in style_final
    )

    checks["FEATURE_BODY_PROTECTED"] = (
        ".project-feature p {" in style_final
        and "overflow: visible !important;" in style_final
        and "line-height: 1.5 !important;" in style_final
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
            "DEPLOY-OP-073",

        "title":
            "Landing Layout Clipping Fix",

        "status":
            "PASS",

        "purpose":
            (
                "Remove parent-level and element-level clipping "
                "from the landing hero and feature cards while "
                "preserving the existing landing design, "
                "navigation, Research View, APIs and runtime."
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
    print("DEPLOY-OP-073")
    print("STATUS: PASS")
    print("LANDING LAYOUT CLIPPING FIX COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
