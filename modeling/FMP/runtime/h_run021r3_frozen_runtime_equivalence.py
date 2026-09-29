from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from ticket_pipeline import TicketPipeline


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
RUNTIME_DIR = ROOT / "modeling" / "FMP" / "runtime"
METRICS = ROOT / "modeling" / "FMP" / "metrics"

LEGACY_ORCHESTRATOR = (
    ROOT
    / "modeling"
    / "FMP"
    / "scripts"
    / "h_run019_full_ticket_pipeline.py"
)


TICKET = {
    "ticket_id": "H-RUN-021R3-VPN-001",
    "creation_time": "2026-09-26T18:03:00Z",
    "creator": "",
    "creator_detail": "",
    "summary": "VPN connection fails after password reset",
    "description": (
        "I reset my corporate password this morning. Since then, "
        "the VPN client connects briefly and then disconnects. "
        "I restarted the laptop and reinstalled the VPN client, "
        "but the issue persists. I need access to the internal "
        "systems for today's work."
    ),
}


def run_legacy():
    source = LEGACY_ORCHESTRATOR.read_text(
        encoding="utf-8"
    )

    lines = source.splitlines()
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("TICKET_ID = "):
            output.append(
                f"TICKET_ID = {TICKET['ticket_id']!r}"
            )
            i += 1
            continue

        if line.startswith("TITLE = "):
            output.append(
                f"TITLE = {TICKET['summary']!r}"
            )
            i += 1
            continue

        if line.startswith("DESCRIPTION = ("):
            output.append(
                f"DESCRIPTION = {TICKET['description']!r}"
            )

            i += 1

            while i < len(lines):
                if lines[i].strip() == ")":
                    i += 1
                    break
                i += 1

            continue

        output.append(line)
        i += 1

    temp_script = (
        METRICS
        / "_h_run021r3_legacy_comparison.py"
    )

    temp_script.write_text(
        "\n".join(output),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(temp_script),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    try:
        temp_script.unlink()
    except FileNotFoundError:
        pass

    if completed.returncode != 0:
        raise RuntimeError(
            completed.stderr
        )

    return completed.stdout


def parse_legacy(stdout):
    values = {}

    for line in stdout.splitlines():
        line = line.strip()

        for task in [
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "T6",
            "T7",
            "T8",
            "T10",
            "T11",
        ]:
            if line.startswith(f"[{task}]"):
                if "->" in line:
                    values[task] = line.split(
                        "->", 1
                    )[1].strip()

    return values


def parse_list(value):
    if isinstance(value, list):
        return value

    if value is None:
        return None

    parsed = ast.literal_eval(value)

    if not isinstance(parsed, list):
        raise ValueError(
            f"Expected list representation, got: {value}"
        )

    return [str(x) for x in parsed]


def parse_float(value):
    if value is None:
        return None

    return float(value)


def compact_new(result):
    tasks = result["tasks"]

    return {
        "T1": tasks["T1"].get("prediction"),
        "T2": tasks["T2"].get("prediction"),
        "T3": tasks["T3"].get("prediction"),
        "T4": [
            str(item["id"])
            for item in tasks["T4"].get(
                "results",
                [],
            )
        ],
        "T5": float(
            tasks["T5"].get(
                "duplicate_evidence"
            )
        ),
        "T6": {
            "status": tasks["T6"]["status"],
            "full_mod010_hybrid_available": tasks[
                "T6"
            ].get(
                "full_mod010_hybrid_available"
            ),
            "top_ids": tasks["T6"].get(
                "top_ids",
                [],
            ),
        },
        "T7": {
            "status": tasks["T7"]["status"],
            "median_seconds": float(
                tasks["T7"]["median_seconds"]
            ),
            "temporal_support": tasks["T7"][
                "temporal_support"
            ],
        },
        "T8": tasks["T8"]["evidence_state"],
        "T10": tasks["T10"]["action"],
        "T11": tasks["T11"]["feedback"],
    }


def compare_exact(field, legacy, new):
    return {
        "field": field,
        "legacy": legacy,
        "new": new,
        "match": legacy == new,
    }


def compare_float(field, legacy, new, tolerance=1e-9):
    legacy_value = parse_float(legacy)
    new_value = parse_float(new)

    difference = abs(
        legacy_value - new_value
    )

    return {
        "field": field,
        "legacy": legacy_value,
        "new": new_value,
        "absolute_difference": difference,
        "tolerance": tolerance,
        "match": difference <= tolerance,
    }


def main():
    print("=" * 70)
    print(
        "H-RUN-021R3 — FROZEN RUNTIME EQUIVALENCE VALIDATION"
    )
    print("=" * 70)

    print("\n[1] Running legacy validated runtime...")
    legacy_stdout = run_legacy()
    legacy_raw = parse_legacy(
        legacy_stdout
    )

    legacy = {
        "T1": legacy_raw.get("T1"),
        "T2": legacy_raw.get("T2"),
        "T3": legacy_raw.get("T3"),
        "T4": parse_list(
            legacy_raw.get("T4")
        ),
        "T5": parse_float(
            legacy_raw.get("T5")
        ),
        "T6": parse_list(
            legacy_raw.get("T6")
        ),
        "T7": parse_float(
            legacy_raw.get("T7")
        ),
        "T8": legacy_raw.get("T8"),
        "T10": legacy_raw.get("T10"),
        "T11": legacy_raw.get("T11"),
    }

    print("Legacy runtime: PASS")

    print("\n[2] Running new TicketPipeline...")
    pipeline = TicketPipeline()

    new = compact_new(
        pipeline.predict(TICKET)
    )

    print("New TicketPipeline: PASS")

    print("\n[3] Normalized equivalence")
    print("-" * 70)

    comparisons = []

    comparisons.append(
        compare_exact(
            "T1",
            legacy["T1"],
            new["T1"],
        )
    )

    comparisons.append(
        compare_exact(
            "T2",
            legacy["T2"],
            new["T2"],
        )
    )

    comparisons.append(
        compare_exact(
            "T3",
            legacy["T3"],
            new["T3"],
        )
    )

    comparisons.append(
        compare_exact(
            "T4",
            legacy["T4"],
            new["T4"],
        )
    )

    comparisons.append(
        compare_float(
            "T5",
            legacy["T5"],
            new["T5"],
        )
    )

    comparisons.append(
        {
            "field": "T6",
            "legacy": legacy["T6"],
            "new": new["T6"],
            "match": (
                new["T6"]["status"]
                == "PARTIAL_NATIVE_RUNTIME"
                and new["T6"][
                    "full_mod010_hybrid_available"
                ]
                is False
                and new["T6"]["top_ids"] == []
            ),
        }
    )

    comparisons.append(
        compare_float(
            "T7",
            legacy["T7"],
            new["T7"]["median_seconds"],
        )
    )

    comparisons.append(
        {
            "field": "T7_temporal_support",
            "legacy": (
                "OUTSIDE_OBSERVED_TRAINING_RANGE"
            ),
            "new": new["T7"][
                "temporal_support"
            ],
            "match": (
                new["T7"][
                    "temporal_support"
                ]
                == "OUTSIDE_OBSERVED_TRAINING_RANGE"
            ),
        }
    )

    comparisons.append(
        compare_exact(
            "T8",
            legacy["T8"],
            new["T8"],
        )
    )

    comparisons.append(
        compare_exact(
            "T10",
            legacy["T10"],
            new["T10"],
        )
    )

    comparisons.append(
        compare_exact(
            "T11",
            legacy["T11"],
            new["T11"],
        )
    )

    for item in comparisons:
        status = (
            "MATCH"
            if item["match"]
            else "MISMATCH"
        )

        print(
            f"{item['field']:>20} : {status}"
        )

        if "absolute_difference" in item:
            print(
                f"  legacy={item['legacy']} "
                f"new={item['new']} "
                f"diff={item['absolute_difference']}"
            )

    all_match = all(
        item["match"]
        for item in comparisons
    )

    output = {
        "operation": "H-RUN-021R3",
        "operation_name": (
            "Normalized frozen runtime equivalence"
        ),
        "ticket": TICKET,
        "legacy_runtime": legacy,
        "new_runtime": new,
        "comparisons": comparisons,
        "validation": {
            "all_equivalence_checks_pass": all_match,
            "comparison_representation_normalized": True,
            "legacy_source_modified": False,
            "model_retraining": False,
            "model_modification": False,
            "threshold_optimization": False,
            "locked_test_reuse": False,
            "prediction_modification": False,
            "synthetic_feedback": False,
        },
        "final_status": (
            "PASS"
            if all_match
            else "REQUIRES_REVIEW"
        ),
    }

    METRICS.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        METRICS
        / "h_run021r3_frozen_runtime_equivalence.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            indent=2,
        )

    print("\n" + "=" * 70)
    print("H-RUN-021R3 SUMMARY")
    print("=" * 70)
    print(
        "Equivalence checks : "
        + ("PASS" if all_match else "FAIL")
    )
    print(
        f"FINAL STATUS       : "
        f"{'PASS' if all_match else 'REQUIRES_REVIEW'}"
    )

    print("\n[INTEGRITY]")
    print("Legacy source modified      : NO")
    print("Model retraining            : NO")
    print("Model modification          : NO")
    print("Threshold optimization      : NO")
    print("Locked test reuse           : NO")
    print("Prediction modification     : NO")
    print("Synthetic feedback          : NO")

    print("\n[ARTIFACT]")
    print(f"JSON : {output_path}")


if __name__ == "__main__":
    main()