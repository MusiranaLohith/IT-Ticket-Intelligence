from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-007 — Historical Assignee Support Distribution
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt007_assignee_support_distribution.png"


# ------------------------------------------------------------
# Completed T4-MOD-003 validation results
# ------------------------------------------------------------

support_categories = [
    "Singleton\n(1)",
    "≤5",
    "≤10",
    "≤20",
    "21+",
]

assignee_counts = [
    2015,
    3234,
    3636,
    3934,
    4809 - 3934,
]


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    support_categories,
    assignee_counts,
)

for bar, count in zip(bars, assignee_counts):
    ax.annotate(
        f"{count:,}",
        (
            bar.get_x() + bar.get_width() / 2,
            count,
        ),
        xytext=(0, 7),
        textcoords="offset points",
        ha="center",
        fontsize=10,
    )


ax.set_title(
    "T4 — Historical Assignee Support Distribution",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel(
    "Historical support threshold"
)

ax.set_ylabel(
    "Number of distinct assignees"
)

ax.set_ylim(0, 5200)

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
print("T4 PLT-007 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-003 validation results")

print("DISTINCT_ASSIGNEES=4809")
print("SINGLETON_ASSIGNEES=2015")
print("ASSIGNEES_SUPPORT_LE_5=3234")
print("ASSIGNEES_SUPPORT_LE_10=3636")
print("ASSIGNEES_SUPPORT_LE_20=3934")
print("MEDIAN_SUPPORT=2")
print("MAX_SUPPORT=2917")

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)