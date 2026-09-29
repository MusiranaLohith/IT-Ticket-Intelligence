from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T4_EVAL = ROOT / "modeling/T4/derived/t4_eval.csv"
T4_TRAIN = ROOT / "modeling/T4/derived/t4_train.csv"
T4_CHECKPOINT = (
    ROOT / "modeling/T4/results/mod011_checkpoints/"
    "t4_mod011_retrieval.npz"
)

T5_VAL = ROOT / "modeling/T5/splits/t5_model_val.csv"
T5_PREDICTIONS = (
    ROOT / "modeling/T5/metrics/"
    "t5_mod007_calibrated_validation_predictions.npz"
)

OUT_DIR = ROOT / "modeling/T8/mod033"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod033_op007_t4_t5_development_evidence.csv"
MANIFEST = OUT_DIR / "t8_mod033_op007_generation_manifest.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


print("=" * 80)
print("T8 MOD-033 — OP-007: T4/T5 NATIVE DEVELOPMENT EVIDENCE GENERATION")
print("=" * 80)


# ---------------------------------------------------------------------
# 1. Load source populations
# ---------------------------------------------------------------------

t4_eval = pd.read_csv(T4_EVAL)
t4_train = pd.read_csv(T4_TRAIN)
t5_val = pd.read_csv(T5_VAL)

required_t4 = {"ID", "target_assignee"}
required_t5 = {"ID"}

if not required_t4.issubset(t4_eval.columns):
    fail("T4 evaluation artifact is missing required columns.")

if not required_t4.issubset(t4_train.columns):
    fail("T4 training artifact is missing required columns.")

if not required_t5.issubset(t5_val.columns):
    fail("T5 validation artifact is missing ID.")

if t4_eval["ID"].duplicated().any():
    fail("Duplicate T4 evaluation IDs detected.")

if t5_val["ID"].duplicated().any():
    fail("Duplicate T5 validation IDs detected.")

if t4_train["ID"].duplicated().any():
    fail("Duplicate T4 training IDs detected.")


# ---------------------------------------------------------------------
# 2. Load native prediction artifacts
# ---------------------------------------------------------------------

t4_npz = np.load(T4_CHECKPOINT, allow_pickle=False)
t5_npz = np.load(T5_PREDICTIONS, allow_pickle=False)

required_t4_npz = {"neighbor_indices", "neighbor_scores"}
required_t5_npz = {"p_sigmoid"}

if not required_t4_npz.issubset(t4_npz.files):
    fail("T4 checkpoint missing required native ranking arrays.")

if not required_t5_npz.issubset(t5_npz.files):
    fail("T5 checkpoint missing frozen sigmoid probability output.")

neighbor_indices = t4_npz["neighbor_indices"]
neighbor_scores = t4_npz["neighbor_scores"]
p_sigmoid = t5_npz["p_sigmoid"]


# ---------------------------------------------------------------------
# 3. Verify exact source-row ordering
# ---------------------------------------------------------------------

if len(neighbor_indices) != len(t4_eval):
    fail("T4 checkpoint row count does not match T4 evaluation rows.")

if len(neighbor_scores) != len(t4_eval):
    fail("T4 score row count does not match T4 evaluation rows.")

if len(p_sigmoid) != len(t5_val):
    fail("T5 probability row count does not match T5 validation rows.")

if neighbor_indices.shape[1] != 20:
    fail("T4 native retrieval does not contain exactly 20 candidates.")

if neighbor_scores.shape != neighbor_indices.shape:
    fail("T4 neighbor index/score shapes do not match.")


# ---------------------------------------------------------------------
# 4. Establish common out-of-sample development population
# ---------------------------------------------------------------------

t4_id_to_pos = {
    ticket_id: i
    for i, ticket_id in enumerate(t4_eval["ID"].tolist())
}

t5_id_to_pos = {
    ticket_id: i
    for i, ticket_id in enumerate(t5_val["ID"].tolist())
}

common_ids = [
    ticket_id
    for ticket_id in t4_eval["ID"].tolist()
    if ticket_id in t5_id_to_pos
]

if not common_ids:
    fail("No common T4-evaluation / T5-validation IDs found.")

print(f"T4 evaluation rows: {len(t4_eval)}")
print(f"T5 validation rows: {len(t5_val)}")
print(f"Common development IDs: {len(common_ids)}")


# ---------------------------------------------------------------------
# 5. Build native T4 ranking evidence
# ---------------------------------------------------------------------

train_targets = t4_train["target_assignee"].astype(str).to_numpy()

records = []

