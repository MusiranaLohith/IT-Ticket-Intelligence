from pathlib import Path
import hashlib
import json
import re


BASE = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

FRONTEND = BASE / "deployment/frontend"
METRICS = BASE / "modeling/FMP/metrics"

INDEX = FRONTEND / "index.html"
APP = FRONTEND / "app.js"
STYLE = FRONTEND / "style.css"

EVIDENCE = METRICS / "deploy_op052_home_visual_audit.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains(text, pattern):
    return re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL,
    ) is not None


def main():
    print("=" * 62)
    print("DEPLOY-OP-052 — HOME PAGE VISUAL AUDIT")
    print("=" * 62)

    print(f"\nFRONTEND: {FRONTEND}")

    required_files = [INDEX, APP, STYLE]

    missing = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    if missing:
        print("\nSTATUS: BLOCKED")
        print("Missing required files:")
        for path in missing:
            print(f"  {path}")
        raise SystemExit(1)

    index_text = INDEX.read_text(encoding="utf-8")
    app_text = APP.read_text(encoding="utf-8")
    style_text = STYLE.read_text(encoding="utf-8")

    results = {}

    print("\n[1] HOME PAGE STRUCTURE")
    print("-" * 62)

    html_checks = {
        "PROJECT_LANDING":
            r'id=["\']project-landing["\']',

        "ENTER_SYSTEM_BUTTON":
            r'id=["\']enter-system-button["\']',

        "VIEW_RESEARCH_BUTTON":
            r'id=["\']view-research-button["\']',

        "FEATURE_STRIP":
            r'class=["\'][^"\']*(?:feature|information)[^"\']*["\']',
    }

    for name, pattern in html_checks.items():
        found = contains(index_text, pattern)
        results[name] = found

        print(
            f"{name:<32}"
            f"{'FOUND' if found else 'MISSING'}"
        )

    print("\n[2] HOME PAGE TEXT")
    print("-" * 62)

    text_checks = {
        "SYSTEM_TITLE":
            "IT Ticket Intelligence",

        "EVIDENCE_FIRST_TAGLINE":
            "Evidence-first ticket triage and human decision support",

        "ENTER_SYSTEM_TEXT":
            "ENTER SYSTEM",

        "VIEW_RESEARCH_TEXT":
            "VIEW RESEARCH",

        "DATASET_INVESTIGATION":
            "DATASET INVESTIGATION",

        "T1_T11_EVIDENCE_CHAIN":
            "T1–T11 EVIDENCE CHAIN",

        "HUMAN_DECISION_BOUNDARY":
            "HUMAN DECISION BOUNDARY",

        "DEPLOYMENT_INTEGRITY":
            "DEPLOYMENT INTEGRITY",
    }

    for name, value in text_checks.items():
        found = value.lower() in index_text.lower()
        results[name] = found

        print(
            f"{name:<32}"
            f"{'FOUND' if found else 'MISSING'}"
        )

    print("\n[3] NAVIGATION IN APP.JS")
    print("-" * 62)

    navigation_checks = {
        "ENTER_SYSTEM_HANDLER":
            r'getElementById\(["\']enter-system-button["\']\)',

        "VIEW_RESEARCH_HANDLER":
            r'getElementById\(["\']view-research-button["\']\)',

        "SHOW_WORKSPACE_HOME":
            r'showWorkspaceHome',

        "SHOW_PROJECT_LANDING":
            r'showProjectLanding',
    }

    for name, pattern in navigation_checks.items():
        found = contains(app_text, pattern)
        results[name] = found

        print(
            f"{name:<32}"
            f"{'FOUND' if found else 'MISSING'}"
        )

    print("\n[4] CURRENT LANDING CSS")
    print("-" * 62)

    css_checks = {
        "LANDING_CONTAINER":
            r'\.project-landing\b',

        "PRIMARY_ACTION":
            r'\.project-primary-action\b',

        "SECONDARY_ACTION":
            r'\.project-secondary-action\b',

        "LANDING_FEATURES":
            r'\.project-(?:feature|information)',

        "LANDING_RESPONSIVE":
            r'@media[^{]*\([^)]*(?:max-width|min-width)',
    }

    for name, pattern in css_checks.items():
        found = contains(style_text, pattern)
        results[name] = found

        print(
            f"{name:<32}"
            f"{'FOUND' if found else 'MISSING'}"
        )

    print("\n[5] CURRENT BUTTON CSS BLOCKS")
    print("-" * 62)

    for selector in [
        ".project-primary-action",
        ".project-secondary-action",
    ]:
        match = re.search(
            re.escape(selector) + r"\s*\{(.*?)\}",
            style_text,
            re.IGNORECASE | re.DOTALL,
        )

        print(f"\n{selector}")

        if match:
            print(match.group(0)[:2500])
        else:
            print("NOT FOUND")

    print("\n[6] LANDING HTML CONTEXT")
    print("-" * 62)

    landing_match = re.search(
        r'<section[^>]+id=["\']project-landing["\'][^>]*>'
        r'.*?</section>',
        index_text,
        re.IGNORECASE | re.DOTALL,
    )

    if landing_match:
        print(landing_match.group(0)[:9000])
        results["LANDING_SECTION_EXTRACTED"] = True
    else:
        print("Landing section could not be extracted.")
        results["LANDING_SECTION_EXTRACTED"] = False

    print("\n[7] FRONTEND SAFETY CHECK")
    print("-" * 62)

    forbidden_frontend_patterns = {
        "TICKET_PIPELINE_REFERENCE":
            r'TicketPipeline',

        "SKLEARN_REFERENCE":
            r'sklearn',

        "PREDICT_BATCH_REFERENCE":
            r'predict_batch\s*\(',
    }

    frontend_source = index_text + "\n" + app_text

    for name, pattern in forbidden_frontend_patterns.items():
        found = contains(
            frontend_source,
            pattern,
        )

        results[name] = not found

        print(
            f"{name:<32}"
            f"{'CLEAN' if not found else 'FOUND'}"
        )

    print("\n[8] SOURCE HASHES")
    print("-" * 62)

    hashes = {
        "index.html": sha256(INDEX),
        "app.js": sha256(APP),
        "style.css": sha256(STYLE),
    }

    for filename, digest in hashes.items():
        print(f"{filename:<20} {digest}")

    print("\n[9] AUDIT RESULT")
    print("-" * 62)

    structural_requirements = [
        "PROJECT_LANDING",
        "ENTER_SYSTEM_BUTTON",
        "VIEW_RESEARCH_BUTTON",
        "SYSTEM_TITLE",
        "EVIDENCE_FIRST_TAGLINE",
        "ENTER_SYSTEM_TEXT",
        "VIEW_RESEARCH_TEXT",
        "ENTER_SYSTEM_HANDLER",
        "VIEW_RESEARCH_HANDLER",
    ]

    structural_failures = [
        name
        for name in structural_requirements
        if not results.get(name, False)
    ]

    safety_requirements = [
        "TICKET_PIPELINE_REFERENCE",
        "SKLEARN_REFERENCE",
        "PREDICT_BATCH_REFERENCE",
    ]

    safety_failures = [
        name
        for name in safety_requirements
        if not results.get(name, False)
    ]

    status = "PASS"

    if structural_failures or safety_failures:
        status = "FAIL"

    evidence = {
        "operation": "DEPLOY-OP-052",
        "title": "Home Page Visual Audit",
        "status": status,
        "files": {
            "index.html": str(INDEX),
            "app.js": str(APP),
            "style.css": str(STYLE),
        },
        "checks": results,
        "hashes": hashes,
        "structural_failures": structural_failures,
        "safety_failures": safety_failures,
        "modification": {
            "index.html": False,
            "app.js": False,
            "style.css": False,
            "backend": False,
            "frozen_runtime": False,
            "modeling": False,
        },
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

    print(f"STATUS: {status}")

    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
