from pathlib import Path
import json


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

T7_MODEL = (
    ROOT
    / "modeling/T7/metrics/t7_mod010_log_normal_aft_model.json"
)

OUTPUT = (
    ROOT
    / "modeling/FMP/metrics/"
    "h_run011r1_t7_model_structure.json"
)


def describe(value, indent=0):
    prefix = " " * indent

    if isinstance(value, dict):
        print(f"{prefix}type=dict keys={len(value)}")

        for key, child in value.items():
            if isinstance(child, dict):
                print(f"{prefix}- {key}: dict")
            elif isinstance(child, list):
                print(
                    f"{prefix}- {key}: "
                    f"list(len={len(child)})"
                )
            else:
                print(
                    f"{prefix}- {key}: "
                    f"{type(child).__name__} "
                    f"value={child}"
                )

    elif isinstance(value, list):
        print(
            f"{prefix}type=list length={len(value)}"
        )

        if value:
            print(
                f"{prefix}first_item_type="
                f"{type(value[0]).__name__}"
            )

    else:
        print(
            f"{prefix}type={type(value).__name__} "
            f"value={value}"
        )


def main():
    print("=" * 72)
    print("H-RUN-011R1 — T7 MODEL JSON STRUCTURE")
    print("=" * 72)

    print("\n[CONTROL]")
    print("training/retraining: NO")
    print("model modification: NO")
    print("prediction: NO")
    print("locked-test use: NO")

    if not T7_MODEL.exists():
        raise FileNotFoundError(
            f"Missing T7 model JSON: {T7_MODEL}"
        )

    model = json.loads(
        T7_MODEL.read_text(
            encoding="utf-8"
        )
    )

    print("\n[ROOT STRUCTURE]")
    describe(model)

    print("\n[IMPORTANT FIELDS]")

    for key in [
        "feature_names",
        "beta",
        "sigma",
    ]:
        print(f"\n--- {key} ---")

        if key not in model:
            print("MISSING")
            continue

        value = model[key]

        if key == "beta" and isinstance(value, dict):
            print(
                f"beta dictionary entries: {len(value)}"
            )

            for idx, (name, coefficient) in enumerate(
                value.items()
            ):
                print(
                    f"{idx}: {name} -> "
                    f"{coefficient}"
                )

                if idx >= 30:
                    print("... truncated ...")
                    break

        elif key == "feature_names":
            print(
                f"type={type(value).__name__}"
            )

            if isinstance(value, list):
                print(
                    f"count={len(value)}"
                )

                for idx, name in enumerate(value):
                    print(
                        f"{idx}: {name}"
                    )

        else:
            describe(value, indent=2)

    output = {
        "operation": "H-RUN-011R1",
        "operation_name": (
            "T7 Model JSON Structure Inspection"
        ),
        "status": "PASS",
        "model_path": str(T7_MODEL),
        "root_type": type(model).__name__,
        "root_keys": list(model.keys()),
        "field_types": {
            key: (
                type(model[key]).__name__
                if key in model
                else None
            )
            for key in [
                "feature_names",
                "beta",
                "sigma",
            ]
        },
        "beta_entry_count": (
            len(model["beta"])
            if isinstance(model.get("beta"), dict)
            else None
        ),
        "controls": {
            "training": False,
            "retraining": False,
            "model_modification": False,
            "prediction": False,
            "locked_test_use": False,
        },
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n[OUTPUT]")
    print(f"written: {OUTPUT}")

    print("\n" + "=" * 72)
    print("H-RUN-011R1 COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()