from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T9_ROOT = PROJECT_ROOT / "modeling" / "T9"
OUTPUT_DIR = T9_ROOT / "mod037"

OP004 = OUTPUT_DIR / "t9_mod037_op004_native_output_acceptance.json"
OP005 = OUTPUT_DIR / "t9_mod037_op005_output_semantics_lock.json"
OP011A = OUTPUT_DIR / "t9_mod037_op011a_t4_prior_artifact_schema.json"

OP020 = (
    PROJECT_ROOT
    / "modeling"
    / "T8"
    / "mod036"
    / "op020"
    / "t8_mod036_op020_assignment_component_baseline.json"
)

OUTPUT = (
    OUTPUT_DIR
    / "t9_mod037_op011b_prior_value_resolution.json"
)


def load(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def summarize(value, depth=0, max_depth=4):
    if depth > max_depth:
        return "<max-depth>"

    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            if isinstance(val, (dict, list)):
                result[key] = summarize(
                    val,
                    depth + 1,
                    max_depth,
                )
            else:
                result[key] = val
        return result

    if isinstance(value, list):
        if len(value) > 30:
            return {
                "type": "list",
                "length": len(value),
                "first_items": [
                    summarize(
                        x,
                        depth + 1,
                        max_depth,
                    )
                    for x in value[:10]
                ],
            }

        return [
            summarize(
                x,
                depth + 1,
                max_depth,
            )
            for x in value
        ]

    return value


def main():

    print("=" * 72)
    print("T9 MOD-037 OP-011B")
    print("Prior Artifact Value Resolution")
    print("=" * 72)
    print()

    artifacts = {
        "OP-004": load(OP004),
        "OP-005": load(OP005),
        "OP-011A": load(OP011A),
        "T8_OP-020": load(OP020),
    }

    for name, artifact in artifacts.items():

        print("=" * 72)
        print(name)
        print("=" * 72)

        print("Top-level keys:")
        for key in artifact.keys():
            print(f"  - {key}")

        print()

        if name == "OP-004":
            print("status:")
            print(artifact.get("status"))

            print()
            print("accepted_tasks:")
            print(artifact.get("accepted_tasks"))

            print()
            print("unavailable_tasks:")
            print(artifact.get("unavailable_tasks"))

        elif name == "OP-005":
            print("status:")
            print(artifact.get("status"))

            print()
            print("native_evaluation_tasks:")
            print(
                artifact.get(
                    "native_evaluation_tasks"
                )
            )

            print()
            print("task_boundary:")
            print(
                json.dumps(
                    artifact.get("task_boundary"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("global_control_validation:")
            print(
                json.dumps(
                    artifact.get(
                        "global_control_validation"
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        elif name == "OP-011A":
            print("status:")
            print(artifact.get("status"))

            print()
            print("Resolved schemas:")
            print(
                json.dumps(
                    artifact.get(
                        "schemas",
                        artifact,
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        elif name == "T8_OP-020":
            print("status:")
            print(artifact.get("status"))

            print()
            print("component:")
            print(
                json.dumps(
                    artifact.get("component"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("sources:")
            print(
                json.dumps(
                    artifact.get("sources"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("native_semantics:")
            print(
                json.dumps(
                    artifact.get(
                        "native_semantics"
                    ),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("alignment:")
            print(
                json.dumps(
                    artifact.get("alignment"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("metrics:")
            print(
                json.dumps(
                    artifact.get("metrics"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("outputs:")
            print(
                json.dumps(
                    artifact.get("outputs"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print()
            print("controls:")
            print(
                json.dumps(
                    artifact.get("controls"),
                    indent=2,
                    ensure_ascii=False,
                )
            )

    result = {
        "operation": "T9_MOD-037_OP-011B",
        "title": "Prior Artifact Value Resolution",
        "status": "PASS",
        "purpose": (
            "Resolve actual values and nested structures "
            "of prior T9/T8 artifacts before executing "
            "the corrected T4 native ranking evaluation."
        ),
        "artifacts": {
            name: summarize(artifact)
            for name, artifact in artifacts.items()
        },
    }

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 72)
    print("OP-011B: PASS")
    print("=" * 72)
    print()
    print("Output:")
    print(OUTPUT)


if __name__ == "__main__":
    main()