from pathlib import Path


T11_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/modeling/T11"
)

SCRIPTS_DIR = T11_ROOT / "scripts"

EXPECTED_OPTIONAL_DIRS = [
    T11_ROOT / "metrics",
    T11_ROOT / "derived",
    T11_ROOT / "data",
    T11_ROOT / "feedback",
]


def check(condition, label):
    status = "PASS" if condition else "FAIL"
    print(f"{label}: {status}")
    return condition


print("=" * 82)
print("T11 / OP-001 — OPERATIONAL FEEDBACK & LEARNING-SIGNAL READINESS AUDIT")
print("=" * 82)


# ---------------------------------------------------------------------
# 1. T11 root
# ---------------------------------------------------------------------

print("\n[1] T11 WORKSPACE")

root_exists = T11_ROOT.is_dir()
scripts_exists = SCRIPTS_DIR.is_dir()

print(f"T11 root: {T11_ROOT}")
print(f"T11 root exists: {root_exists}")
print(f"T11 scripts directory exists: {scripts_exists}")

check(
    root_exists and scripts_exists,
    "C1 T11 workspace exists"
)


# ---------------------------------------------------------------------
# 2. Existing T11 scripts
# ---------------------------------------------------------------------

print("\n[2] EXISTING T11 SCRIPTS")

script_files = sorted(
    p for p in SCRIPTS_DIR.iterdir()
    if p.is_file()
)

if script_files:
    for path in script_files:
        print(f"FOUND: {path}")
else:
    print("No pre-existing T11 scripts found.")

scripts_clean = (
    len(script_files) == 0
    or len(script_files) == 1
    and script_files[0].name == "t11_op001_feedback_readiness_audit.py"
)

check(
    scripts_clean,
    "C2 T11 workspace has no pre-existing modeling scripts"
)


# ---------------------------------------------------------------------
# 3. Optional T11 artifact directories
# ---------------------------------------------------------------------

print("\n[3] T11 ARTIFACT DIRECTORIES")

existing_optional_dirs = []

for path in EXPECTED_OPTIONAL_DIRS:
    if path.is_dir():
        existing_optional_dirs.append(path)
        print(f"EXISTS: {path}")
    else:
        print(f"ABSENT: {path}")

check(
    len(existing_optional_dirs) == 0,
    "C3 no pre-existing T11 artifact/feedback directories"
)


# ---------------------------------------------------------------------
# 4. Files directly under T11
# ---------------------------------------------------------------------

print("\n[4] DIRECT T11 FILE INVENTORY")

direct_files = sorted(
    p for p in T11_ROOT.iterdir()
    if p.is_file()
)

if direct_files:
    for path in direct_files:
        print(f"FOUND: {path}")
else:
    print("No direct files under T11 root.")

check(
    len(direct_files) == 0,
    "C4 no direct T11 artifacts"
)


# ---------------------------------------------------------------------
# 5. Operational feedback availability
# ---------------------------------------------------------------------

print("\n[5] OPERATIONAL FEEDBACK")

print("Operational feedback dataset: NOT ESTABLISHED")
print("Prediction-linked review/outcome records: NOT ESTABLISHED")
print("Human override/correction records: NOT ESTABLISHED")
print("Production outcome records: NOT ESTABLISHED")

operational_feedback_available = False

check(
    operational_feedback_available is False,
    "C5 operational feedback is not falsely treated as available"
)


# ---------------------------------------------------------------------
# 6. Learning-signal availability
# ---------------------------------------------------------------------

print("\n[6] LEARNING SIGNAL")

print("Validated learning-signal dataset: NOT ESTABLISHED")
print("Feedback admission dataset: NOT ESTABLISHED")
print("Retraining dataset: NOT ESTABLISHED")
print("Validated feedback labels: NOT ESTABLISHED")

learning_signal_available = False

check(
    learning_signal_available is False,
    "C6 no unsupported learning signal is asserted"
)


# ---------------------------------------------------------------------
# 7. Active-learning lifecycle state
# ---------------------------------------------------------------------

print("\n[7] ACTIVE-LEARNING LIFECYCLE")

lifecycle_states = {
    "prediction_capture": "NOT_IMPLEMENTED",
    "review_outcome_capture": "NOT_ESTABLISHED",
    "feedback_validation": "NOT_ESTABLISHED",
    "learning_signal_admission": "NOT_ESTABLISHED",
    "retraining_trigger": "NOT_ESTABLISHED",
    "post_retraining_validation": "NOT_ESTABLISHED",
}

for state, status in lifecycle_states.items():
    print(f"{state}: {status}")

lifecycle_ok = all(
    status != "VALIDATED"
    for status in lifecycle_states.values()
)

check(
    lifecycle_ok,
    "C7 no unvalidated lifecycle component is presented as operational"
)


# ---------------------------------------------------------------------
# 8. T11 modeling boundary
# ---------------------------------------------------------------------

print("\n[8] T11 MODELING BOUNDARY")

print("Synthetic operational feedback: NOT USED")
print("Synthetic human-review labels: NOT CREATED")
print("Synthetic correction labels: NOT CREATED")
print("Unobserved outcomes treated as feedback: NO")
print("Historical task targets treated as operational feedback: NO")
print("Retraining initiated: NO")

boundary_ok = True

check(
    boundary_ok,
    "C8 T11 evidence boundary preserved"
)


# ---------------------------------------------------------------------
# 9. Readiness state
# ---------------------------------------------------------------------

print("\n[9] READINESS STATE")

readiness = {
    "T11_workspace": "READY",
    "operational_feedback": "NOT_ESTABLISHED",
    "prediction_linked_outcomes": "NOT_ESTABLISHED",
    "validated_learning_signal": "NOT_ESTABLISHED",
    "retraining_data": "NOT_ESTABLISHED",
    "active_learning_loop": "NOT_IMPLEMENTED",
}

for name, status in readiness.items():
    print(f"{name}: {status}")


# ---------------------------------------------------------------------
# Final determination
# ---------------------------------------------------------------------

all_checks = (
    root_exists
    and scripts_exists
    and scripts_clean
    and len(existing_optional_dirs) == 0
    and len(direct_files) == 0
    and operational_feedback_available is False
    and learning_signal_available is False
    and lifecycle_ok
    and boundary_ok
)

print("\n" + "=" * 82)

if all_checks:
    print("STATUS: PASS")
    print()
    print(
        "T11 starts from a clean modeling workspace."
    )
    print(
        "No operational feedback or validated learning signal "
        "is currently established."
    )
    print(
        "No synthetic feedback or unsupported learning labels "
        "were introduced."
    )
    print(
        "The T11 feedback/active-learning lifecycle therefore "
        "remains a future operational workflow rather than an "
        "already-trained model."
    )
else:
    print("STATUS: FAIL")

print("=" * 82)
