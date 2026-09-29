from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-002 — Final BM25 Hit@K Curve
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt002_bm25_hit_at_k.png"


# ------------------------------------------------------------
# Completed T4-MOD-011 full BM25 evaluation results
# ------------------------------------------------------------

k_values = [1, 3, 5, 10, 20]

hit_at_k = [
    0.207854,
    0.298630,
    0.333661,
    0.381519,
    0.435440,
]


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(9, 6))

ax.plot(
    k_values,
    [value * 100 for value in hit_at_k],
    marker="o",
    linewidth=2,
)

# Annotate every measured point
for k, value in zip(k_values, hit_at_k):
    ax.annotate(
        f"{value * 100:.2f}%",
        (k, value * 100),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=9,
    )


ax.set_title(
    "T4 — Final BM25 Hit@K",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("K")
ax.set_ylabel("Hit@K (%)")

ax.set_xticks(k_values)
ax.set_ylim(0, 50)

ax.grid(
    axis="both",
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
print("T4 PLT-002 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-011 full BM25 evaluation")
print("EVALUATION_ROWS=35626")

print("HIT@1=0.207854")
print("HIT@3=0.298630")
print("HIT@5=0.333661")
print("HIT@10=0.381519")
print("HIT@20=0.435440")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)