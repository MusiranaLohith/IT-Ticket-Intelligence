from pathlib import Path


PROJECT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "models"
)

METRICS_DIR = (
    PROJECT_ROOT
    / "modeling"
    / "T5"
    / "metrics"
)


EXPECTED_ARTIFACTS = [
    "t5_mod007_calibration_models.joblib",
    "t5_mod007_calibrated_tfidf.joblib",
    "t5_mod007_calibrated_validation_predictions.npz",
]


print("=" * 80)
print("T5-MOD-009 — MOD-007 ARTIFACT DIAGNOSTIC")
print("=" * 80)

print("\nMODEL DIRECTORY")
print(MODEL_DIR)

print("\nEXPECTED MOD-007 ARTIFACTS")

for filename in EXPECTED_ARTIFACTS:
    path = MODEL_DIR / filename

    print(
        f"{filename}: "
        f"{'EXISTS' if path.exists() else 'MISSING'}"
    )

    if path.exists():
        print(
            f"  size={path.stat().st_size:,} bytes"
        )


print("\nALL FILES IN MODEL DIRECTORY")

if MODEL_DIR.exists():
    files = sorted(
        MODEL_DIR.iterdir(),
        key=lambda p: p.name.lower(),
    )

    if not files:
        print("  <EMPTY>")

    for path in files:
        if path.is_file():
            print(
                f"  {path.name} "
                f"({path.stat().st_size:,} bytes)"
            )
else:
    print("  MODEL DIRECTORY DOES NOT EXIST")


print("\nRELEVANT METRIC ARTIFACTS")

if METRICS_DIR.exists():
    for path in sorted(
        METRICS_DIR.iterdir(),
        key=lambda p: p.name.lower(),
    ):
        if "mod007" in path.name.lower():
            print(
                f"  {path.name} "
                f"({path.stat().st_size:,} bytes)"
            )


print("\nNo model loaded.")
print("No model trained.")
print("No evaluation performed.")
print("No files modified.")

print("\nRESULT: ARTIFACT_DIAGNOSTIC_COMPLETE")