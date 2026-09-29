from pathlib import Path
import json
import joblib
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = PROJECT_ROOT / "modeling" / "T5" / "models"
METRICS_DIR = PROJECT_ROOT / "modeling" / "T5" / "metrics"

CALIBRATION_MODEL = MODEL_DIR / "t5_mod007_calibration_models.joblib"
CALIBRATION_PREDICTIONS = METRICS_DIR / "t5_mod007_calibrated_validation_predictions.npz"
COMPARISON_JSON = METRICS_DIR / "t5_mod007_calibration_comparison.json"


def describe_object(name, obj, indent="  "):
    print(f"{indent}{name}")
    print(f"{indent}  type: {type(obj)}")

    if isinstance(obj, dict):
        print(f"{indent}  keys:")
        for key, value in obj.items():
            print(f"{indent}    {key!r}: {type(value)}")

    elif isinstance(obj, (list, tuple)):
        print(f"{indent}  length: {len(obj)}")

        for index, value in enumerate(obj):
            print(f"{indent}    [{index}]: {type(value)}")

    else:
        for attr in ("coef_", "intercept_", "classes_", "n_features_in_"):
            if hasattr(obj, attr):
                value = getattr(obj, attr)

                if hasattr(value, "shape"):
                    print(f"{indent}  {attr}: shape={value.shape}")
                else:
                    print(f"{indent}  {attr}: {value!r}")


print("=" * 80)
print("T5-MOD-009 — MOD-007 ARTIFACT CONTENT INSPECTION")
print("=" * 80)

print("\n1. CALIBRATION MODEL ARTIFACT")
print("-" * 80)

if not CALIBRATION_MODEL.exists():
    print("FAIL: Calibration model artifact does not exist.")
else:
    print(f"Path: {CALIBRATION_MODEL}")
    print(f"Size: {CALIBRATION_MODEL.stat().st_size:,} bytes")

    obj = joblib.load(CALIBRATION_MODEL)

    print(f"Loaded object type: {type(obj)}")

    if isinstance(obj, dict):
        print("\nDictionary contents:")
        for key, value in obj.items():
            print(f"\n  KEY: {key!r}")
            describe_object("VALUE", value, indent="    ")
    else:
        describe_object("ROOT OBJECT", obj)

print("\n2. MOD-007 VALIDATION PREDICTIONS")
print("-" * 80)

if not CALIBRATION_PREDICTIONS.exists():
    print("MISSING: MOD-007 calibrated validation predictions.")
else:
    print(f"Path: {CALIBRATION_PREDICTIONS}")
    print(f"Size: {CALIBRATION_PREDICTIONS.stat().st_size:,} bytes")

    data = np.load(CALIBRATION_PREDICTIONS)

    print("NPZ arrays:")

    for key in data.files:
        array = data[key]

        print(
            f"  {key}: "
            f"shape={array.shape}, "
            f"dtype={array.dtype}"
        )

print("\n3. MOD-007 COMPARISON METADATA")
print("-" * 80)

if not COMPARISON_JSON.exists():
    print("MISSING: MOD-007 comparison JSON.")
else:
    print(f"Path: {COMPARISON_JSON}")

    with open(COMPARISON_JSON, "r", encoding="utf-8") as f:
        comparison = json.load(f)

    print("Top-level keys:")
    for key in comparison:
        print(f"  {key}")

print("\n4. MODEL DIRECTORY")
print("-" * 80)

for path in sorted(MODEL_DIR.iterdir()):
    if path.is_file():
        print(f"  {path.name} ({path.stat().st_size:,} bytes)")

print("\n5. REQUIRED MOD-007 COMPONENTS")
print("-" * 80)

required = {
    "calibration_models": CALIBRATION_MODEL.exists(),
    "calibrated_tfidf": (
        MODEL_DIR / "t5_mod007_calibrated_tfidf.joblib"
    ).exists(),
    "calibrated_validation_predictions": CALIBRATION_PREDICTIONS.exists(),
}

for name, exists in required.items():
    print(f"  {name}: {'PRESENT' if exists else 'MISSING'}")

print("\nNo model trained.")
print("No evaluation performed.")
print("No dataset modified.")
print("No artifacts modified.")

print("\nRESULT: MOD007_ARTIFACT_CONTENT_INSPECTION_COMPLETE")