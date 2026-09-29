import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# T3-VIZ-001
# Final T3 Visualization
# ============================================================

PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

VALIDATION_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_class_weighted_validation_metrics.json"
)

TEST_PATH = (
    PROJECT_ROOT
    / "modeling/T3/metrics/"
      "t3_final_test_metrics.json"
)

GENERALIZATION_PATH = (
    PROJECT_ROOT
    / "modeling/T3/analysis/"
      "t3_final_generalization_analysis.json"
)

PLOTS_DIR = (
    PROJECT_ROOT
    / "modeling/T3/plots"
)

MANIFEST_PATH = (
    PLOTS_DIR
    / "t3_visualization_manifest.json"
)

LABELS = ["S1", "S2", "S3", "S4"]


# ============================================================
# Load existing evidence
# ============================================================

print("T3_VIZ_001_START")

with open(VALIDATION_PATH, encoding="utf-8") as f:
    validation = json.load(f)

with open(TEST_PATH, encoding="utf-8") as f:
    test = json.load(f)

with open(GENERALIZATION_PATH, encoding="utf-8") as f:
    generalization = json.load(f)

PLOTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 1. Validation vs Test metrics
# ============================================================

metrics = [
    "Accuracy",
    "Macro F1",
    "Weighted F1",
]

validation_values = [
    validation["accuracy"],
    validation["macro_f1"],
    validation["weighted_f1"],
]

test_values = [
    test["accuracy"],
    test["macro_f1"],
    test["weighted_f1"],
]

x = np.arange(len(metrics))
width = 0.35

plt.figure(figsize=(9, 6))

plt.bar(
    x - width / 2,
    validation_values,
    width,
    label="Validation",
)

plt.bar(
    x + width / 2,
    test_values,
    width,
    label="Locked Test",
)

plt.xticks(x, metrics)
plt.ylabel("Score")
plt.ylim(0, 1)
plt.title(
    "T3 — Validation vs Locked Test Performance"
)
plt.legend()
plt.tight_layout()

plot1 = PLOTS_DIR / "t3_validation_vs_test.png"
plt.savefig(plot1, dpi=200)
plt.close()


# ============================================================
# 2. Locked Test per-class F1
# ============================================================

test_f1 = [
    test["per_class"][label]["f1"]
    for label in LABELS
]

plt.figure(figsize=(8, 6))

plt.bar(
    LABELS,
    test_f1,
)

plt.ylabel("F1 Score")
plt.ylim(0, 1)
plt.xlabel("Severity")
plt.title(
    "T3 — Locked Test Per-Class F1"
)
plt.tight_layout()

plot2 = PLOTS_DIR / "t3_test_per_class_f1.png"
plt.savefig(plot2, dpi=200)
plt.close()


# ============================================================
# 3. Locked Test confusion matrix
# ============================================================

cm = np.array(
    test["confusion_matrix"],
    dtype=int,
)

plt.figure(figsize=(8, 7))

plt.imshow(cm)

plt.colorbar(
    label="Number of Tickets"
)

plt.xticks(
    np.arange(len(LABELS)),
    LABELS,
)

plt.yticks(
    np.arange(len(LABELS)),
    LABELS,
)

plt.xlabel("Predicted Severity")
plt.ylabel("Actual Severity")

plt.title(
    "T3 — Locked Test Confusion Matrix"
)

for i in range(len(LABELS)):
    for j in range(len(LABELS)):
        plt.text(
            j,
            i,
            str(cm[i, j]),
            ha="center",
            va="center",
        )

plt.tight_layout()

plot3 = (
    PLOTS_DIR
    / "t3_test_confusion_matrix.png"
)

plt.savefig(plot3, dpi=200)
plt.close()


# ============================================================
# 4. True vs Predicted class distribution
# ============================================================

true_counts = [
    test["true_counts"][label]
    for label in LABELS
]

predicted_counts = [
    test["prediction_counts"][label]
    for label in LABELS
]

x = np.arange(len(LABELS))

plt.figure(figsize=(9, 6))

plt.bar(
    x - width / 2,
    true_counts,
    width,
    label="True",
)

plt.bar(
    x + width / 2,
    predicted_counts,
    width,
    label="Predicted",
)

plt.xticks(x, LABELS)
plt.ylabel("Number of Tickets")
plt.xlabel("Severity")
plt.title(
    "T3 — Locked Test True vs Predicted Distribution"
)
plt.legend()
plt.tight_layout()

plot4 = (
    PLOTS_DIR
    / "t3_test_true_vs_predicted_distribution.png"
)

plt.savefig(plot4, dpi=200)
plt.close()


# ============================================================
# Manifest
# ============================================================

manifest = {
    "operation": "T3-VIZ-001",
    "task": "T3_SEVERITY_PREDICTION",

    "source_artifacts": [
        str(VALIDATION_PATH),
        str(TEST_PATH),
        str(GENERALIZATION_PATH),
    ],

    "plots": [
        str(plot1),
        str(plot2),
        str(plot3),
        str(plot4),
    ],

    "visualizations": [
        "validation_vs_locked_test_metrics",
        "locked_test_per_class_f1",
        "locked_test_confusion_matrix",
        "locked_test_true_vs_predicted_distribution",
    ],

    "modeling_performed": False,
    "training_performed": False,
    "test_selection_performed": False,
    "raw_mozilla_accessed": False,
    "dataset_modified": False,

    "status": "VISUALIZATION_COMPLETE",
}

with open(
    MANIFEST_PATH,
    "w",
    encoding="utf-8",
) as f:
    json.dump(
        manifest,
        f,
        indent=2,
    )


print(f"PLOT_1={plot1}")
print(f"PLOT_2={plot2}")
print(f"PLOT_3={plot3}")
print(f"PLOT_4={plot4}")
print(f"MANIFEST={MANIFEST_PATH}")

print("TRAINING_PERFORMED=False")
print("TEST_SELECTION_PERFORMED=False")
print("RAW_MOZILLA_ACCESSED=False")
print("DATASET_MODIFIED=False")
print("STATUS=VISUALIZATION_COMPLETE")
print("T3_VIZ_001_COMPLETE")