for ticket_id in common_ids:
    t4_pos = t4_id_to_pos[ticket_id]
    t5_pos = t5_id_to_pos[ticket_id]

    indices = neighbor_indices[t4_pos]
    scores = neighbor_scores[t4_pos]

    ranked_assignees = train_targets[indices]

    row = {
        "ID": ticket_id,

        "t4_rank_1_assignee": ranked_assignees[0],
        "t4_rank_1_score": float(scores[0]),

        "t4_rank_2_assignee": ranked_assignees[1],
        "t4_rank_2_score": float(scores[1]),

        "t4_rank_3_assignee": ranked_assignees[2],
        "t4_rank_3_score": float(scores[2]),

        "t4_rank_4_assignee": ranked_assignees[3],
        "t4_rank_4_score": float(scores[3]),

        "t4_rank_5_assignee": ranked_assignees[4],
        "t4_rank_5_score": float(scores[4]),

        "t4_rank_6_assignee": ranked_assignees[5],
        "t4_rank_6_score": float(scores[5]),

        "t4_rank_7_assignee": ranked_assignees[6],
        "t4_rank_7_score": float(scores[6]),

        "t4_rank_8_assignee": ranked_assignees[7],
        "t4_rank_8_score": float(scores[7]),

        "t4_rank_9_assignee": ranked_assignees[8],
        "t4_rank_9_score": float(scores[8]),

        "t4_rank_10_assignee": ranked_assignees[9],
        "t4_rank_10_score": float(scores[9]),

        "t4_rank_11_assignee": ranked_assignees[10],
        "t4_rank_11_score": float(scores[10]),

        "t4_rank_12_assignee": ranked_assignees[11],
        "t4_rank_12_score": float(scores[11]),

        "t4_rank_13_assignee": ranked_assignees[12],
        "t4_rank_13_score": float(scores[12]),

        "t4_rank_14_assignee": ranked_assignees[13],
        "t4_rank_14_score": float(scores[13]),

        "t4_rank_15_assignee": ranked_assignees[14],
        "t4_rank_15_score": float(scores[14]),

        "t4_rank_16_assignee": ranked_assignees[15],
        "t4_rank_16_score": float(scores[15]),

        "t4_rank_17_assignee": ranked_assignees[16],
        "t4_rank_17_score": float(scores[16]),

        "t4_rank_18_assignee": ranked_assignees[17],
        "t4_rank_18_score": float(scores[17]),

        "t4_rank_19_assignee": ranked_assignees[18],
        "t4_rank_19_score": float(scores[18]),

        "t4_rank_20_assignee": ranked_assignees[19],
        "t4_rank_20_score": float(scores[19]),

        "t5_p_duplicate": float(p_sigmoid[t5_pos]),

        "t4_source_population": "t4_eval",
        "t5_source_population": "t5_model_val",
        "t4_prediction_boundary": "Creation",
        "t5_prediction_boundary": "Creation",
        "t4_implementation": "T4-MOD-011-BM25",
        "t5_implementation": "T5-MOD-007-SIGMOID",
    }

    records.append(row)


output = pd.DataFrame(records)


# ---------------------------------------------------------------------
# 6. Integrity checks
# ---------------------------------------------------------------------

if len(output) != len(common_ids):
    fail("Output row count does not match common development population.")

if output["ID"].duplicated().any():
    fail("Duplicate IDs detected in generated development evidence.")

if output["t5_p_duplicate"].isna().any():
    fail("Missing T5 probabilities detected.")

if not np.isfinite(output["t5_p_duplicate"]).all():
    fail("Non-finite T5 probabilities detected.")

if not (
    (output["t5_p_duplicate"] >= 0.0)
    & (output["t5_p_duplicate"] <= 1.0)
).all():
    fail("T5 probabilities outside [0,1] detected.")

for i in range(1, 21):
    col = f"t4_rank_{i}_score"
    if not np.isfinite(output[col]).all():
        fail(f"Non-finite T4 ranking scores detected in {col}.")


# ---------------------------------------------------------------------
# 7. Locked-evaluation guards
# ---------------------------------------------------------------------

t4_eval_ids = set(t4_eval["ID"])
t5_val_ids = set(t5_val["ID"])

if not set(output["ID"]).issubset(t4_eval_ids):
    fail("Generated IDs fall outside T4 evaluation population.")

if not set(output["ID"]).issubset(t5_val_ids):
    fail("Generated IDs fall outside T5 validation population.")


# ---------------------------------------------------------------------
# 8. Save native evidence
# ---------------------------------------------------------------------

output.to_csv(OUTPUT, index=False)

manifest = {
    "operation": "MOD-033 / OP-007",
    "status": "PASS",
    "rows": int(len(output)),
    "common_development_ids": int(len(common_ids)),

    "t4": {
        "source_population": "t4_eval.csv",
        "source_rows": int(len(t4_eval)),
        "implementation": "T4-MOD-011-BM25",
        "output_semantics": "native ranked assignee candidates with retrieval scores",
        "top_k": 20,
        "prediction_boundary": "Creation",
        "checkpoint": str(T4_CHECKPOINT),
    },

    "t5": {
        "source_population": "t5_model_val.csv",
        "source_rows": int(len(t5_val)),
        "implementation": "T5-MOD-007-SIGMOID",
        "output_semantics": "native calibrated duplicate probability",
        "probability_field": "p_duplicate",
        "prediction_boundary": "Creation",
        "checkpoint": str(T5_PREDICTIONS),
    },

    "guards": {
        "same_ticket_ids": True,
        "t4_native_ranking_preserved": True,
        "t4_ranking_to_probability_conversion": False,
        "t5_native_probability_preserved": True,
        "t5_identity_reinterpretation": False,
        "synthetic_t8_target": False,
        "model_training_performed": False,
        "locked_evaluation_repurposed": False,
        "post_creation_features_used": False,
    },

    "artifacts": {
        "development_evidence": str(OUTPUT),
        "manifest": str(MANIFEST),
    },
}

with MANIFEST.open("w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)


print("\n" + "=" * 80)
print("MOD-033 OP-007 COMPLETE")
print("=" * 80)
print(f"Development evidence rows: {len(output)}")
print("T4 semantics: native BM25 ranked candidates")
print("T5 semantics: native sigmoid-calibrated duplicate probability")
print("Model training: NO")
print("Locked evaluation repurposed: NO")
print("Synthetic T8 target: NO")
print(f"Evidence: {OUTPUT}")
print(f"Manifest: {MANIFEST}")
print("=" * 80)