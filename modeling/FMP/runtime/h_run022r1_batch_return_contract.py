from __future__ import annotations

import json
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent

if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from ticket_pipeline import TicketPipeline


TICKET = {
    "ticket_id": "DEV-CONTRACT-001",
    "creation_time": "2026-09-27T09:00:00+05:30",
    "creator": "",
    "creator_detail": "",
    "summary": "VPN disconnects after password reset",
    "description": (
        "I reset my corporate password this morning. "
        "The VPN connects briefly and then disconnects. "
        "I restarted the laptop and reinstalled the VPN client, "
        "but the issue persists."
    ),
}


def describe_object(name, obj):
    print()
    print("=" * 78)
    print(name)
    print("=" * 78)

    print("Python type:")
    print(type(obj))

    print()
    print("Representation:")
    print(repr(obj))

    if isinstance(obj, dict):
        print()
        print("Dictionary keys:")
        for key in obj.keys():
            print(f"  {key!r} -> {type(obj[key])}")

    elif isinstance(obj, list):
        print()
        print(f"List length: {len(obj)}")

        if obj:
            first = obj[0]

            print()
            print("First element type:")
            print(type(first))

            print()
            print("First element representation:")
            print(repr(first))

            if isinstance(first, dict):
                print()
                print("First element dictionary keys:")
                for key in first.keys():
                    print(f"  {key!r} -> {type(first[key])}")

            else:
                print()
                print("First element attributes:")
                attrs = [
                    name
                    for name in dir(first)
                    if not name.startswith("_")
                ]

                for attr in attrs[:100]:
                    try:
                        value = getattr(first, attr)
                        if not callable(value):
                            print(f"  {attr!r} -> {type(value)}")
                    except Exception:
                        pass

    else:
        print()
        print("Object attributes:")

        attrs = [
            name
            for name in dir(obj)
            if not name.startswith("_")
        ]

        for attr in attrs[:100]:
            try:
                value = getattr(obj, attr)
                if not callable(value):
                    print(f"  {attr!r} -> {type(value)}")
            except Exception:
                pass


def main():
    print("=" * 78)
    print("H-RUN-022R1 — BATCH RETURN CONTRACT INSPECTION")
    print("=" * 78)

    print()
    print("[1] Initializing TicketPipeline...")
    pipeline = TicketPipeline()
    print("TicketPipeline initialization: PASS")

    print()
    print("[2] Running predict() on one ticket...")
    single = pipeline.predict(TICKET)
    print("predict(): completed")

    describe_object("SINGLE predict() RESULT", single)

    print()
    print("[3] Running predict_batch() on the same ticket...")
    batch = pipeline.predict_batch([TICKET])
    print("predict_batch(): completed")

    describe_object("BATCH predict_batch() RESULT", batch)

    print()
    print("=" * 78)
    print("H-RUN-022R1 SUMMARY")
    print("=" * 78)

    print("Single result type :", type(single))
    print("Batch result type  :", type(batch))

    if isinstance(batch, list):
        print("Batch length       :", len(batch))

    print()
    print("No model execution changes")
    print("No retraining")
    print("No model modification")
    print("No threshold optimization")
    print("No locked-test reuse")
    print("No prediction modification")

    print()
    print("STATUS: CONTRACT_INSPECTION_COMPLETE")


if __name__ == "__main__":
    main()