import os
from typing import Any

import psycopg
from psycopg.types.json import Jsonb


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "it_ticket_triage")
DB_USER = os.getenv("DB_USER", "it_ticket_app")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_connection():
    if not DB_PASSWORD:
        raise RuntimeError("DB_PASSWORD environment variable is not set")

    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def save_ticket(ticket: dict[str, Any]) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tickets (
                    ticket_id,
                    creation_time,
                    creator,
                    creator_detail,
                    summary,
                    description
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (ticket_id)
                DO UPDATE SET
                    creation_time = EXCLUDED.creation_time,
                    creator = EXCLUDED.creator,
                    creator_detail = EXCLUDED.creator_detail,
                    summary = EXCLUDED.summary,
                    description = EXCLUDED.description
                RETURNING id
                """,
                (
                    ticket["ticket_id"],
                    ticket["creation_time"],
                    ticket["creator"],
                    ticket["creator_detail"],
                    ticket["summary"],
                    ticket["description"],
                ),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Unable to persist ticket")

            return row[0]


def save_analysis(
    ticket_db_id: int,
    analysis_result: dict[str, Any],
    explanation: dict[str, Any],
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ticket_analyses (
                    ticket_id,
                    analysis_result,
                    explanation
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    ticket_db_id,
                    Jsonb(analysis_result),
                    Jsonb(explanation),
                ),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Unable to persist analysis")

            return row[0]


def save_human_review(
    analysis_id: int,
    decision: str,
    review_notes: str | None = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO human_reviews (
                    ticket_analysis_id,
                    decision,
                    review_notes
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    analysis_id,
                    decision,
                    review_notes,
                ),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Unable to persist human review")

            return row[0]
