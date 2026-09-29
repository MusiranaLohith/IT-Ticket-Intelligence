from pathlib import Path
import re


FRONTEND = Path(
    "/home/whiteblack/Documents/IT-Ticket-Triage-System/deployment/frontend"
)

APP = FRONTEND / "app.js"
BACKUP = FRONTEND / "app.js.before-deploy-op036"


if not APP.exists():
    raise SystemExit(f"FAIL: app.js not found: {APP}")


if not BACKUP.exists():
    raise SystemExit(
        f"FAIL: expected existing backup not found: {BACKUP}"
    )


current = APP.read_text(encoding="utf-8")
backup = BACKUP.read_text(encoding="utf-8")


if current != backup:
    raise SystemExit(
        "FAIL: current app.js differs from the OP-036 backup. "
        "Refusing to modify the file."
    )


pattern = re.compile(
    r'/\* =========================================================\n'
    r'   TICKET EXPLANATION\n'
    r'   ========================================================= \*/\n\n'
    r'function renderExplanation\([\s\S]*?\n\n'
    r'/\* =========================================================\n'
    r'   COMPLETE RESPONSE RENDERER\n'
    r'   ========================================================= \*/',
    re.MULTILINE,
)


replacement = r'''/* =========================================================
   TICKET EXPLANATION
   ========================================================= */

function renderExplanation(
    response
) {
    const explanationElement =
        document.getElementById(
            "explanation-content"
        );

    if (!explanationElement) {
        return;
    }

    explanationElement.innerHTML = "";


    if (
        response.explanation === null ||
        response.explanation === undefined
    ) {
        const empty =
            document.createElement("p");

        empty.className =
            "explanation-empty";

        empty.textContent =
            "No TicketExplanation result was returned.";

        explanationElement.appendChild(
            empty
        );

        return;
    }


    const rawText =
        typeof response.explanation ===
        "string"
            ? response.explanation
            : JSON.stringify(
                response.explanation,
                null,
                2
            );


    /*
     * The text itself comes directly from the
     * frozen TicketExplanation runtime.
     *
     * This function changes presentation only.
     * It does not modify:
     *
     * - predictions
     * - evidence
     * - task semantics
     * - decision state
     * - lifecycle state
     * - limitations
     */

    const text =
        rawText
            .replace(/\r/g, "")
            .replace(
                /\n{3,}/g,
                "\n\n"
            )
            .trim();


    /*
     * These section headings correspond to the
     * actual TicketExplanation format observed
     * from the deployed frozen runtime.
     */

    const sectionDefinitions = [
        {
            heading: "TICKET",
            pattern: /TICKET\s+[^\n]+/i
        },
        {
            heading: "ISSUE",
            pattern: /ISSUE/i
        },
        {
            heading: "SUPPORTING EVIDENCE",
            pattern: /SUPPORTING EVIDENCE/i
        },
        {
            heading: "T4 ROUTING / ASSIGNMENT",
            pattern: /T4\s+ROUTING\s*\/\s*ASSIGNMENT/i
        },
        {
            heading: "T5 DUPLICATE EVIDENCE",
            pattern: /T5\s+DUPLICATE EVIDENCE/i
        },
        {
            heading: "T6 SEMANTIC RETRIEVAL",
            pattern: /T6\s+SEMANTIC RETRIEVAL/i
        },
        {
            heading: "T7 RESOLUTION EVIDENCE",
            pattern: /T7\s+RESOLUTION EVIDENCE/i
        },
        {
            heading: "HOW THE PIPELINE REACHED ITS DECISION",
            pattern:
                /HOW THE PIPELINE REACHED ITS DECISION/i
        },
        {
            heading: "PIPELINE DECISION",
            pattern: /PIPELINE DECISION/i
        },
        {
            heading: "WHY THIS DECISION",
            pattern: /WHY THIS DECISION/i
        },
        {
            heading: "PLAIN-ENGLISH SUMMARY",
            pattern: /PLAIN-ENGLISH SUMMARY/i
        },
        {
            heading: "SYSTEM MATURITY",
            pattern: /SYSTEM MATURITY/i
        },
        {
            heading: "INTEGRITY",
            pattern: /INTEGRITY/i
        }
    ];


    const matches = [];


    for (
        const definition
        of sectionDefinitions
    ) {
        const match =
            definition.pattern.exec(
                text
            );

        if (!match) {
            continue;
        }

        matches.push({
            index: match.index,
            end: match.index +
                match[0].length,
            heading:
                definition.heading
        });
    }


    matches.sort(
        (a, b) =>
            a.index - b.index
    );


    /*
     * Remove duplicate/overlapping matches.
     */

    const uniqueMatches = [];

    for (
        const match
        of matches
    ) {
        const previous =
            uniqueMatches[
                uniqueMatches.length - 1
            ];

        if (
            previous &&
            match.index < previous.end
        ) {
            continue;
        }

        uniqueMatches.push(
            match
        );
    }


    /*
     * If the runtime format ever changes,
     * preserve the complete original explanation
     * rather than silently losing information.
     */

    if (
        uniqueMatches.length === 0
    ) {
        const fallback =
            document.createElement(
                "pre"
            );

        fallback.className =
            "explanation-raw";

        fallback.textContent =
            rawText;

        explanationElement.appendChild(
            fallback
        );

        return;
    }


    for (
        let i = 0;
        i < uniqueMatches.length;
        i += 1
    ) {
        const current =
            uniqueMatches[i];

        const next =
            uniqueMatches[i + 1];


        const block =
            document.createElement(
                "section"
            );

        block.className =
            "explanation-block";


        const title =
            document.createElement(
                "div"
            );

        title.className =
            "explanation-block-title";

        title.textContent =
            current.heading;


        const content =
            document.createElement(
                "div"
            );

        content.className =
            "explanation-block-content";


        let bodyStart =
            current.end;

        let bodyEnd =
            next
                ? next.index
                : text.length;


        let body =
            text.slice(
                bodyStart,
                bodyEnd
            );


        /*
         * TICKET is a special case because its
         * heading includes the ticket identifier.
         */

        if (
            current.heading === "TICKET"
        ) {
            const ticketLine =
                text.slice(
                    current.index,
                    current.end
                );

            content.textContent =
                ticketLine
                    .replace(
                        /^TICKET\s*/i,
                        ""
                    )
                    .trim();
        } else {
            content.textContent =
                body
                    .replace(
                        /^[\s:|-]+/,
                        ""
                    )
                    .trim();
        }


        if (
            !content.textContent
        ) {
            content.textContent =
                "—";
        }


        block.appendChild(
            title
        );

        block.appendChild(
            content
        );

        explanationElement.appendChild(
            block
        );
    }
}


/* =========================================================
   COMPLETE RESPONSE RENDERER
   ========================================================= */'''


new_source, replacements = pattern.subn(
    lambda match: replacement,
    current,
    count=1
)


if replacements != 1:
    raise SystemExit(
        "FAIL: expected exactly one "
        "renderExplanation block; "
        f"found {replacements}"
    )


APP.write_text(
    new_source,
    encoding="utf-8"
)


print("============================================================")
print("DEPLOY-OP-036C — STRUCTURED EXPLANATION PRESENTATION")
print("============================================================")
print("STATUS: PASS")
print(f"APP_UPDATED: {APP}")
print(f"EXISTING_BACKUP_VERIFIED: {BACKUP}")
print("CURRENT_EQUALS_BACKUP_BEFORE_CHANGE: True")
print(f"RENDER_EXPLANATION_REPLACEMENTS: {replacements}")
print(f"NEW_APP_SIZE_BYTES: {APP.stat().st_size}")
print("BACKEND_MODIFIED: False")
print("FROZEN_RUNTIME_MODIFIED: False")
print("BATCH_LOGIC_MODIFIED: False")
print("T1_T11_LOGIC_MODIFIED: False")
print("EXPLANATION_DATA_MODIFIED: False")
print("EXPLANATION_PRESENTATION_MODIFIED: True")
print("============================================================")
