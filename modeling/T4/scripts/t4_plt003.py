from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-003 — Final BM25 Ranking Metrics
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt003_ranking_metrics.png"


# ------------------------------------------------------------
# Completed T4-MOD-011 full BM25 evaluation results
# ------------------------------------------------------------

metrics = {
    "MRR": 0.266392,
    "NDCG@5": 0.275642,
    "NDCG@10": 0.291126,
}


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

names = list(metrics.keys())
values = list(metrics.values())

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    names,
    values,
)

for bar, value in zip(bars, values):
    ax.annotate(
        f"{value:.4f}",
        (
            bar.get_x() + bar.get_width() / 2,
            value,
        ),
        xytext=(0, 7),
        textcoords="offset points",
        ha="center",
        fontsize=10,
    )


ax.set_title(
    "T4 — Final BM25 Ranking Metrics",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Ranking Metric")
ax.set_ylabel("Score")

ax.set_ylim(0, 0.35)

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
print("T4 PLT-003 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-011 full BM25 evaluation")

print("MRR=0.266392")
print("NDCG@5=0.275642")
print("NDCG@10=0.291126")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)