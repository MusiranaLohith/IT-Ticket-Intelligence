# IT Ticket Intelligence - Deployment Runtime

## Runtime API

The validated runtime provides:

- TicketPipeline.predict(ticket)
- TicketPipeline.predict_batch(tickets)

## Pipeline

T1 -> T2 -> T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9 -> T10 -> T11

## Important boundaries

- T1-T7 use frozen modeling artifacts.
- T8 preserves native evidence semantics.
- Missing evidence is not treated as a negative outcome.
- T9 does not create universal confidence or universal risk.
- T10 does not establish an empirically validated autonomous threshold.
- T11 represents lifecycle and feedback state.

## T6 limitation

The full frozen MOD-010 semantic branch depends on stored
evaluation-population semantic evidence.

A genuinely new ticket therefore reports the explicit
PARTIAL_NATIVE_RUNTIME boundary rather than fabricating
a semantic score.

## T7 limitation

The frozen survival model executes using the authoritative
21-feature creation-time construction.

Tickets outside the observed training temporal range receive
an explicit temporal-support limitation.

## Decision boundary

The system provides decision support.

It does not claim autonomous ticket disposition.

Human decision remains required where the T10 policy boundary
indicates incomplete or unsupported evidence.
