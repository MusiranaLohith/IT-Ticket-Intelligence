#!/usr/bin/env python3

from __future__ import annotations

import inspect
import json
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

RUNTIME_ROOT = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "deployment"
    / "runtime"
)

METRICS_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "FMP"
    / "metrics"
)

REPORT_PATH = (
    METRICS_DIR
    / "deploy_op002_runtime_contract.json"
)


def json_safe(value):
    """
    Convert common NumPy/Pandas/scikit-learn values
    into JSON-safe representations without changing
    the runtime result itself.
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, dict):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            json_safe(v)
            for v in value
        ]

    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except Exception:
            pass

    if hasattr(value, "tolist"):
        try:
            return json_safe(value.tolist())
        except Exception:
            pass

    return {
        "__type__": type(value).__name__,
        "__repr__": repr(value),
    }


def structure_summary(value, path="root"):
    """
    Recursively describe the runtime output structure
    without changing the actual result.
    """

    if value is None:
        return {
            "path": path,
            "type": "NoneType",
        }

    if isinstance(value, dict):
        children = []

        for key, child in value.items():
            children.append(
                structure_summary(
                    child,
                    f"{path}.{key}",
                )
            )

        return {
            "path": path,
            "type": "dict",
            "keys": [str(k) for k in value.keys()],
            "children": children,
        }

    if isinstance(value, (list, tuple)):
        result = {
            "path": path,
            "type": type(value).__name__,
            "length": len(value),
        }

        if value:
            result["first_item"] = structure_summary(
                value[0],
                f"{path}[0]",
            )

        return result

    return {
        "path": path,
        "type": type(value).__name__,
        "value_preview": str(value)[:500],
    }


def callable_signature(obj, name):
    try:
        member = getattr(obj, name)
        return str(inspect.signature(member))
    except Exception as exc:
        return f"ERROR: {exc!r}"


def class_methods(cls):
    result = {}

    for name in sorted(dir(cls)):
        if name.startswith("_"):
            continue

        try:
            member = getattr(cls, name)

            if callable(member):
                try:
                    result[name] = str(
                        inspect.signature(member)
                    )
                except Exception:
                    result[name] = "<signature unavailable>"

        except Exception as exc:
            result[name] = f"<error: {exc!r}>"

    return result


def extract_ticket_requirements(ticket_pipeline_module):
    """
    Inspect source-level references to required ticket fields
    without modifying or executing model code.
    """

    source_path = (
        RUNTIME_ROOT
        / "ticket_pipeline.py"
    )

    source = source_path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    required_fields = []

    known_fields = [
        "ticket_id",
        "creation_time",
        "creator",
        "creator_detail",
        "summary",
        "description",
    ]

    for field in known_fields:
        if f'"{field}"' in source or f"'{field}'" in source:
            required_fields.append(field)

    return {
        "source_path": str(source_path),
        "known_fields_referenced": required_fields,
    }


def main():
    print("=" * 72)
    print("IT TICKET TRIAGE SYSTEM")
    print("DEPLOY-OP-002 — RUNTIME CONTRACT RECONCILIATION")
    print("=" * 72)

    print()
    print("[1] Runtime path")
    print(RUNTIME_ROOT)

    if not RUNTIME_ROOT.exists():
        raise SystemExit(
            "ERROR: deployment runtime directory does not exist."
        )

    sys.path.insert(
        0,
        str(RUNTIME_ROOT),
    )

    print()
    print("[2] Importing packaged runtime")

    import ticket_pipeline
    import ticket_explanation

    from ticket_pipeline import TicketPipeline
    from ticket_explanation import TicketExplanation

    print("  ticket_pipeline: PASS")
    print("  ticket_explanation: PASS")

    print()
    print("[3] Class signatures")

    pipeline_init = callable_signature(
        TicketPipeline,
        "__init__",
    )

    pipeline_predict = callable_signature(
        TicketPipeline,
        "predict",
    )

    pipeline_predict_batch = callable_signature(
        TicketPipeline,
        "predict_batch",
    )

    explanation_init = callable_signature(
        TicketExplanation,
        "__init__",
    )

    explanation_explain = callable_signature(
        TicketExplanation,
        "explain",
    )

    print("  TicketPipeline.__init__:", pipeline_init)
    print("  TicketPipeline.predict:", pipeline_predict)
    print(
        "  TicketPipeline.predict_batch:",
        pipeline_predict_batch,
    )
    print(
        "  TicketExplanation.__init__:",
        explanation_init,
    )
    print(
        "  TicketExplanation.explain:",
        explanation_explain,
    )

    print()
    print("[4] Public callable inventory")

    pipeline_methods = class_methods(
        TicketPipeline
    )

    explanation_methods = class_methods(
        TicketExplanation
    )

    for name, signature in pipeline_methods.items():
        print(
            f"  TicketPipeline.{name}{signature}"
        )

    print()

    for name, signature in explanation_methods.items():
        print(
            f"  TicketExplanation.{name}{signature}"
        )

    print()
    print("[5] Ticket field references")

    field_info = extract_ticket_requirements(
        ticket_pipeline
    )

    print(
        "  Fields referenced:",
        field_info["known_fields_referenced"],
    )

    print()
    print("[6] Constructing packaged TicketPipeline")

    pipeline = TicketPipeline()

    print("  TicketPipeline(): PASS")

    print()
    print("[7] Synthetic contract ticket")

    ticket = {
        "ticket_id": "DEPLOY-OP002-001",
        "creation_time": "2026-09-27T08:00:00",
        "creator": "contract-test-user",
        "creator_detail": "engineering",
        "summary": "VPN connection problem",
        "description": (
            "User cannot connect to the company VPN "
            "from the workstation."
        ),
    }

    print(
        json.dumps(
            ticket,
            indent=2,
        )
    )

    print()
    print("[8] Executing TicketPipeline.predict()")

    prediction = pipeline.predict(ticket)

    print("  predict(): PASS")

    print()
    print("[9] Raw result top-level structure")

    print(
        json.dumps(
            structure_summary(prediction),
            indent=2,
        )
    )

    print()
    print("[10] Raw result top-level keys")

    if isinstance(prediction, dict):
        print(
            "  ",
            list(prediction.keys()),
        )
    else:
        print(
            "  WARNING: prediction is not a dict:",
            type(prediction).__name__,
        )

    print()
    print("[11] T1–T11 inspection")

    task_summary = {}

    if isinstance(prediction, dict):

        tasks = prediction.get("tasks")

        if isinstance(tasks, dict):

            for task_name, task_value in tasks.items():

                if isinstance(task_value, dict):
                    task_info = {
                        "type": "dict",
                        "keys": [
                            str(k)
                            for k in task_value.keys()
                        ],
                    }

                    for key in [
                        "status",
                        "state",
                        "action",
                        "evidence_state",
                        "limitation",
                        "warning",
                    ]:
                        if key in task_value:
                            task_info[key] = json_safe(
                                task_value[key]
                            )

                    task_summary[str(task_name)] = task_info

                    print(
                        f"  {task_name}: "
                        f"{task_info}"
                    )

                else:
                    task_summary[str(task_name)] = {
                        "type": type(
                            task_value
                        ).__name__,
                        "value": json_safe(
                            task_value
                        ),
                    }

                    print(
                        f"  {task_name}: "
                        f"{json_safe(task_value)}"
                    )

        else:
            print(
                "  WARNING: prediction['tasks'] "
                "is not a dictionary."
            )

    print()
    print("[12] Final result inspection")

    final_result = None

    if isinstance(prediction, dict):
        final_result = prediction.get(
            "final"
        )

    print(
        json.dumps(
            json_safe(final_result),
            indent=2,
        )
    )

    print()
    print("[13] Integrity result inspection")

    integrity_result = None

    if isinstance(prediction, dict):
        integrity_result = prediction.get(
            "integrity"
        )

    print(
        json.dumps(
            json_safe(integrity_result),
            indent=2,
        )
    )

    print()
    print("[14] TicketExplanation")

    explanation = TicketExplanation()

    print("  TicketExplanation(): PASS")

    explanation_result = explanation.explain(
        prediction
    )

    print("  explain(): PASS")

    print()
    print("[15] Explanation output structure")

    print(
        json.dumps(
            structure_summary(
                explanation_result
            ),
            indent=2,
        )
    )

    print()
    print("[16] Explanation output")

    if isinstance(
        explanation_result,
        str,
    ):
        print(explanation_result)
    else:
        print(
            json.dumps(
                json_safe(
                    explanation_result
                ),
                indent=2,
            )
        )

    print()
    print("[17] JSON serialization test")

    try:
        serialized = json.dumps(
            json_safe(prediction),
            indent=2,
        )

        print(
            "  Pipeline result serialization: PASS"
        )

        serialized_length = len(serialized)

    except Exception as exc:
        print(
            "  Pipeline result serialization: FAIL"
        )
        print("  ERROR:", repr(exc))
        serialized_length = None

    try:
        explanation_serialized = json.dumps(
            json_safe(explanation_result),
            indent=2,
        )

        print(
            "  Explanation serialization: PASS"
        )

        explanation_serialized_length = len(
            explanation_serialized
        )

    except Exception as exc:
        print(
            "  Explanation serialization: FAIL"
        )
        print("  ERROR:", repr(exc))
        explanation_serialized_length = None

    print()
    print("[18] Contract report")

    report = {
        "operation": "DEPLOY-OP-002",
        "title": (
            "Runtime Contract Reconciliation"
        ),
        "timestamp": datetime.now().isoformat(),
        "read_only": True,
        "runtime_root": str(RUNTIME_ROOT),

        "interfaces": {
            "TicketPipeline": {
                "__init__": pipeline_init,
                "predict": pipeline_predict,
                "predict_batch": pipeline_predict_batch,
                "methods": pipeline_methods,
            },
            "TicketExplanation": {
                "__init__": explanation_init,
                "explain": explanation_explain,
                "methods": explanation_methods,
            },
        },

        "ticket_fields": field_info,

        "contract_ticket": ticket,

        "prediction_structure": structure_summary(
            prediction
        ),

        "prediction_top_level_keys": (
            list(prediction.keys())
            if isinstance(prediction, dict)
            else None
        ),

        "task_summary": task_summary,

        "final_result": json_safe(
            final_result
        ),

        "integrity_result": json_safe(
            integrity_result
        ),

        "explanation_structure": structure_summary(
            explanation_result
        ),

        "explanation_result": json_safe(
            explanation_result
        ),

        "serialization": {
            "pipeline_result": (
                "PASS"
                if serialized_length is not None
                else "FAIL"
            ),
            "pipeline_serialized_length": (
                serialized_length
            ),
            "explanation_result": (
                "PASS"
                if explanation_serialized_length
                is not None
                else "FAIL"
            ),
            "explanation_serialized_length": (
                explanation_serialized_length
            ),
        },
    }

    METRICS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(REPORT_PATH)

    print()
    print("=" * 72)
    print("DEPLOY-OP-002 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()