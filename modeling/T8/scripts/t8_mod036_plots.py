from pathlib import Path
import json

import matplotlib.pyplot as plt


PROJECT_ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

MOD036_ROOT = PROJECT_ROOT / "modeling" / "T8" / "mod036"

OP024_JSON = (
    MOD036_ROOT
    / "op024"
    / "t8_mod036_op024_decision_input_composition.json"
)

OP025_JSON = (
    MOD036_ROOT
    / "op025"
    / "t8_mod036_op025_decision_engine_composition.json"
)

PLOT_DIR = MOD036_ROOT / "plots"


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"Required artifact not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_bar_chart(
    labels,
    values,
    title,
    axis_label,
    output_path,
    horizontal=False,
):
    fig, ax = plt.subplots(figsize=(10, 6))

    if horizontal:
        bars = ax.barh(labels, values)
        ax.invert_yaxis()
        ax.set_xlabel(axis_label)
        ax.set_ylabel("")
    else:
        bars = ax.bar(labels, values)
        ax.set_ylabel(axis_label)
        ax.set_xlabel("")

    ax.set_title(title)

    for bar, value in zip(bars, values):
        if horizontal:
            ax.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                f" {value:,}",
                va="center",
                ha="left",
            )
        else:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:,}",
                ha="center",
                va="bottom",
            )

    if horizontal:
        ax.grid(axis="x", alpha=0.25)
    else:
        ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    op024 = load_json(OP024_JSON)
    op025 = load_json(OP025_JSON)

    # =========================================================
    # 1. Evidence availability by component
    # =========================================================

    component_availability = op025["component_availability"]

    availability_labels = [
        "Priority",
        "Assignment",
        "Duplicate",
        "Resolution",
    ]

    availability_values = [
        component_availability["priority"],
        component_availability["assignment"],
        component_availability["duplicate"],
        component_availability["resolution"],
    ]

    save_bar_chart(
        labels=availability_labels,
        values=availability_values,
        title="T8 Evidence Availability by Decision Component",
        axis_label="Rows with available native evidence",
        output_path=PLOT_DIR / "t8_evidence_availability.png",
    )

    # =========================================================
    # 2. Evidence-count distribution
    #
    # OP-025 does not store an explicit count distribution.
    # It stores evidence patterns. Therefore derive the count
    # directly from the recorded evidence-pattern populations.
    # =========================================================

    evidence_patterns = op025["evidence_patterns"]

    evidence_count_distribution = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
    }

    for pattern, count in evidence_patterns.items():
        component_count = len(pattern.split("|"))
        evidence_count_distribution[component_count] += count

    count_labels = [
        "1 component",
        "2 components",
        "3 components",
        "4 components",
    ]

    count_values = [
        evidence_count_distribution[1],
        evidence_count_distribution[2],
        evidence_count_distribution[3],
        evidence_count_distribution[4],
    ]

    save_bar_chart(
        labels=count_labels,
        values=count_values,
        title="T8 Evidence-Count Distribution",
        axis_label="Number of decision-engine cases",
        output_path=PLOT_DIR / "t8_evidence_count.png",
    )

    # =========================================================
    # 3. Evidence-pattern distribution
    # =========================================================

    pattern_items = sorted(
        evidence_patterns.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    pattern_labels = [
        pattern.replace("|", " + ")
        for pattern, _ in pattern_items
    ]

    pattern_values = [
        count
        for _, count in pattern_items
    ]

    save_bar_chart(
        labels=pattern_labels,
        values=pattern_values,
        title="T8 Evidence-Pattern Distribution",
        axis_label="Number of cases",
        output_path=PLOT_DIR / "t8_evidence_patterns.png",
        horizontal=True,
    )

    # =========================================================
    # 4. Overall decision-state distribution
    # =========================================================

    overall_states = op025["overall_evidence_states"]

    state_labels = [
        "SUPPORTED",
        "INSUFFICIENT_EVIDENCE",
        "CONFLICTING",
        "UNAVAILABLE",
    ]

    state_values = [
        overall_states["SUPPORTED"],
        overall_states["INSUFFICIENT_EVIDENCE"],
        overall_states["CONFLICTING"],
        overall_states["UNAVAILABLE"],
    ]

    save_bar_chart(
        labels=state_labels,
        values=state_values,
        title="T8 Decision-State Distribution",
        axis_label="Number of cases",
        output_path=PLOT_DIR / "t8_decision_states.png",
        horizontal=True,
    )

    # =========================================================
    # Validation of derived evidence counts
    # =========================================================

    union_rows = op025["population"]["union_rows"]

    derived_total = sum(evidence_count_distribution.values())

    if derived_total != union_rows:
        raise RuntimeError(
            "Evidence-pattern counts do not sum to the T8 union population: "
            f"{derived_total} != {union_rows}"
        )

    # =========================================================
    # Final output
    # =========================================================

    print("T8 documentation plotting: PASS")
    print()

    print(f"Decision-engine population: {union_rows:,}")
    print(
        "Derived evidence-count distribution:"
    )

    for component_count in range(1, 5):
        print(
            f"  {component_count} component(s): "
            f"{evidence_count_distribution[component_count]:,}"
        )

    print()
    print("Generated plots:")

    for path in sorted(PLOT_DIR.glob("t8_*.png")):
        print(f"  {path}")

    print()
    print("Source artifacts:")
    print(f"  {OP024_JSON}")
    print(f"  {OP025_JSON}")

    print()
    print(
        "These are documentation/visualization artifacts only. "
        "T8 modeling and closure artifacts were not modified."
    )


if __name__ == "__main__":
    main()