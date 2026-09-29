from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# T4 PLT-001 — Overall Top-K Model Comparison
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt001_model_comparison.png"


# Completed T4 results
metrics = {
    "R1 LinearSVC": {
        "Hit@1": 0.281059,
        "Hit@3": 0.363527,
        "Hit@5": 0.401926,
        "Hit@10": 0.450065,
    },
    "MOD-007 TF-IDF Retrieval": {
        "Hit@1": 0.257902,
        "Hit@3": 0.323191,
        "Hit@5": 0.352973,
        "Hit@10": 0.393084,
    },
    "MOD-008 Word+Char Retrieval": {
        "Hit@1": 0.213355,
        "Hit@3": 0.303206,
        "Hit@5": 0.336777,
        "Hit@10": 0.382109,
    },
    "MOD-011 BM25": {
        "Hit@1": 0.207854,
        "Hit@3": 0.298630,
        "Hit@5": 0.333661,
        "Hit@10": 0.381519,
    },
}


top_k = ["Hit@1", "Hit@3", "Hit@5", "Hit@10"]

x = np.arange(len(top_k))
width = 0.19


fig, ax = plt.subplots(figsize=(10, 6))

for index, (model_name, values) in enumerate(metrics.items()):
    scores = [values[k] * 100 for k in top_k]

    offset = (index - 1.5) * width

    ax.bar(
        x + offset,
        scores,
        width,
        label=model_name,
    )


ax.set_title(
    "T4 — Overall Top-K Comparison",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Ranking Metric")
ax.set_ylabel("Score (%)")

ax.set_xticks(x)
ax.set_xticklabels(top_k)

ax.set_ylim(0, 50)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.25,
)

ax.legend(
    loc="upper left",
    fontsize=9,
)

fig.tight_layout()

fig.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight",
)

plt.close(fig)


print("=" * 70)
print("T4 PLT-001 COMPLETE")
print("=" * 70)
print(f"OUTPUT={OUTPUT_PATH}")
print("SOURCE=Completed T4 modeling results")
print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")
print("=" * 70)