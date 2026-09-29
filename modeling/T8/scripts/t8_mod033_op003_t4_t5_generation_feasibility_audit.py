from pathlib import Path
import json
import re


ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System"
)

OUTPUT = (
    ROOT
    / "modeling/T8/mod033"
    / "t8_mod033_op003_t4_t5_generation_feasibility.json"
)


SEARCH_ROOTS = {
    "T4": ROOT / "modeling/T4",
    "T5": ROOT / "modeling/T5",
}


KEYWORDS = [
    "predict",
    "prediction",
    "predictions",
    "predict_proba",
    "decision_function",
    "rank",
    "ranking",
    "retrieval",
    "save",
    "csv",
    "output",
    "evaluation",
    "validation",
    "train",
    "fit",
    "checkpoint",
    "model",
    "ID",
    "Creation",
]


def source_files(root):
    if not root.exists():
        return []

    return sorted(
        path
        for path in root.rglob("*.py")
        if path.is_file()
    )


def relevant_lines(path):
    matches = []

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception as exc:

        return {
            "error": repr(exc),
            "matches": [],
        }

    for number, line in enumerate(
        text.splitlines(),
        start=1,
    ):

        lowered = line.lower()

        if any(
            keyword.lower() in lowered
            for keyword in KEYWORDS
        ):

            matches.append(
                {
                    "line": number,
                    "text": line.strip(),
                }
            )

    return {
        "error": None,
        "matches": matches,
    }


def find_contract_terms(root):
    contracts = []

    if not root.exists():
        return contracts

    for path in sorted(
        root.rglob("*.json")
    ):

        if "contract" not in path.name.lower():
            continue

        try:

            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            contracts.append(
                {
                    "path": str(
                        path.relative_to(ROOT)
                    ),
                    "top_level_type":
                        type(data).__name__,
                    "keys":
                        list(data.keys())
                        if isinstance(data, dict)
                        else [],
                }
            )

        except Exception as exc:

            contracts.append(
                {
                    "path": str(
                        path.relative_to(ROOT)
                    ),
                    "error": repr(exc),
                }
            )

    return contracts


print("=" * 100)
print(
    "T8 MOD-033 — OP-003: "
    "T4/T5 NATIVE DEVELOPMENT PREDICTION "
    "GENERATION FEASIBILITY AUDIT"
)
print("=" * 100)


audit = {
    "module": "T8-MOD-033",
    "operation": "OP-003",
    "tasks": {},
    "locked_evaluation_used": False,
    "prediction_generation_performed": False,
}


for task, root in SEARCH_ROOTS.items():

    print("\n" + "=" * 100)
    print(task)
    print("=" * 100)

    files = source_files(root)

    print(
        "Python source files found:",
        len(files),
    )

    task_record = {
        "root_exists": root.exists(),
        "python_source_count": len(files),
        "source_files": [],
        "contracts": find_contract_terms(root),
    }

    print("\nContracts:")

    for contract in task_record["contracts"]:

        print(
            "  ",
            contract["path"],
        )

        if "keys" in contract:
            print(
                "     keys:",
                contract["keys"],
            )

    for path in files:

        inspection = relevant_lines(path)

        record = {
            "path": str(
                path.relative_to(ROOT)
            ),
            "keyword_matches":
                inspection["matches"],
            "error":
                inspection["error"],
        }

        if inspection["matches"]:

            print(
                "\n---",
                path.relative_to(ROOT),
                "---",
            )

            for match in inspection["matches"][:80]:

                print(
                    f"{match['line']:5d}: "
                    f"{match['text']}"
                )

            if len(
                inspection["matches"]
            ) > 80:

                print(
                    "...",
                    len(
                        inspection["matches"]
                    ) - 80,
                    "additional matches",
                )

        task_record[
            "source_files"
        ].append(record)

    audit["tasks"][task] = task_record


# ------------------------------------------------------------------
# Targeted feasibility signals
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("TARGETED FEASIBILITY SIGNALS")
print("=" * 100)


for task, record in audit["tasks"].items():

    print("\n", task)

    all_matches = []

    for source in record["source_files"]:

        for match in source[
            "keyword_matches"
        ]:

            all_matches.append(
                (
                    source["path"],
                    match["line"],
                    match["text"],
                )
            )

    signals = {
        "has_predict_api":
            any(
                "predict(" in text
                or "predict_proba(" in text
                for _, _, text in all_matches
            ),

        "has_ranking_logic":
            any(
                "rank" in text.lower()
                or "retrieval" in text.lower()
                for _, _, text in all_matches
            ),

        "has_csv_output_logic":
            any(
                "to_csv" in text
                or "csv" in text.lower()
                for _, _, text in all_matches
            ),

        "has_ID_reference":
            any(
                re.search(
                    r"\bID\b",
                    text
                )
                for _, _, text in all_matches
            ),

        "has_validation_or_eval_logic":
            any(
                "validation" in text.lower()
                or "evaluation" in text.lower()
                for _, _, text in all_matches
            ),

        "has_checkpoint_logic":
            any(
                "checkpoint" in text.lower()
                for _, _, text in all_matches
            ),

        "has_train_fit_logic":
            any(
                ".fit(" in text
                or "fit(" in text
                for _, _, text in all_matches
            ),
    }

    record["feasibility_signals"] = signals

    for key, value in signals.items():

        print(
            f"{key}: {value}"
        )


# ------------------------------------------------------------------
# Explicit guards
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("FEASIBILITY GUARDS")
print("=" * 100)

guards = {
    "native_semantics_preserved":
        True,

    "no_T4_ranking_to_probability_conversion":
        True,

    "no_T5_duplicate_identity_reinterpretation":
        True,

    "no_locked_evaluation_repurposing":
        True,

    "no_post_creation_features":
        True,

    "no_prediction_generation_performed":
        True,
}

for key, value in guards.items():

    print(
        f"{key}: {value}"
    )

audit["guards"] = guards


# ------------------------------------------------------------------
# Final interpretation
# ------------------------------------------------------------------

print("\n" + "=" * 100)
print("INTERPRETATION")
print("=" * 100)

print(
    "This audit determines whether the existing "
    "native T4/T5 implementation contains enough "
    "reproducible machinery to consider development "
    "prediction generation."
)

print(
    "It does NOT itself generate predictions."
)

print(
    "It does NOT establish that generation is "
    "safe or eligible."
)

print(
    "Split provenance, prediction boundary, "
    "development population, and output semantics "
    "must still be verified before generation."
)


with OUTPUT.open(
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        audit,
        f,
        indent=2,
    )


print(
    "\nAudit written:",
    OUTPUT,
)

print("\n" + "=" * 100)
print("MOD-033 OP-003 COMPLETE")
print("=" * 100)