from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-005 — True-Assignee Top-20 Retrieval Coverage
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt005_retrieval_coverage.png"


# ------------------------------------------------------------
# Completed T4 retrieval-analysis results
# ------------------------------------------------------------

methods = [
    "MOD-007 TF-IDF",
    "MOD-011 BM25",
]

coverage = [
    0.457450,
    0.473347,
]


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 6))

bars = ax.bar(
    methods,
    [value * 100 for value in coverage],
)

for bar, value in zip(bars, coverage):
    ax.annotate(
        f"{value * 100:.2f}%",
        (
            bar.get_x() + bar.get_width() / 2,
            value * 100,
        ),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=10,
    )


ax.set_title(
    "T4 — True-Assignee Top-20 Retrieval Coverage",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Retrieval Method")
ax.set_ylabel("True-Assignee Coverage (%)")

ax.set_ylim(0, 60)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25,
)

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
print("T4 PLT-005 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-012 retrieval evidence analysis")

print("MOD007_TOP20_COVERAGE=0.457450")
print("BM25_TOP20_COVERAGE=0.473347")
print("DELTA=0.015897")
print("DELTA_PP=+1.5897")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)