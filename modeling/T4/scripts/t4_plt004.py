from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-004 — Long-Tail Performance by Assignee Support
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt004_long_tail_performance.png"


# ------------------------------------------------------------
# Completed T4-MOD-011 full BM25 evaluation results
# ------------------------------------------------------------

support_buckets = [
    "1",
    "2–5",
    "6–10",
    "11–20",
    "21–50",
    "51–100",
    "101+",
]

hit_at_1 = [
    0.012208,
    0.029005,
    0.033188,
    0.186846,
    0.132994,
    0.230679,
    0.293375,
]

hit_at_5 = [
    0.031536,
    0.081619,
    0.075109,
    0.278027,
    0.256177,
    0.411241,
    0.450052,
]

hit_at_10 = [
    0.043744,
    0.100169,
    0.089083,
    0.310164,
    0.305596,
    0.471194,
    0.511491,
]

hit_at_20 = [
    0.052899,
    0.120067,
    0.120524,
    0.352018,
    0.361919,
    0.518267,
    0.584213,
]


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))

x = range(len(support_buckets))

ax.plot(
    x,
    [value * 100 for value in hit_at_1],
    marker="o",
    linewidth=2,
    label="Hit@1",
)

ax.plot(
    x,
    [value * 100 for value in hit_at_5],
    marker="o",
    linewidth=2,
    label="Hit@5",
)

ax.plot(
    x,
    [value * 100 for value in hit_at_10],
    marker="o",
    linewidth=2,
    label="Hit@10",
)

ax.plot(
    x,
    [value * 100 for value in hit_at_20],
    marker="o",
    linewidth=2,
    label="Hit@20",
)


ax.set_title(
    "T4 — Long-Tail Performance by Historical Assignee Support",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel(
    "Historical target-assignee support in training"
)

ax.set_ylabel(
    "Hit Rate (%)"
)

ax.set_xticks(list(x))
ax.set_xticklabels(support_buckets)

ax.set_ylim(0, 65)

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
print("T4 PLT-004 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-011 full BM25 evaluation")

print("SUPPORT_BUCKETS=1|2-5|6-10|11-20|21-50|51-100|101+")

print("HIT@1=0.012208|0.029005|0.033188|0.186846|0.132994|0.230679|0.293375")
print("HIT@5=0.031536|0.081619|0.075109|0.278027|0.256177|0.411241|0.450052")
print("HIT@10=0.043744|0.100169|0.089083|0.310164|0.305596|0.471194|0.511491")
print("HIT@20=0.052899|0.120067|0.120524|0.352018|0.361919|0.518267|0.584213")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)