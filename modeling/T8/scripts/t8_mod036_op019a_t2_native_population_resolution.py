from pathlib import Path
import csv
import json


ROOT = Path("/home/whiteblack/Documents/IT-Ticket-Triage-System")
T2_ROOT = ROOT / "modeling/T2"
OUT_DIR = ROOT / "modeling/T8/mod036/op019a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = OUT_DIR / "t8_mod036_op019a_t2_native_population_resolution.json"

csv.field_size_limit(10_000_000)


TARGET_NAMES = {
    "target_priority",
    "priority",
    "priority_truth",
    "priority_target",
    "first_priority",
    "priority_label",
}

ID_NAMES = {
    "id",
    "ID",
    "ticket_id",
    "bug_id",
    "ticket",
}

TEXT_NAMES = {
    "summary",
    "Summary",
    "description",
    "Description",
    "short_desc",
    "short_description",
}

FORBIDDEN_POST_CREATION_TERMS = (
    "resolved",
    "resolution",
    "closed",
    "closure",
    "assigned",
    "assignee",
    "assignment",
    "history",
    "event",
    "future",
)


def read_csv_header(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
            newline="",
        ) as f:
            reader = csv.reader(f)
            return next(reader, [])
    except Exception as exc:
        return [f"__READ_ERROR__: {exc}"]


def inspect_json(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
        ) as f:
            obj = json.load(f)

        keys = []

        if isinstance(obj, dict):
            keys = list(obj.keys())

        return {
            "valid_json": True,
            "type": type(obj).__name__,
            "top_level_keys": keys[:100],
        }

    except Exception as exc:
        return {
            "valid_json": False,
            "error": str(exc),
        }


def score_csv(path, columns):
    lowered = {
        str(column).strip().lower()
        for column in columns
    }

    target_hits = sorted(
        lowered & {
            x.lower()
            for x in TARGET_NAMES
        }
    )

    id_hits = sorted(
        lowered & {
            x.lower()
            for x in ID_NAMES
        }
    )

    text_hits = sorted(
        lowered & {
            x.lower()
            for x in TEXT_NAMES
        }
    )

    forbidden_hits = sorted(
        column
        for column in columns
        if any(
            token in str(column).lower()
            for token in FORBIDDEN_POST_CREATION_TERMS
        )
    )

    score = 0

    if target_hits:
        score += 10

    if id_hits:
        score += 3

    if len(text_hits) >= 2:
        score += 3

    if forbidden_hits:
        score -= 2

    return {
        "score": score,
        "target_hits": target_hits,
        "id_hits": id_hits,
        "text_hits": text_hits,
        "forbidden_post_creation_like_columns": forbidden_hits,
    }


