from __future__ import annotations


class TicketExplanation:
    """
    Human-readable presentation layer for TicketPipeline output.

    This class does not modify predictions, thresholds, models,
    or pipeline decisions. It only explains the existing result.
    """

    @staticmethod
    def _priority_text(value):
        if value is None:
            return "Unavailable"

        return f"{value} — Priority class {value}"

    @staticmethod
    def _severity_text(value):
        if value is None:
            return "Unavailable"

        return f"{value} — Severity class {value}"

    @staticmethod
    def _t4_explanation(t4):
        results = t4.get("results", [])

        if not results:
            return (
                "No historical related-ticket candidates were "
                "returned by the routing/assignment evidence stage."
            )

        return (
            f"{len(results)} historical related-ticket candidates "
            "were retrieved. These are historical retrieval "
            "evidence, not proof of current operational assignment."
        )

    @staticmethod
    def _t5_explanation(t5):
        score = t5.get("duplicate_evidence")

        if score is None:
            return (
                "Duplicate evidence was unavailable. "
                "No duplicate decision is inferred."
            )

        return (
            f"Duplicate evidence = {score:.4f}. "
            "No operational duplicate threshold was applied."
        )

    @staticmethod
    def _t6_explanation(t6):
        status = t6.get("status")

        if status == "PARTIAL_NATIVE_RUNTIME":
            return (
                "Full semantic retrieval is unavailable for this "
                "genuinely new ticket because the frozen MOD-010 "
                "semantic component depends on stored semantic "
                "evidence for the existing evaluation population. "
                "No semantic score was fabricated."
            )

        if status == "EXECUTED":
            return (
                "The semantic retrieval component executed using "
                "its available native evidence."
            )

        return f"T6 runtime status: {status}"

    @staticmethod
    def _t7_explanation(t7):
        median = t7.get("median_seconds")
        support = t7.get("temporal_support")

        if median is None:
            return "Resolution-time evidence was unavailable."

        text = (
            f"The model produced a median resolution-time estimate "
            f"of {median:.2f} seconds."
        )

        if support == "OUTSIDE_OBSERVED_TRAINING_RANGE":
            text += (
                " However, the ticket creation year is outside the "
                "observed training range, so this estimate carries "
                "a temporal-support limitation."
            )

        return text

    @staticmethod
    def _t8_explanation(t8):
        state = t8.get("evidence_state")

        if state == "SUPPORTED_WITH_LIMITATIONS":
            return (
                "The integrated evidence is usable with limitations. "
                "Some task evidence is incomplete or outside its "
                "supported runtime conditions. Missing evidence is "
                "not treated as negative evidence."
            )

        return f"Integrated evidence state: {state}"

    @staticmethod
    def _t9_explanation(t9):
        return (
            "The pipeline preserves the native meaning of each task "
            "output. It does not create a universal confidence or "
            "risk score by combining incompatible task outputs."
        )

    @staticmethod
    def _t10_explanation(t10):
        action = t10.get("action")

        if action == "HUMAN_DECISION_REQUIRED":
            return (
                "The pipeline does not establish an autonomous "
                "operational action. Because the available evidence "
                "has documented limitations, the ticket requires "
                "human review."
            )

        return f"Pipeline action: {action}"

    @staticmethod
    def _t11_explanation(t11):
        feedback = t11.get("feedback")

        if feedback == "AWAITING_OUTCOME":
            return (
                "The ticket is awaiting an eventual operational "
                "outcome. No synthetic feedback is created."
            )

        return f"Lifecycle state: {feedback}"

    @classmethod
    def explain(cls, result):
        ticket = result.get("ticket", {})
        tasks = result.get("tasks", {})
        final = result.get("final", {})
        integrity = result.get("integrity", {})

        ticket_id = ticket.get("ticket_id", "UNKNOWN")
        summary = ticket.get("summary", "")

        t1 = tasks.get("T1", {})
        t2 = tasks.get("T2", {})
        t3 = tasks.get("T3", {})
        t4 = tasks.get("T4", {})
        t5 = tasks.get("T5", {})
        t6 = tasks.get("T6", {})
        t7 = tasks.get("T7", {})
        t8 = tasks.get("T8", {})
        t9 = tasks.get("T9", {})
        t10 = tasks.get("T10", {})
        t11 = tasks.get("T11", {})

        category = final.get(
            "category",
            t1.get("prediction", "Unavailable"),
        )

        priority = final.get(
            "priority",
            t2.get("prediction"),
        )

        severity = final.get(
            "severity",
            t3.get("prediction"),
        )

        lines = []

        lines.append("=" * 78)
        lines.append(f"TICKET {ticket_id}")
        lines.append("=" * 78)

        lines.append("")
        lines.append("ISSUE")
        lines.append("-" * 78)
        lines.append(summary)

        lines.append("")
        lines.append("WHAT THE SYSTEM FOUND")
        lines.append("-" * 78)
        lines.append(f"Category : {category}")
        lines.append(f"Priority : {cls._priority_text(priority)}")
        lines.append(f"Severity : {cls._severity_text(severity)}")

        lines.append("")
        lines.append("SUPPORTING EVIDENCE")
        lines.append("-" * 78)
        lines.append(f"T4 Routing / Assignment: {cls._t4_explanation(t4)}")
        lines.append(f"T5 Duplicate Evidence: {cls._t5_explanation(t5)}")
        lines.append(f"T6 Semantic Retrieval: {cls._t6_explanation(t6)}")
        lines.append(f"T7 Resolution Evidence: {cls._t7_explanation(t7)}")

        lines.append("")
        lines.append("HOW THE PIPELINE REACHED ITS DECISION")
        lines.append("-" * 78)

        lines.append(
            "1. T1–T3 produced category, priority, and severity evidence."
        )
        lines.append(
            "2. T4 added historical related-ticket retrieval evidence."
        )
        lines.append(
            "3. T5 added duplicate-relationship evidence without "
            "applying an operational threshold."
        )
        lines.append(
            "4. T6 reported only the semantic evidence that was "
            "actually available for this new ticket."
        )
        lines.append(
            "5. T7 produced resolution-time evidence together with "
            "its temporal-support status."
        )
        lines.append(
            f"6. T8 integrated the available evidence as: "
            f"{t8.get('evidence_state')}"
        )
        lines.append(
            "7. T9 preserved native task semantics and did not "
            "create universal confidence or risk."
        )
        lines.append(
            f"8. T10 produced the pipeline action: "
            f"{t10.get('action')}"
        )
        lines.append(
            f"9. T11 recorded the lifecycle state: "
            f"{t11.get('feedback')}"
        )

        lines.append("")
        lines.append("PIPELINE DECISION")
        lines.append("-" * 78)
        lines.append(
            f"Evidence state : {final.get('evidence_state')}"
        )
        lines.append(
            f"Action         : {final.get('action')}"
        )
        lines.append(
            f"Lifecycle      : {final.get('lifecycle')}"
        )

        lines.append("")
        lines.append("WHY THIS DECISION")
        lines.append("-" * 78)
        lines.append(cls._t8_explanation(t8))
        lines.append(cls._t10_explanation(t10))
        lines.append(cls._t11_explanation(t11))

        warnings = t10.get("warnings", [])

        if warnings:
            lines.append("")
            lines.append("PIPELINE WARNINGS")
            lines.append("-" * 78)

            for warning in warnings:
                lines.append(f"- {warning}")

        lines.append("")
        lines.append("PLAIN-ENGLISH SUMMARY")
        lines.append("-" * 78)

        summary_parts = [
            (
                f"The system classified this ticket as {category}, "
                f"with {priority} priority evidence and "
                f"{severity} severity evidence."
            ),
            cls._t4_explanation(t4),
            cls._t6_explanation(t6),
            cls._t7_explanation(t7),
            (
                f"The integrated evidence state is "
                f"{final.get('evidence_state')}."
            ),
            cls._t10_explanation(t10),
        ]

        for part in summary_parts:
            lines.append(part)

        lines.append("")
        lines.append("SYSTEM MATURITY")
        lines.append("-" * 78)
        lines.append(
            "Research / engineering prototype — NOT PRODUCTION READY."
        )
        lines.append(
            "This output is decision-support evidence, not an "
            "autonomous operational ticket disposition."
        )

        lines.append("")
        lines.append("INTEGRITY")
        lines.append("-" * 78)

        integrity_failures = [
            key
            for key, value in integrity.items()
            if value not in (False, "NO", "NOT_PERFORMED")
        ]

        if integrity_failures:
            lines.append(
                "Integrity check: FAIL — "
                + ", ".join(integrity_failures)
            )
        else:
            lines.append("Integrity check: PASS")

        lines.append("=" * 78)

        return "\n".join(lines)