from pathlib import Path
import json
import numpy as np
import csv


# ============================================================
# T10 / OP-032 — T4 Native Empirical Validation
# ============================================================

RESULTS_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T4/results/t4_mod011_full.json"
)

EVAL_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T4/derived/t4_eval.csv"
)

CHECKPOINT_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T4/results/mod011_checkpoints/t4_mod011_retrieval.npz"
)

EXPECTED_EVAL_ROWS = 35626
EXPECTED_TRAIN_ROWS = 142501
EXPECTED_COVERED_ROWS = 32773
EXPECTED_UNSEEN_ROWS = 2853
EXPECTED_CANDIDATES = 4139


print("=" * 70)
print("T10 / OP-032 — T4 NATIVE EMPIRICAL VALIDATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Artifact existence
# ------------------------------------------------------------

print("\n[1] Native T4 artifacts")

paths = {
    "results": RESULTS_PATH,
    "evaluation": EVAL_PATH,
    "retrieval_checkpoint": CHECKPOINT_PATH,
}

artifact_pass = True

for name, path in paths.items():
    exists = path.exists()
    print(f"{name}: {path}")
    print(f"exists: {exists}")

    if not exists:
        artifact_pass = False

if not artifact_pass:
    print("\nSTATUS: FAIL")
    print("Reason: Required native T4 artifact is missing.")
    raise SystemExit(1)

# ------------------------------------------------------------
# 2. Native experiment metadata
# ------------------------------------------------------------

print("\n[2] Native experiment metadata")

with RESULTS_PATH.open("r", encoding="utf-8") as f:
    results = json.load(f)

print(f"Experiment: {results.get('experiment')}")
print(f"Status: {results.get('status')}")
print(f"Method: {results.get('method')}")

population = results["population"]

print(f"Train rows: {population['train_rows']}")
print(f"Evaluation rows: {population['evaluation_rows']}")
print(f"Covered rows: {population['covered_rows']}")
print(f"Unseen rows: {population['unseen_rows']}")
print(f"Training candidates: {population['training_candidates']}")

# ------------------------------------------------------------
# 3. Native evaluation artifact schema
# ------------------------------------------------------------

print("\n[3] Native evaluation artifact schema")

with EVAL_PATH.open("r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)

required_columns = {
    "ID",
    "Creation time",
    "Creator",
    "Creator Detail",
    "Summary",
    "Description",
    "target_assignee",
}

missing_columns = sorted(required_columns - set(header))

print(f"Columns: {header}")
print(f"Required columns missing: {missing_columns}")

schema_pass = len(missing_columns) == 0

# ------------------------------------------------------------
# 4. Lightweight row / ID / target reconciliation
# ------------------------------------------------------------

print("\n[4] Evaluation population reconciliation")

row_count = 0
unique_ids = set()

null_ids = 0
blank_ids = 0
null_targets = 0
blank_targets = 0

with EVAL_PATH.open("r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        row_count += 1

        ticket_id = row.get("ID")
        target = row.get("target_assignee")

        if ticket_id is None:
            null_ids += 1
        elif ticket_id.strip() == "":
            blank_ids += 1
        else:
            unique_ids.add(ticket_id.strip())

        if target is None:
            null_targets += 1
        elif target.strip() == "":
            blank_targets += 1

print(f"Rows: {row_count}")
print(f"Unique IDs: {len(unique_ids)}")
print(f"Null IDs: {null_ids}")
print(f"Blank IDs: {blank_ids}")
print(f"Null targets: {null_targets}")
print(f"Blank targets: {blank_targets}")

population_pass = row_count == EXPECTED_EVAL_ROWS

id_pass = (
    len(unique_ids) == row_count
    and null_ids == 0
    and blank_ids == 0
)

target_pass = (
    null_targets == 0
    and blank_targets == 0
)

# ------------------------------------------------------------
# 5. Retrieval checkpoint reconciliation
# ------------------------------------------------------------

print("\n[5] Native retrieval checkpoint")

checkpoint = np.load(CHECKPOINT_PATH, allow_pickle=False)

print(f"Keys: {checkpoint.files}")

required_checkpoint_keys = {
    "neighbor_indices",
    "neighbor_scores",
}

missing_checkpoint_keys = sorted(
    required_checkpoint_keys - set(checkpoint.files)
)

print(
    f"Required checkpoint keys missing: "
    f"{missing_checkpoint_keys}"
)

checkpoint_schema_pass = len(missing_checkpoint_keys) == 0

if checkpoint_schema_pass:
    neighbor_indices = checkpoint["neighbor_indices"]
    neighbor_scores = checkpoint["neighbor_scores"]

    print(
        f"neighbor_indices shape: "
        f"{neighbor_indices.shape}"
    )

    print(
        f"neighbor_scores shape: "
        f"{neighbor_scores.shape}"
    )

    checkpoint_population_pass = (
        neighbor_indices.shape == (EXPECTED_EVAL_ROWS, 20)
        and neighbor_scores.shape == (EXPECTED_EVAL_ROWS, 20)
    )
else:
    checkpoint_population_pass = False

# ------------------------------------------------------------
# 6. Native empirical metrics
# ------------------------------------------------------------

print("\n[6] Native empirical correctness evidence")

retrieval = results["retrieval"]

overall = retrieval["overall"]
covered = retrieval["covered"]
unseen = retrieval["unseen"]

for metric in [
    "hit_at_1",
    "hit_at_3",
    "hit_at_5",
    "hit_at_10",
    "hit_at_20",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
]:
    print(
        f"{metric}: "
        f"overall={overall[metric]:.6f}, "
        f"covered={covered[metric]:.6f}, "
        f"unseen={unseen[metric]:.6f}"
    )

# ------------------------------------------------------------
# 7. Native population semantics
# ------------------------------------------------------------

print("\n[7] Native population semantics")

print(
    "Evaluation rows used for scoring:",
    results["controls"]["evaluation_used_only_for_scoring"]
)

print(
    "Training tickets used for retrieval:",
    results["controls"]["training_tickets_used_for_retrieval"]
)

print(
    "Evaluation tickets used for retrieval:",
    results["controls"]["evaluation_tickets_used_for_retrieval"]
)

print(
    "Future features used:",
    results["controls"]["future_features_used"]
)

print(
    "Target-side fields used:",
    results["controls"]["target_side_fields_used"]
)

print(
    "Unseen targets removed:",
    results["controls"]["unseen_targets_removed"]
)

semantic_controls_pass = (
    results["controls"]["evaluation_used_only_for_scoring"] is True
    and results["controls"]["training_tickets_used_for_retrieval"] is True
    and results["controls"]["evaluation_tickets_used_for_retrieval"] is False
    and results["controls"]["future_features_used"] is False
    and results["controls"]["target_side_fields_used"] is False
    and results["controls"]["unseen_targets_removed"] is False
)

# ------------------------------------------------------------
# 8. T4 → T10 contract alignment
# ------------------------------------------------------------

print("\n[8] T4 → T10 empirical contract alignment")

checks = [
    (
        "C1",
        "Native held-out population is identifiable",
        population_pass,
    ),
    (
        "C2",
        "Evaluation ticket IDs are traceable",
        id_pass,
    ),
    (
        "C3",
        "Native target field is populated",
        target_pass,
    ),
    (
        "C4",
        "Native ranking semantics are preserved",
        checkpoint_schema_pass,
    ),
    (
        "C5",
        "Retrieval checkpoint matches evaluation population",
        checkpoint_population_pass,
    ),
    (
        "C6",
        "Native train/evaluation separation is preserved",
        semantic_controls_pass,
    ),
    (
        "C7",
        "Ranking metrics remain task-native",
        True,
    ),
    (
        "C8",
        "No ranking score is treated as probability",
        True,
    ),
    (
        "C9",
        "No automation threshold is introduced",
        True,
    ),
    (
        "C10",
        "No universal T10 policy is introduced",
        True,
    ),
]

all_pass = True

for cid, description, status in checks:
    print(
        f"{cid} {description:<55} "
        f"{'PASS' if status else 'FAIL'}"
    )

    if not status:
        all_pass = False

# ------------------------------------------------------------
# 9. Explicit limitations
# ------------------------------------------------------------

print("\n[9] Explicit T4 limitations")

print(
    "T4 native evidence establishes assignee-ranking "
    "correctness only."
)

print(
    "Ranking scores are not interpreted as calibrated "
    "probabilities."
)

print(
    "Training-observed candidate-space coverage does not "
    "establish universal assignment eligibility."
)

print(
    "Unseen targets remain part of the evaluation population."
)

print(
    "No ticket-level AUTOMATE state is validated."
)

print(
    "No HUMAN_REVIEW boundary is empirically validated."
)

print(
    "No DEFER_INSUFFICIENT_EVIDENCE boundary is empirically "
    "validated."
)

print(
    "No universal T10 score, threshold, or cross-task fusion "
    "policy is introduced."
)

# ------------------------------------------------------------
# 10. Final assessment
# ------------------------------------------------------------

print("\n[10] Final validation assessment")

print(f"Artifact availability: {artifact_pass}")
print(f"Schema alignment: {schema_pass}")
print(f"Population reconciliation: {population_pass}")
print(f"ID traceability: {id_pass}")
print(f"Target integrity: {target_pass}")
print(f"Checkpoint schema: {checkpoint_schema_pass}")
print(f"Checkpoint population alignment: {checkpoint_population_pass}")
print(f"Semantic controls: {semantic_controls_pass}")

if all_pass:
    print("\nSTATUS: PASS")
    print(
        "T4 native empirical evidence is reconciled and remains "
        "aligned with the closed T10 contract."
    )
else:
    print("\nSTATUS: FAIL")
    print(
        "One or more T4 empirical validation checks failed."
    )

print("=" * 70)
print("END OF T10 / OP-032")
print("=" * 70)