def main():

    print("=" * 80)
    print("T8 DECISION ENGINE — MOD-036 OP-019A")
    print("T2 Native Labeled Development Population Resolution")
    print("=" * 80)

    if not T2_ROOT.exists():
        raise FileNotFoundError(T2_ROOT)

    csv_candidates = sorted(
        T2_ROOT.rglob("*.csv")
    )

    json_candidates = sorted(
        T2_ROOT.rglob("*.json")
    )

    print("\nT2 files discovered")
    print("-" * 80)
    print(f"  CSV files:  {len(csv_candidates)}")
    print(f"  JSON files: {len(json_candidates)}")

    csv_results = []

    for path in csv_candidates:

        columns = read_csv_header(path)

        if not columns:
            continue

        assessment = score_csv(
            path,
            columns,
        )

        if (
            assessment["target_hits"]
            or assessment["id_hits"]
            or assessment["text_hits"]
        ):
            csv_results.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "size_bytes": path.stat().st_size,
                    "columns": columns,
                    **assessment,
                }
            )

    csv_results.sort(
        key=lambda x: (
            x["score"],
            bool(x["target_hits"]),
            len(x["text_hits"]),
        ),
        reverse=True,
    )

    print("\nCandidate CSV artifacts")
    print("-" * 80)

    for item in csv_results[:30]:
        print(
            f"  score={item['score']:>3} "
            f"target={item['target_hits']} "
            f"id={item['id_hits']} "
            f"text={item['text_hits']} "
            f"{item['path']}"
        )

    # -------------------------------------------------------------
    # JSON provenance scan
    # -------------------------------------------------------------

    json_results = []

    target_terms = (
        "target_priority",
        "priority",
        "priority_target",
        "target",
        "prediction_boundary",
        "creation",
        "train",
        "validation",
        "split",
    )

    for path in json_candidates:

        try:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            ).lower()
        except Exception:
            continue

        hits = [
            term
            for term in target_terms
            if term in text
        ]

        if hits:
            json_results.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "size_bytes": path.stat().st_size,
                    "hits": hits,
                }
            )

    print("\nRelevant JSON provenance artifacts")
    print("-" * 80)

    for item in json_results[:30]:
        print(
            f"  {item['path']} "
            f"hits={item['hits']}"
        )

    # -------------------------------------------------------------
    # Contract inspection
    # -------------------------------------------------------------

    contract_candidates = [
        path
        for path in json_candidates
        if "contract" in path.name.lower()
    ]

    contracts = []

    for path in contract_candidates:

        inspection = inspect_json(path)

        contracts.append(
            {
                "path": str(path.relative_to(ROOT)),
                **inspection,
            }
        )

    # -------------------------------------------------------------
    # Identify strongest native population candidates
    # -------------------------------------------------------------

    native_candidates = [
        item
        for item in csv_results
        if item["target_hits"]
        and item["id_hits"]
        and len(item["text_hits"]) >= 2
    ]

    # -------------------------------------------------------------
    # Do not select automatically if ambiguous
    # -------------------------------------------------------------

    resolution_status = (
        "RESOLVED_SINGLE_STRONG_CANDIDATE"
        if len(native_candidates) == 1
        else
        "MULTIPLE_CANDIDATES_REQUIRE_PROVENANCE_CHECK"
        if len(native_candidates) > 1
        else
        "NO_NATIVE_LABELED_POPULATION_RESOLVED"
    )

    print("\nResolution")
    print("-" * 80)
    print(
        f"  strong native candidates: "
        f"{len(native_candidates)}"
    )
    print(
        f"  status: {resolution_status}"
    )

    if native_candidates:
        print("\nStrong candidates")
        print("-" * 80)

        for item in native_candidates[:20]:
            print(
                f"  {item['path']}"
            )
            print(
                f"    rows cannot yet be trusted from header-only scan"
            )
            print(
                f"    target columns: {item['target_hits']}"
            )
            print(
                f"    ID columns: {item['id_hits']}"
            )
            print(
                f"    text columns: {item['text_hits']}"
            )
            print(
                f"    post-Creation-like columns: "
                f"{item['forbidden_post_creation_like_columns']}"
            )

    result = {
        "operation": "MOD-036 OP-019A",
        "purpose": (
            "Resolve the authoritative native T2 labeled development "
            "population required for T8 Priority Decision Component "
            "development."
        ),
        "t2_root": str(T2_ROOT.relative_to(ROOT)),
        "discovered_files": {
            "csv_count": len(csv_candidates),
            "json_count": len(json_candidates),
        },
        "csv_candidates": csv_results,
        "json_provenance_candidates": json_results,
        "contracts": contracts,
        "native_population_candidates": native_candidates,
        "resolution": {
            "status": resolution_status,
            "automatic_selection_performed": False,
            "training_performed": False,
            "prediction_generation_performed": False,
            "dataset_modified": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nArtifact")
    print("-" * 80)
    print(f"  {OUTPUT}")

    print("\nStatus: PASS")
    print(
        "Note: PASS means the resolution audit completed; "
        "it does not mean a training population was selected."
    )

    print("=" * 80)


if __name__ == "__main__":
    main()