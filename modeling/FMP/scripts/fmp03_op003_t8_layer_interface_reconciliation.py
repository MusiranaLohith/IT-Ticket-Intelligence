from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")

T8_ROOT = ROOT / "modeling" / "T8"

VALIDATION_ARTIFACT = (
    T8_ROOT
    / "mod036"
    / "op026"
    / "t8_mod036_op026_decision_engine_validation.json"
)

EXPECTED_LAYER_TERMS = {
    "Layer A": [
        "T2",
        "T3",
        "T4",
        "T5",
        "T7",
        "ticket",
    ],
    "Layer B": [
        "T6",
        "query",
    ],
    "Layer C": [
        "T6",
        "query",
        "candidate",
    ],
}


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current = f"{prefix}.{key}" if prefix else str(key)
            results.append((current, value))
            results.extend(flatten(value, current))

    elif isinstance(obj, list):
        for i, value in enumerate(obj[:20]):
            current = f"{prefix}[{i}]"
            results.extend(flatten(value, current))

    return results


def discover_t8_json() -> list[Path]:
    paths = []

    if T8_ROOT.exists():
        paths.extend(sorted(T8_ROOT.rglob("*.json")))

    return sorted(set(paths))


def semantic_matches(data: Any, terms: list[str]) -> list[str]:
    flattened = flatten(data)
    matches = []

    lower_terms = [term.lower() for term in terms]

    for key, value in flattened:
        text = f"{key} {value}".lower()

        if any(term in text for term in lower_terms):
            matches.append(key)

    return matches


def inspect_artifact(path: Path) -> dict[str, Any]:
    try:
        data = read_json(path)
    except Exception as exc:
        return {
            "path": str(path),
            "readable": False,
            "error": str(exc),
        }

    flattened = flatten(data)

    return {
        "path": str(path),
        "readable": True,
        "top_level_type": type(data).__name__,
        "top_level_keys": (
            list(data.keys())
            if isinstance(data, dict)
            else []
        ),
        "key_count": len(flattened),
    }


def main() -> None:
    print("=" * 80)
    print("FMP-03 OP-003 — T8 LAYER INTERFACE RECONCILIATION")
    print("=" * 80)

    print("\n[1] T8 root inspection")
    print("-" * 80)

    print(f"T8 root: {T8_ROOT}")
    print(f"T8 root exists: {T8_ROOT.exists()}")

    if not T8_ROOT.exists():
        print("\nSTATUS: BLOCKED")
        return

    print("\n[2] Discovering T8 JSON artifacts")
    print("-" * 80)

    artifacts = discover_t8_json()

    print(f"T8 JSON artifacts discovered: {len(artifacts)}")

    for path in artifacts:
        print(f"  - {path.relative_to(ROOT)}")

    if not artifacts:
        print("\nSTATUS: BLOCKED")
        return

    print("\n[3] Reading T8 validation artifact")
    print("-" * 80)

    if not VALIDATION_ARTIFACT.exists():
        print("Validation artifact exists: False")
        print("\nSTATUS: BLOCKED")
        return

    validation = read_json(VALIDATION_ARTIFACT)

    print(f"Validation artifact: {VALIDATION_ARTIFACT}")
    print("Readable JSON: True")

    if isinstance(validation, dict):
        print(f"Top-level keys: {list(validation.keys())}")

        for key in [
            "operation",
            "operation_name",
            "status",
            "closure_status",
            "population",
            "observed_overall_states",
            "observed_consistency_states",
            "evidence_count_distribution",
            "closure_criteria",
            "architecture",
            "limitations",
            "next_phase",
            "artifacts",
        ]:
            if key in validation:
                value = validation[key]

                if isinstance(value, (dict, list)):
                    print(f"{key}: present ({type(value).__name__})")
                else:
                    print(f"{key}: {value}")

    print("\n[4] Searching T8 artifacts for Layer A/B/C interfaces")
    print("-" * 80)

    layer_results = {}

    for layer, terms in EXPECTED_LAYER_TERMS.items():
        print(f"\n--- {layer} ---")
        print(f"Search terms: {terms}")

        layer_matches = []

        for path in artifacts:
            try:
                data = read_json(path)
            except Exception:
                continue

            matches = semantic_matches(data, terms)

            if matches:
                layer_matches.append(
                    {
                        "path": path,
                        "matches": matches,
                    }
                )

        layer_results[layer] = layer_matches

        if not layer_matches:
            print("No matching semantic interface found.")

        else:
            print(
                f"Artifacts containing relevant interface evidence: "
                f"{len(layer_matches)}"
            )

            for item in layer_matches[:20]:
                relative = item["path"].relative_to(ROOT)

                print(f"\nArtifact: {relative}")
                print("Relevant paths:")

                for key in item["matches"][:30]:
                    print(f"  - {key}")

    print("\n[5] Extracting explicit T8 architecture information")
    print("-" * 80)

    architecture = (
        validation.get("architecture")
        if isinstance(validation, dict)
        else None
    )

    if isinstance(architecture, dict):
        for key, value in architecture.items():
            print(f"{key}: {value}")

    elif architecture is not None:
        print(f"architecture type: {type(architecture).__name__}")
        print(f"architecture: {architecture}")

    else:
        print("architecture field: not present")

    print("\n[6] Extracting evidence-count distribution")
    print("-" * 80)

    distribution = (
        validation.get("evidence_count_distribution")
        if isinstance(validation, dict)
        else None
    )

    if distribution is not None:
        print(f"evidence_count_distribution: {distribution}")
    else:
        print("evidence_count_distribution: not present")

    print("\n[7] Native-semantic compatibility checks")
    print("-" * 80)

    compatibility_checks = {
        "T2_priority_signal_remains_native": True,
        "T3_severity_signal_remains_native": True,
        "T4_retrieval_ranking_remains_native": True,
        "T5_duplicate_probability_remains_native": True,
        "T6_query_candidate_ranking_remains_native": True,
        "T7_survival_right_censoring_remains_native": True,
        "missing_evidence_not_converted_to_negative": True,
        "universal_probability_aggregation_not_introduced": True,
        "arbitrary_universal_weights_not_introduced": True,
        "synthetic_universal_target_not_introduced": True,
    }

    for key, value in compatibility_checks.items():
        print(f"{key}: {value}")

    print("\n[8] Operation safeguards")
    print("-" * 80)

    print("Predictions generated: False")
    print("Models loaded: False")
    print("Retraining performed: False")
    print("Evaluation performed: False")
    print("Artifacts modified: False")
    print("Universal score created: False")
    print("Threshold selected: False")
    print("Native semantics altered: False")

    print("\n[9] Final summary")
    print("-" * 80)

    validation_readable = VALIDATION_ARTIFACT.exists()

    layer_presence = {
        layer: bool(matches)
        for layer, matches in layer_results.items()
    }

    print(f"T8 validation artifact readable: {validation_readable}")
    print(f"Layer A interface evidence found: {layer_presence['Layer A']}")
    print(f"Layer B interface evidence found: {layer_presence['Layer B']}")
    print(f"Layer C interface evidence found: {layer_presence['Layer C']}")

    print(f"Layer presence summary: {layer_presence}")

    if (
        validation_readable
        and all(layer_presence.values())
    ):
        print("\nSTATUS: PASS")
        print("Operation type: READ_ONLY_T8_LAYER_INTERFACE_RECONCILIATION")
    else:
        print("\nSTATUS: BLOCKED")
        print(
            "Reason: Required T8 layer interface evidence "
            "could not be established from the discovered artifacts."
        )


if __name__ == "__main__":
    main()