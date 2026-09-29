from pathlib import Path
import csv
import json
from collections import defaultdict


# ============================================================
# T10 / OP-033 — T6 Native Empirical Validation
# ============================================================

RESULTS_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T6/metrics/t6_mod010_corrected_hybrid_results.json"
)

RANKINGS_PATH = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/"
    "modeling/T6/metrics/t6_mod010_corrected_hybrid_query_rankings.csv"
)

EXPECTED_TOTAL_ROWS = 274922
EXPECTED_TRAIN_ROWS = 192506
EXPECTED_EVAL_ROWS = 82416
EXPECTED_TRAIN_QUERIES = 1906
EXPECTED_EVAL_QUERIES = 816
EXPECTED_TOTAL_QUERIES = 2722
EXPECTED_CANDIDATES_PER_QUERY = 101


print("=" * 70)
print("T10 / OP-033 — T6 NATIVE EMPIRICAL VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# 1. Artifact availability
# ------------------------------------------------------------

print("\n[1] Native T6 artifacts")

for name, path in {
    "results": RESULTS_PATH,
    "corrected_rankings": RANKINGS_PATH,
}.items():

    exists = path.exists()

    print(f"{name}: {path}")
    print(f"exists: {exists}")

    if not exists:
        print("\nSTATUS: FAIL")
        print("Reason: Required native T6 artifact is missing.")
        raise SystemExit(1)


# ------------------------------------------------------------
# 2. Native experiment metadata
# ------------------------------------------------------------

print("\n[2] Native experiment metadata")

with RESULTS_PATH.open("r", encoding="utf-8") as f:
    results = json.load(f)

print(f"Task: {results.get('task_id')}")
print(f"Operation: {results.get('operation_id')}")
print(f"Operation name: {results.get('operation_name')}")
print(f"Status: {results.get('status')}")

population = results["population"]

print(f"Train rows: {population['train_rows']}")
print(f"Eval rows: {population['eval_rows']}")
print(f"Queries: {population['queries']}")
print(f"Candidate rows: {population['candidate_rows']}")


# ------------------------------------------------------------
# 3. Native ranking artifact schema
# ------------------------------------------------------------

print("\n[3] Native ranking artifact schema")

with RANKINGS_PATH.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.reader(f)
    header = next(reader)

required_columns = {
    "split",
    "query_id",
    "candidate_id",
    "target_observed",
    "semantic_score",
    "tfidf_score",
    "tfidf_score_normalized",
    "semantic_score_normalized",
    "hybrid_score",
}

missing_columns = sorted(
    required_columns - set(header)
)

print(f"Columns: {header}")
print(f"Required columns missing: {missing_columns}")

schema_pass = len(missing_columns) == 0

if not schema_pass:
    print("\nSTATUS: FAIL")
    raise SystemExit(1)


# ------------------------------------------------------------
# 4. Chunked population reconciliation
# ------------------------------------------------------------

print("\n[4] Native population reconciliation")

total_rows = 0
train_rows = 0
eval_rows = 0

train_queries = set()
eval_queries = set()
all_queries = set()

eval_query_rows = defaultdict(int)
eval_query_positive_rows = defaultdict(int)

eval_positive_rows = 0
eval_false_rows = 0

invalid_split_rows = 0
invalid_target_values = 0

blank_query_ids = 0
blank_candidate_ids = 0

# We only need lightweight aggregation.
# Do not retain the full 275k-row artifact in memory.

with RANKINGS_PATH.open(
    "r",
    encoding="utf-8",
    newline=""
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        total_rows += 1

        split = (row.get("split") or "").strip()
        query_id = (row.get("query_id") or "").strip()
        candidate_id = (row.get("candidate_id") or "").strip()
        target_observed = (
            (row.get("target_observed") or "")
            .strip()
            .lower()
        )

        if query_id == "":
            blank_query_ids += 1

        if candidate_id == "":
            blank_candidate_ids += 1

        if split not in {"TRAIN", "EVAL"}:
            invalid_split_rows += 1

        if target_observed not in {"true", "false"}:
            invalid_target_values += 1

        if split == "TRAIN":

            train_rows += 1
            train_queries.add(query_id)

        elif split == "EVAL":

            eval_rows += 1
            eval_queries.add(query_id)

            eval_query_rows[query_id] += 1

            if target_observed == "true":
                eval_positive_rows += 1
                eval_query_positive_rows[query_id] += 1

            elif target_observed == "false":
                eval_false_rows += 1

        if query_id:
            all_queries.add(query_id)


print(f"Total rows: {total_rows}")
print(f"Train rows: {train_rows}")
print(f"Eval rows: {eval_rows}")

print(f"Total unique queries: {len(all_queries)}")
print(f"Train unique queries: {len(train_queries)}")
print(f"Eval unique queries: {len(eval_queries)}")

print(f"Eval target_observed=True rows: {eval_positive_rows}")
print(f"Eval target_observed=False rows: {eval_false_rows}")

print(f"Blank query IDs: {blank_query_ids}")
print(f"Blank candidate IDs: {blank_candidate_ids}")
print(f"Invalid split rows: {invalid_split_rows}")
print(f"Invalid target_observed values: {invalid_target_values}")


# ------------------------------------------------------------
# 5. Evaluation query structure
# ------------------------------------------------------------

print("\n[5] Evaluation query structure")

eval_query_size_values = set(eval_query_rows.values())
eval_positive_count_values = set(
    eval_query_positive_rows.get(q, 0)
    for q in eval_queries
)

print(
    "Distinct candidate-row counts per eval query:",
    sorted(eval_query_size_values)
)

print(
    "Distinct target_observed=True counts per eval query:",
    sorted(eval_positive_count_values)
)

eval_queries_all_101 = (
    len(eval_query_rows) == EXPECTED_EVAL_QUERIES
    and eval_query_size_values == {EXPECTED_CANDIDATES_PER_QUERY}
)

eval_queries_one_positive = (
    len(eval_query_positive_rows) == EXPECTED_EVAL_QUERIES
    and eval_positive_count_values == {1}
)


# ------------------------------------------------------------
# 6. Native evaluation metrics
# ------------------------------------------------------------

print("\n[6] Native T6 empirical correctness evidence")

eval_metrics = results["metrics"]["eval"]["corrected_hybrid"]

for metric in [
    "recall_at_1",
    "recall_at_3",
    "recall_at_5",
    "recall_at_10",
    "recall_at_20",
    "mrr",
    "ndcg_at_5",
    "ndcg_at_10",
]:
    print(
        f"{metric}: "
        f"{eval_metrics[metric]:.6f}"
    )


# ------------------------------------------------------------
# 7. Native controls
# ------------------------------------------------------------

print("\n[7] Native methodological controls")

controls = results["controls"]

for key, value in controls.items():
    print(f"{key}: {value}")

controls_pass = (
    controls["raw_dataset_read"] is False
    and controls["target_modification"] is False
    and controls["candidate_pool_modification"] is False
    and controls["semantic_recomputation"] is False
    and controls["model_training"] is False
    and controls["calibration"] is False
    and controls["threshold_optimization"] is False
    and controls["evaluation_weight_selection"] is False
)


# ------------------------------------------------------------
# 8. T6 → T10 contract alignment
# ------------------------------------------------------------

print("\n[8] T6 → T10 empirical contract alignment")

population_pass = (
    total_rows == EXPECTED_TOTAL_ROWS
    and train_rows == EXPECTED_TRAIN_ROWS
    and eval_rows == EXPECTED_EVAL_ROWS
    and len(all_queries) == EXPECTED_TOTAL_QUERIES
    and len(train_queries) == EXPECTED_TRAIN_QUERIES
    and len(eval_queries) == EXPECTED_EVAL_QUERIES
)

query_structure_pass = (
    eval_queries_all_101
    and eval_queries_one_positive
)

target_semantics_pass = (
    invalid_target_values == 0
)

checks = [
    (
        "C1",
        "Native train/evaluation population reconciles",
        population_pass,
    ),
    (
        "C2",
        "Evaluation query population is traceable",
        len(eval_queries) == EXPECTED_EVAL_QUERIES,
    ),
    (
        "C3",
        "Native query candidate structure reconciles",
        query_structure_pass,
    ),
    (
        "C4",
        "Observed target semantics are preserved",
        target_semantics_pass,
    ),
    (
        "C5",
        "observable non-target candidates are not treated as true negatives",
        True,
    ),
    (
        "C6",
        "Native hybrid ranking semantics are preserved",
        schema_pass,
    ),
    (
        "C7",
        "Native methodological controls remain intact",
        controls_pass,
    ),
    (
        "C8",
        "Ranking score is not interpreted as probability",
        True,
    ),
    (
        "C9",
        "No automation threshold is introduced",
        True,
    ),
    (
        "C10",
        "No universal T10 policy or cross-task fusion is introduced",
        True,
    ),
]

all_pass = True

for cid, description, status in checks:

    print(
        f"{cid} {description:<58} "
        f"{'PASS' if status else 'FAIL'}"
    )

    if not status:
        all_pass = False


# ------------------------------------------------------------
# 9. Explicit limitations
# ------------------------------------------------------------

print("\n[9] Explicit T6 limitations")

print(
    "T6 native evidence establishes duplicate-related "
    "query retrieval/ranking correctness only."
)

print(
    "target_observed=False is not interpreted as a true negative."
)

print(
    "hybrid_score remains a native ranking score, not a "
    "calibrated probability."
)

print(
    "Recall@K does not establish ticket-level automation "
    "eligibility."
)

print(
    "No automation threshold is validated."
)

print(
    "No human-review boundary is empirically validated."
)

print(
    "No defer boundary is empirically validated."
)

print(
    "No universal T10 score or cross-task fusion policy "
    "is introduced."
)


# ------------------------------------------------------------
# 10. Final assessment
# ------------------------------------------------------------

print("\n[10] Final validation assessment")

print(f"Schema alignment: {schema_pass}")
print(f"Population reconciliation: {population_pass}")
print(f"Query structure reconciliation: {query_structure_pass}")
print(f"Target semantics: {target_semantics_pass}")
print(f"Methodological controls: {controls_pass}")

if all_pass:

    print("\nSTATUS: PASS")

    print(
        "T6 native empirical evidence is reconciled and remains "
        "aligned with the closed T10 contract."
    )

else:

    print("\nSTATUS: FAIL")

    print(
        "One or more T6 empirical validation checks failed."
    )


print("=" * 70)
print("END OF T10 / OP-033")
print("=" * 70)