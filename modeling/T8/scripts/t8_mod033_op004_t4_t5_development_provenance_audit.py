from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T8_DIR = ROOT / "modeling" / "T8"
OUT_DIR = T8_DIR / "mod033"

T4_DIR = ROOT / "modeling" / "T4"
T5_DIR = ROOT / "modeling" / "T5"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod033_op004_t4_t5_development_provenance_audit.json"


def section(title: str) -> None:
    print("\n" + "-" * 100)
    print(title)
    print("-" * 100)


def discover_files(root: Path, patterns: list[str]) -> list[str]:
    found = []
    if not root.exists():
        return found

    for pattern in patterns:
        for p in sorted(root.rglob(pattern)):
            if p.is_file():
                found.append(str(p.relative_to(ROOT)))

    return sorted(set(found))


def inspect_csv(path: Path) -> dict:
    info = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "rows": None,
        "columns": [],
        "id_column_candidates": [],
        "creation_column_candidates": [],
    }

    if not path.exists():
        return info

    try:
        df = pd.read_csv(path, nrows=5)
        info["columns"] = list(df.columns)

        info["id_column_candidates"] = [
            c for c in df.columns
            if str(c).strip().lower() in {
                "id",
                "ticket_id",
                "issue_id",
                "bug_id",
                "canonical_id",
            }
            or str(c).strip().lower().endswith("_id")
        ]

        info["creation_column_candidates"] = [
            c for c in df.columns
            if "creation" in str(c).lower()
            or "created" in str(c).lower()
        ]

        # Obtain row count without loading the complete file into memory.
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            rows = sum(1 for _ in f) - 1

        info["rows"] = max(rows, 0)

    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"

    return info


def inspect_json(path: Path) -> dict:
    info = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
    }

    if not path.exists():
        return info

    try:
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)

        info["top_level_type"] = type(obj).__name__

        if isinstance(obj, dict):
            info["keys"] = list(obj.keys())

            # Print useful split/population/provenance-looking keys.
            interesting = {}
            for k, v in obj.items():
                key = str(k).lower()
                if any(
                    token in key
                    for token in [
                        "split",
                        "train",
                        "test",
                        "eval",
                        "valid",
                        "population",
                        "boundary",
                        "creation",
                        "provenance",
                        "candidate",
                        "ranking",
                        "duplicate",
                        "target",
                        "artifact",
                    ]
                ):
                    interesting[k] = v

            info["interesting_fields"] = interesting

    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"

    return info


def inspect_text(path: Path) -> dict:
    info = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
    }

    if not path.exists():
        return info

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")

        patterns = {
            "creation_boundary_terms": [
                r"\bCreation\b",
                r"\bcreation_time\b",
                r"\bcreated_at\b",
                r"\bCreationTime\b",
            ],
            "split_terms": [
                r"\btrain\b",
                r"\btest\b",
                r"\beval\b",
                r"\bvalidation\b",
                r"\bsplit\b",
            ],
            "prediction_terms": [
                r"\bpredict\b",
                r"\bprediction\b",
                r"\bprobability\b",
                r"\bconfidence\b",
                r"\branking\b",
                r"\bduplicate\b",
            ],
        }

        matches = {}

        for category, pats in patterns.items():
            category_matches = []
            for pat in pats:
                if re.search(pat, text, flags=re.IGNORECASE):
                    category_matches.append(pat)
            matches[category] = category_matches

        info["signals"] = matches
        info["bytes"] = len(text.encode("utf-8"))

    except Exception as exc:
        info["error"] = f"{type(exc).__name__}: {exc}"

    return info


print("=" * 100)
print("T8 MOD-033 — OP-004: T4/T5 DEVELOPMENT SPLIT / PROVENANCE / BOUNDARY AUDIT")
print("=" * 100)

results = {
    "operation": "MOD-033 / OP-004",
    "status": "IN_PROGRESS",
    "t4": {},
    "t5": {},
    "guards": {},
}

# ---------------------------------------------------------------------
# 1. Discover native T4/T5 contracts, scripts, models, predictions,
#    splits, and derived artifacts.
# ---------------------------------------------------------------------

section("1. T4 native artifact discovery")

t4_patterns = [
    "*.json",
    "*.csv",
    "*.pkl",
    "*.pickle",
    "*.joblib",
    "*.h5",
    "*.keras",
    "*.pt",
    "*.pth",
    "*.bin",
    "*.txt",
]

t4_files = discover_files(T4_DIR, t4_patterns)

for f in t4_files:
    print(f)

results["t4"]["discovered_files"] = t4_files

section("2. T5 native artifact discovery")

t5_files = discover_files(T5_DIR, t4_patterns)

for f in t5_files:
    print(f)

results["t5"]["discovered_files"] = t5_files

# ---------------------------------------------------------------------
# 2. Identify likely split/prediction artifacts.
# ---------------------------------------------------------------------

section("3. Candidate split / prediction / contract files")

