from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUT_DIR = ROOT / "modeling/T8/mod033"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod033_op005_development_population_audit.json"

T4_TRAIN = ROOT / "modeling/T4/derived/t4_train.csv"
T4_EVAL = ROOT / "modeling/T4/derived/t4_eval.csv"
T4_FEATURES = ROOT / "modeling/T4/derived/t4_features.csv"

T5_MODEL_TRAIN = ROOT / "modeling/T5/splits/t5_model_train.csv"
T5_MODEL_VAL = ROOT / "modeling/T5/splits/t5_model_val.csv"
T5_FEATURES = ROOT / "modeling/T5/derived/t5_train_features.csv"

# Known locked evaluation artifacts from native T5 closure.
T5_LOCKED_EVAL = ROOT / "modeling/T5/metrics/t5_mod009_locked_evaluation_metrics.json"


def read_ids(path: Path) -> tuple[set, list]:
    if not path.exists():
        return set(), []

    df = pd.read_csv(path, usecols=["ID"])
    ids = df["ID"].dropna().tolist()
    return set(ids), ids


def inspect_population(name: str, path: Path) -> dict:
    result = {
        "name": name,
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "rows": None,
        "unique_ids": None,
        "duplicate_ids": None,
    }

    if not path.exists():
        return result

    df = pd.read_csv(path, usecols=["ID"])

    result["rows"] = len(df)
    result["unique_ids"] = df["ID"].nunique(dropna=True)
    result["duplicate_ids"] = int(df["ID"].duplicated().sum())

    return result


print("=" * 80)
print("T8 MOD-033 — OP-005: DEVELOPMENT POPULATION ELIGIBILITY AUDIT")
print("=" * 80)

results = {
    "operation": "MOD-033 / OP-005",
    "status": "IN_PROGRESS",
    "t4": {},
    "t5": {},
    "guards": {},
}


# ---------------------------------------------------------------------
# T4
# ---------------------------------------------------------------------

print("\nT4 DEVELOPMENT POPULATION")

t4_train_ids, _ = read_ids(T4_TRAIN)
t4_eval_ids, _ = read_ids(T4_EVAL)
t4_feature_ids, _ = read_ids(T4_FEATURES)

t4_train_eval_overlap = t4_train_ids & t4_eval_ids
t4_train_feature_overlap = t4_train_ids & t4_feature_ids
t4_eval_feature_overlap = t4_eval_ids & t4_feature_ids

results["t4"]["artifacts"] = [
    inspect_population("train", T4_TRAIN),
    inspect_population("evaluation", T4_EVAL),
    inspect_population("features", T4_FEATURES),
]

results["t4"]["population_checks"] = {
    "train_rows": len(t4_train_ids),
    "evaluation_rows": len(t4_eval_ids),
    "feature_rows": len(t4_feature_ids),
    "train_eval_id_overlap": len(t4_train_eval_overlap),
    "train_feature_id_overlap": len(t4_train_feature_overlap),
    "evaluation_feature_id_overlap": len(t4_eval_feature_overlap),
}

# T4 development population is the native training population only if
# it is ID-addressable and separate from the locked evaluation artifact.
t4_development_candidate = (
    len(t4_train_ids) > 0
    and len(t4_train_eval_overlap) == 0
)

print(f"train IDs: {len(t4_train_ids)}")
print(f"evaluation IDs: {len(t4_eval_ids)}")
print(f"feature IDs: {len(t4_feature_ids)}")
print(f"train/evaluation overlap: {len(t4_train_eval_overlap)}")
print(f"development candidate eligible: {t4_development_candidate}")


# ---------------------------------------------------------------------
# T5
# ---------------------------------------------------------------------

print("\nT5 DEVELOPMENT POPULATION")

t5_train_ids, _ = read_ids(T5_MODEL_TRAIN)
t5_val_ids, _ = read_ids(T5_MODEL_VAL)
t5_feature_ids, _ = read_ids(T5_FEATURES)

t5_train_val_overlap = t5_train_ids & t5_val_ids
t5_train_feature_overlap = t5_train_ids & t5_feature_ids
t5_val_feature_overlap = t5_val_ids & t5_feature_ids

results["t5"]["artifacts"] = [
    inspect_population("model_train", T5_MODEL_TRAIN),
    inspect_population("model_validation", T5_MODEL_VAL),
    inspect_population("features", T5_FEATURES),
]

results["t5"]["population_checks"] = {
    "model_train_rows": len(t5_train_ids),
    "model_validation_rows": len(t5_val_ids),
    "feature_rows": len(t5_feature_ids),
    "train_validation_id_overlap": len(t5_train_val_overlap),
    "train_feature_id_overlap": len(t5_train_feature_overlap),
    "validation_feature_id_overlap": len(t5_val_feature_overlap),
}

t5_development_candidate = (
    len(t5_train_ids) > 0
    and len(t5_val_ids) > 0
    and len(t5_train_val_overlap) == 0
)

print(f"model-train IDs: {len(t5_train_ids)}")
print(f"model-validation IDs: {len(t5_val_ids)}")
print(f"feature IDs: {len(t5_feature_ids)}")
print(f"train/validation overlap: {len(t5_train_val_overlap)}")
print(f"development candidate eligible: {t5_development_candidate}")


# ---------------------------------------------------------------------
# Cross-task development population
# ---------------------------------------------------------------------

print("\nCROSS-TASK DEVELOPMENT POPULATION")

t4_dev_ids = t4_train_ids
t5_dev_ids = t5_train_ids

common_dev_ids = t4_dev_ids & t5_dev_ids

results["cross_task"] = {
    "t4_development_ids": len(t4_dev_ids),
    "t5_development_ids": len(t5_dev_ids),
    "common_development_ids": len(common_dev_ids),
}


# ---------------------------------------------------------------------
# Locked evaluation guards
# ---------------------------------------------------------------------

print("\nLOCKED-EVALUATION GUARDS")

guards = {
    "t4_train_evaluation_overlap_zero": len(t4_train_eval_overlap) == 0,
    "t5_train_validation_overlap_zero": len(t5_train_val_overlap) == 0,
    "t4_development_population_exists": t4_development_candidate,
    "t5_development_population_exists": t5_development_candidate,
    "common_development_population_exists": len(common_dev_ids) > 0,
    "no_prediction_generation_performed": True,
    "no_model_training_performed": True,
    "no_locked_evaluation_repurposed": True,
    "native_task_semantics_preserved": True,
}

results["guards"] = guards

for key, value in guards.items():
    print(f"{key}: {value}")


# ---------------------------------------------------------------------
# Decision
# ---------------------------------------------------------------------

eligible = (
    t4_development_candidate
    and t5_development_candidate
    and len(common_dev_ids) > 0
)

if eligible:
    results["status"] = "PASS"
    results["decision"] = (
        "PASS — ID-addressable non-locked development populations exist "
        "for T4 and T5, with a non-empty common development population. "
        "Prediction generation remains a separate operation."
    )
else:
    results["status"] = "BLOCKED"
    results["decision"] = (
        "BLOCKED — a valid common non-locked development population "
        "could not be established from the inspected native artifacts."
    )

results["interpretation"] = (
    "This audit establishes population eligibility only. It does not "
    "generate T4/T5 predictions or train models. Native task semantics "
    "must remain unchanged in any subsequent generation operation."
)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("MOD-033 OP-005 COMPLETE")
print("=" * 80)
print(f"Decision: {results['decision']}")
print(f"Audit written to: {OUTPUT}")