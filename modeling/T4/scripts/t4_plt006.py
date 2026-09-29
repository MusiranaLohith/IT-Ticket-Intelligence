from pathlib import Path

import matplotlib.pyplot as plt


# ============================================================
# T4 PLT-006 — Open-World Evaluation Population
# ============================================================

PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

OUTPUT_DIR = PROJECT_ROOT / "modeling" / "T4" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "t4_plt006_open_world.png"


# ------------------------------------------------------------
# Completed T4-MOD-004 chronological split results
# ------------------------------------------------------------

total_evaluation_rows = 35_626

training_observed_target_rows = 32_773
unseen_target_rows = 2_853


training_observed_percentage = (
    training_observed_target_rows / total_evaluation_rows * 100
)

unseen_percentage = (
    unseen_target_rows / total_evaluation_rows * 100
)


# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------

labels = [
    "Training-observed\ntarget",
    "Unseen target",
]

values = [
    training_observed_percentage,
    unseen_percentage,
]

fig, ax = plt.subplots(figsize=(8, 6))

bars = ax.bar(
    labels,
    values,
)

for bar, percentage, count in zip(
    bars,
    values,
    [
        training_observed_target_rows,
        unseen_target_rows,
    ],
):
    ax.annotate(
        f"{percentage:.2f}%\n(n={count:,})",
        (
            bar.get_x() + bar.get_width() / 2,
            percentage,
        ),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
        fontsize=10,
    )


ax.set_title(
    "T4 — Open-World Evaluation Population",
    fontsize=14,
    fontweight="bold",
)

ax.set_xlabel("Evaluation target status")
ax.set_ylabel("Evaluation rows (%)")

ax.set_ylim(0, 100)

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
print("T4 PLT-006 COMPLETE")
print("=" * 70)

print(f"OUTPUT={OUTPUT_PATH}")

print("SOURCE=T4-MOD-004 chronological split results")

print(f"EVALUATION_ROWS={total_evaluation_rows}")
print(
    f"TRAINING_OBSERVED_TARGET_ROWS="
    f"{training_observed_target_rows}"
)
print(
    f"UNSEEN_TARGET_ROWS="
    f"{unseen_target_rows}"
)
print(
    f"TRAINING_OBSERVED_PERCENTAGE="
    f"{training_observed_percentage:.6f}"
)
print(
    f"UNSEEN_TARGET_PERCENTAGE="
    f"{unseen_percentage:.6f}"
)

print("RAW_MOZILLA_ACCESSED=False")
print("MODEL_TRAINED=False")
print("NEW_EXPERIMENT=False")

print("=" * 70)