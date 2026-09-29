from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Deployment path configuration
# ---------------------------------------------------------------------------

DEPLOYMENT_ROOT = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/deployment"
)

if str(DEPLOYMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT_ROOT))

from config.deployment_config import CONFIG
from database import save_ticket, save_analysis, save_human_review


PROJECT_ROOT = CONFIG.project_root
RUNTIME_ROOT = CONFIG.packaged_runtime_root


if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))


# ---------------------------------------------------------------------------
# Frozen runtime imports
# ---------------------------------------------------------------------------

from ticket_pipeline import TicketPipeline
from ticket_explanation import TicketExplanation


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=CONFIG.application_name,
    version=CONFIG.application_version,
    description=(
        "Evidence-first IT ticket analysis and human decision support "
        "wrapped around the frozen T1-T11 runtime."
    ),
)


# ---------------------------------------------------------------------------
# Browser CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=[
        "*",
    ],
)


# ---------------------------------------------------------------------------
# Frozen runtime instances
# ---------------------------------------------------------------------------

PIPELINE = TicketPipeline()
EXPLAINER = TicketExplanation()


# ---------------------------------------------------------------------------
# Ticket schema
# ---------------------------------------------------------------------------

class TicketRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    ticket_id: str = Field(
        ...,
        min_length=1,
    )

    creation_time: str = Field(
        ...,
        min_length=1,
    )

    creator: str = Field(
        ...,
        min_length=1,
    )

    creator_detail: str = Field(
        ...,
        min_length=1,
    )

    summary: str = Field(
        ...,
        min_length=1,
    )

    description: str = Field(
        ...,
        min_length=1,
    )


class BatchTicketRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    tickets: list[TicketRequest] = Field(
        ...,
        min_length=1,
    )


class HumanReviewRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    analysis_id: int = Field(
        ...,
        ge=1,
    )

    decision: str = Field(
        ...,
        min_length=1,
    )

    review_notes: str | None = None


# ---------------------------------------------------------------------------
# Path sanitization
# ---------------------------------------------------------------------------

def sanitize_paths(value: Any) -> Any:
    """
    Recursively sanitize absolute project/runtime paths before exposing
    runtime results through the API boundary.

    The frozen runtime itself is not modified.
    """

    if isinstance(value, dict):
        return {
            key: sanitize_paths(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            sanitize_paths(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            sanitize_paths(item)
            for item in value
        ]

    if isinstance(value, str):
        normalized = value.replace("\\", "/")

        project_text = str(PROJECT_ROOT).replace("\\", "/")
        runtime_text = str(RUNTIME_ROOT).replace("\\", "/")

        if normalized.startswith(runtime_text):
            relative = normalized[len(runtime_text):].lstrip("/")
            return f"runtime/{relative}"

        if normalized.startswith(project_text):
            relative = normalized[len(project_text):].lstrip("/")
            return relative

        return value

    return value


# ---------------------------------------------------------------------------
# Single-ticket endpoint
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "OK",
        "application": {
            "name": CONFIG.application_name,
            "version": CONFIG.application_version,
        },
        "runtime": {
            "status": "AVAILABLE",
            "location": str(RUNTIME_ROOT),
        },
        "production": {
            "ready": CONFIG.production_ready,
            "authorization": CONFIG.production_authorization,
        },
    }


@app.post("/tickets/analyze")
def analyze_ticket(ticket: TicketRequest) -> dict[str, Any]:
    """
    Analyze one ticket through the frozen T1-T11 runtime
    and persist the ticket and analysis in PostgreSQL.
    """

    ticket_data = ticket.model_dump()

    ticket_db_id = save_ticket(ticket_data)

    raw_result = PIPELINE.predict(ticket_data)

    explanation = EXPLAINER.explain(raw_result)

    analysis_db_id = save_analysis(
        ticket_db_id,
        raw_result,
        explanation,
    )

    response = {
        **raw_result,
        "explanation": explanation,
        "persistence": {
            "ticket_id": ticket_db_id,
            "analysis_id": analysis_db_id,
        },
    }

    return sanitize_paths(response)


# ---------------------------------------------------------------------------
# Batch endpoint
# ---------------------------------------------------------------------------

@app.post("/tickets/analyze-batch")
def analyze_batch(
    request: BatchTicketRequest,
) -> dict[str, Any]:
    """
    Analyze multiple independent tickets through the frozen
    TicketPipeline.predict_batch() runtime capability.

    Each submitted ticket and resulting analysis is persisted
    independently in PostgreSQL.

    The API does not define special batch sizes. The number of
    tickets comes entirely from the submitted input.
    """

    ticket_data = [
        ticket.model_dump()
        for ticket in request.tickets
    ]

    ticket_db_ids = [
        save_ticket(ticket)
        for ticket in ticket_data
    ]

    raw_results = PIPELINE.predict_batch(ticket_data)

    results: list[dict[str, Any]] = []

    for ticket_db_id, raw_result in zip(ticket_db_ids, raw_results):
        explanation = EXPLAINER.explain(raw_result)

        analysis_db_id = save_analysis(
            ticket_db_id,
            raw_result,
            explanation,
        )

        result = {
            **raw_result,
            "explanation": explanation,
            "persistence": {
                "ticket_id": ticket_db_id,
                "analysis_id": analysis_db_id,
            },
        }

        results.append(
            sanitize_paths(result)
        )

    return {
        "batch": {
            "submitted": len(ticket_data),
            "analyzed": len(results),
            "failed": 0,
        },
        "results": results,
    }


# ---------------------------------------------------------------------------
# Human review endpoint
# ---------------------------------------------------------------------------

@app.post("/tickets/reviews")
def create_human_review(
    review: HumanReviewRequest,
) -> dict[str, Any]:
    """
    Persist a human decision against a stored ticket analysis.
    """

    try:
        review_id = save_human_review(
            review.analysis_id,
            review.decision,
            review.review_notes,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to persist human review: {exc}",
        ) from exc

    return {
        "status": "saved",
        "review_id": review_id,
        "analysis_id": review.analysis_id,
        "decision": review.decision,
        "review_notes": review.review_notes,
    }