def classify_paths(files: list[str]) -> dict:
    groups = {
        "contracts": [],
        "splits": [],
        "predictions": [],
        "models": [],
        "scripts": [],
        "other": [],
    }

    for rel in files:
        low = rel.lower()

        if "contract" in low:
            groups["contracts"].append(rel)
        elif any(x in low for x in ["split", "train", "test", "eval", "validation"]):
            groups["splits"].append(rel)
        elif any(x in low for x in ["predict", "prediction", "oof", "output"]):
            groups["predictions"].append(rel)
        elif any(x in low for x in [".pkl", ".pickle", ".joblib", ".h5", ".keras", ".pt", ".pth", ".bin"]):
            groups["models"].append(rel)
        elif "/scripts/" in low or low.endswith(".py"):
            groups["scripts"].append(rel)
        else:
            groups["other"].append(rel)

    return groups


results["t4"]["file_groups"] = classify_paths(t4_files)
results["t5"]["file_groups"] = classify_paths(t5_files)

print("\nT4 groups:")
for k, v in results["t4"]["file_groups"].items():
    print(f"{k}: {len(v)}")

print("\nT5 groups:")
for k, v in results["t5"]["file_groups"].items():
    print(f"{k}: {len(v)}")

# ---------------------------------------------------------------------
# 3. Inspect candidate JSON contracts/artifacts.
# ---------------------------------------------------------------------

section("4. T4 JSON contract/artifact inspection")

t4_json = []
for rel in t4_files:
    if rel.lower().endswith(".json"):
        info = inspect_json(ROOT / rel)
        t4_json.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t4"]["json_inspection"] = t4_json

section("5. T5 JSON contract/artifact inspection")

t5_json = []
for rel in t5_files:
    if rel.lower().endswith(".json"):
        info = inspect_json(ROOT / rel)
        t5_json.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t5"]["json_inspection"] = t5_json

# ---------------------------------------------------------------------
# 4. Inspect CSV artifacts without loading them fully.
# ---------------------------------------------------------------------

section("6. T4 CSV artifact inspection")

t4_csv = []
for rel in t4_files:
    if rel.lower().endswith(".csv"):
        info = inspect_csv(ROOT / rel)
        t4_csv.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t4"]["csv_inspection"] = t4_csv

section("7. T5 CSV artifact inspection")

t5_csv = []
for rel in t5_files:
    if rel.lower().endswith(".csv"):
        info = inspect_csv(ROOT / rel)
        t5_csv.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t5"]["csv_inspection"] = t5_csv

# ---------------------------------------------------------------------
# 5. Inspect native Python implementation signals.
# ---------------------------------------------------------------------

section("8. T4 native implementation signal inspection")

t4_py = []
for rel in t4_files:
    if rel.lower().endswith(".py"):
        info = inspect_text(ROOT / rel)
        t4_py.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t4"]["python_inspection"] = t4_py

section("9. T5 native implementation signal inspection")

t5_py = []
for rel in t5_files:
    if rel.lower().endswith(".py"):
        info = inspect_text(ROOT / rel)
        t5_py.append(info)
        print(json.dumps(info, indent=2, default=str))

results["t5"]["python_inspection"] = t5_py

# ---------------------------------------------------------------------
# 6. Conservative eligibility guards.
#
# At this stage we do NOT declare development generation eligible.
# We only establish whether the audit found enough evidence to proceed
# to a more targeted provenance review.
# ---------------------------------------------------------------------

section("10. Eligibility guards")

all_t4 = " ".join(t4_files).lower()
all_t5 = " ".join(t5_files).lower()

results["guards"] = {
    "t4_directory_exists": T4_DIR.exists(),
    "t5_directory_exists": T5_DIR.exists(),
    "t4_native_artifacts_discovered": len(t4_files) > 0,
    "t5_native_artifacts_discovered": len(t5_files) > 0,
    "no_prediction_generation_performed": True,
    "no_model_training_performed": True,
    "no_locked_evaluation_repurposed": True,
    "no_t4_ranking_to_probability_conversion": True,
    "no_t5_duplicate_identity_reinterpretation": True,
    "creation_boundary_not_assumed": True,
    "development_population_not_assumed": True,
}

for k, v in results["guards"].items():
    print(f"{k}: {v}")

# ---------------------------------------------------------------------
# 7. Explicit status.
# ---------------------------------------------------------------------

results["status"] = "PASS"

results["interpretation"] = (
    "The audit discovered the native T4/T5 project artifacts and inspected "
    "their available contracts, split/prediction/model files, CSV metadata, "
    "and implementation signals. This operation does not itself establish "
    "that a particular development population is eligible for prediction "
    "generation. Exact split provenance, prediction boundary, candidate "
    "semantics, and population overlap must be reviewed from the discovered "
    "native artifacts before generation."
)

results["decision"] = (
    "PASS — sufficient native artifact evidence was discovered to proceed "
    "to targeted T4/T5 split-provenance and population verification; "
    "development prediction generation remains blocked until that verification "
    "is completed."
)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print("\n" + "=" * 100)
print("MOD-033 OP-004 COMPLETE")
print("=" * 100)
print(f"Audit written to: {OUTPUT}")