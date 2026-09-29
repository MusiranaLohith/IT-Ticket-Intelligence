from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# T4 PLT-008 — True-Assignee Retrieval Position Distribution
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt008_retrieval_position_distribution.png"


# ------------------------------------------------------------
# Completed T4-MOD-012 retrieval evidence analysis
#
# Counts are for the covered evaluation population:
# 32,773 rows whose target assignee was observed in training.
# ------------------------------------------------------------

positions = list(range(1, 21))

mod007_counts = [
    7275,
    2123,
    911,
    736,
    564,
    422,
    362,
    294,
    238,
    239,
    233,
    210,
    187,
    200,
    186,
    179,
    164,
    162,
    140,
    167,
]

bm25_counts = [
    7405,
    2182,
    1052,
    674,
    574,
    449,
    394,
    285,
    307,
    270,
    250,
    246,
    211,
    202,
    189,
    165,
    187,
    164,
    153,
    154,
]

mod007_not_retrieved = 17781
bm25_not_retrieved = 17260


# ------------------------------------------------------------
# Convert counts to percentages
# ------------------------------------------------------------

mod007_total = sum(mod007_counts) + mod007_not_retrieved
bm25_total = sum(bm25_counts) + bm25_not_retrieved

mod007_percentages = [
    count / mod007_total * 100
    for count in mod007_counts
]

bm25_percentages = [
    count / bm25_total * 100
    for count in bm25_counts
]


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(11, 6))

x = np.arange(1, 21)

ax.plot(
    x,
    mod007_percentages,
    marker="o",
    linewidth=2,
    label="MOD-007 TF-IDF",
)

ax.plot(
    x,
    bm25_percentages,
    marker="o",
    linewidth=2,
    label="MOD-011 BM25",
)


ax.set_title(
    "T4 — True-Assignee Retrieval Position Distribution",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel(
    "Position of true historical assignee in Top-20 retrieval"
)

ax.set_ylabel(
    "Covered evaluation rows (%)"
)

ax.set_xticks(range(1, 21))

ax.grid(
    axis="both",
    linestyle="--",
    alpha=0.25,
)

ax.legend()

fig.tight_layout()

fig.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


# ------------------------------------------------------------
# Verification
# ------------------------------------------------------------

print("=" * 70)
print("T4 PLT-008 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-012 retrieval evidence analysis")

print("COVERED_EVALUATION_ROWS=32773")

print(
    f"MOD007_RETRIEVED_TOP20="
    f"{sum(mod007_counts)}"
)

print(
    f"MOD007_NOT_RETRIEVED="
    f"{mod007_not_retrieved}"
)

print(
    f"BM25_RETRIEVED_TOP20="
    f"{sum(bm25_counts)}"
)

print(
    f"BM25_NOT_RETRIEVED="
    f"{bm25_not_retrieved}"
)

print("MOD007_TOP20_COVERAGE=0.457450")
print("BM25_TOP20_COVERAGE=0.473347")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)