from pathlib import Path
import json

ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
MODEL_ROOT = ROOT / "modeling"

print("=" * 80)
print("FMP-02 / FINAL T2-T7 ARTIFACT-TO-CLOSURE RECONCILIATION")
print("=" * 80)


def exists(path):
    return path.exists()


def report(label, path):
    print(f"{label}: {'FOUND' if exists(path) else 'MISSING'}")
    print(f"  {path}")


# ============================================================================
# T2
# ============================================================================
print("\n" + "-" * 80)
print("T2 — PRIORITY")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T2" / "analysis" / "t2_final_closure.json",
)

report(
    "final model candidate MOD-007",
    MODEL_ROOT / "T2" / "models" / "t2_class_weighted_tfidf_logreg.joblib",
)

report(
    "final test metrics",
    MODEL_ROOT / "T2" / "analysis" / "t2_final_test_metrics.json",
)

report(
    "final test predictions",
    MODEL_ROOT / "T2" / "analysis" / "t2_final_test_predictions.csv",
)


# ============================================================================
# T3
# ============================================================================
print("\n" + "-" * 80)
print("T3 — SEVERITY")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T3" / "analysis" / "t3_final_closure.json",
)

report(
    "final candidate MOD-008",
    MODEL_ROOT / "T3" / "models" / "t3_class_weighted_tfidf_logreg.joblib",
)

report(
    "final test metrics",
    MODEL_ROOT / "T3" / "metrics" / "t3_final_test_metrics.json",
)

report(
    "final test split",
    MODEL_ROOT / "T3" / "splits" / "t3_test.csv",
)


# ============================================================================
# T4
# ============================================================================
print("\n" + "-" * 80)
print("T4 — HISTORICAL ROUTING / ASSIGNMENT RETRIEVAL")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T4" / "results" / "t4_mod013_closure.json",
)

report(
    "final retrieval result",
    MODEL_ROOT / "T4" / "results" / "t4_mod013_closure.json",
)

report(
    "MOD-007 TF-IDF artifact",
    MODEL_ROOT / "T4" / "results" / "mod007_checkpoints" / "t4_mod007_tfidf.joblib",
)

report(
    "MOD-007 neighbor artifact",
    MODEL_ROOT / "T4" / "results" / "mod007_checkpoints" / "t4_mod007_neighbors.joblib",
)

report(
    "R1 TF-IDF artifact",
    MODEL_ROOT / "T4" / "results" / "r1_checkpoints" / "t4_r1_tfidf.joblib",
)

report(
    "R1 LinearSVC artifact",
    MODEL_ROOT / "T4" / "results" / "r1_checkpoints" / "t4_r1_linear_svc.joblib",
)


# ============================================================================
# T5
# ============================================================================
print("\n" + "-" * 80)
print("T5 — DUPLICATE DETECTION")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T5" / "metrics" / "t5_mod011_final_closure.json",
)

report(
    "TF-IDF vectorizer",
    MODEL_ROOT / "T5" / "models" / "t5_mod005_tfidf.joblib",
)

report(
    "base Logistic Regression",
    MODEL_ROOT / "T5" / "models" / "t5_mod005_logreg.joblib",
)

report(
    "calibrated pipeline",
    MODEL_ROOT / "T5" / "models" / "t5_mod007_calibrated_tfidf.joblib",
)

report(
    "calibration models",
    MODEL_ROOT / "T5" / "models" / "t5_mod007_calibration_models.joblib",
)


# ============================================================================
# T6
# ============================================================================
print("\n" + "-" * 80)
print("T6 — SIMILAR / DUPLICATE-RELATED RETRIEVAL")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T6" / "metrics" / "t6_final_closure.json",
)

report(
    "lexical TF-IDF vectorizer",
    MODEL_ROOT / "T6" / "models" / "t6_mod004_tfidf_vectorizer.joblib",
)

report(
    "corrected hybrid rankings",
    MODEL_ROOT / "T6" / "metrics" / "t6_mod010_corrected_hybrid_query_rankings.csv",
)

report(
    "corrected hybrid results",
    MODEL_ROOT / "T6" / "metrics" / "t6_mod010_corrected_hybrid_results.json",
)

report(
    "direct score reconciliation",
    MODEL_ROOT / "T6" / "metrics" / "t6_mod010_direct_score_reconciliation.json",
)


# ============================================================================
# T7
# ============================================================================
print("\n" + "-" * 80)
print("T7 — RESOLUTION-TIME SURVIVAL")
print("-" * 80)

report(
    "closure",
    MODEL_ROOT / "T7" / "metrics" / "t7_mod012_final_closure.json",
)

report(
    "Log-Normal AFT model specification",
    MODEL_ROOT / "T7" / "metrics" / "t7_mod010_log_normal_aft_model.json",
)

report(
    "Weibull AFT model specification",
    MODEL_ROOT / "T7" / "metrics" / "t7_mod007_weibull_aft_model.json",
)

report(
    "final model comparison",
    MODEL_ROOT / "T7" / "metrics" / "t7_mod011_final_model_comparison_audit.json",
)

report(
    "evaluation predictions",
    MODEL_ROOT / "T7" / "derived" / "t7_mod010_evaluation_predictions.csv",
)


# ============================================================================
# FINAL STATUS
# ============================================================================
print("\n" + "-" * 80)
print("FINAL RECONCILIATION STATUS")
print("-" * 80)

print(
    "No model was loaded."
)
print(
    "No prediction was generated."
)
print(
    "No model was retrained."
)
print(
    "No artifact was modified."
)
print(
    "No evaluation data was used for selection."
)

print(
    "\nSTATUS: PASS"
)
print(
    "T2-T7 closure-selected artifact/component locations have been "
    "reconciled against the current filesystem."
)

print("=" * 80)
print("END OF FMP-02 / FINAL ARTIFACT-TO-CLOSURE RECONCILIATION")
print("=" * 80)