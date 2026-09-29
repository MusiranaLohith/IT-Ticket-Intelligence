"use strict";

/*
 * IT Ticket Intelligence System
 * Dashboard
 *
 * DEPLOY-OP-012
 *
 * Responsibilities:
 * - Collect single-ticket input
 * - Submit single tickets to FastAPI
 * - Accept JSON/CSV batch input
 * - Validate batch input internally
 * - Submit batch tickets to FastAPI
 * - Render batch results
 * - Reuse the same detailed analysis view for selected batch tickets
 * - Render T1-T11 evidence
 * - Preserve the human-decision boundary
 *
 * This file does NOT:
 * - implement ML logic
 * - duplicate T1-T11 logic
 * - fabricate predictions
 * - calculate confidence
 * - calculate risk
 * - modify the frozen runtime
 * - establish production authorization
 */

const API_BASE_URL = "http://127.0.0.1:8000";

const TASK_IDS = [
    "T1",
    "T2",
    "T3",
    "T4",
    "T5",
    "T6",
    "T7",
    "T8",
    "T9",
    "T10",
    "T11"
];

const REQUIRED_TICKET_FIELDS = [
    "ticket_id",
    "creation_time",
    "creator",
    "creator_detail",
    "summary",
    "description"
];


/* =========================================================
   DOM REFERENCES
   ========================================================= */

const form =
    document.getElementById("ticket-form");

const analyzeButton =
    document.getElementById("analyze-ticket-button") ||
    document.getElementById("analyze-button");

const errorMessage =
    document.getElementById("error-message");

const resultSection =
    document.getElementById("results-panel");

const evidenceSection =
    document.getElementById("evidence-section");

const pipelineSection =
    document.getElementById("pipeline-section");

const reviewSection =
    document.getElementById("human-review-content");

const limitationsSection =
    document.getElementById("limitations-section");

const explanationSection =
    document.getElementById("explanation-section");

const batchFileInput =
    document.getElementById("batch-file");

const batchButton =
    document.getElementById("batch-validate-button") ||
    document.getElementById("batch-analyze-button");

const batchStatus =
    document.getElementById("batch-validation-summary") ||
    document.getElementById("batch-status");

const batchResultsPanel =
    document.getElementById("batch-results-panel");

const batchResultsTable =
    document.getElementById("batch-results-table");

const batchResultsTableBody =
    document.getElementById("batch-results-table-body");

const batchFileName =
    document.getElementById("batch-file-name");

const batchResultsAnalyzed =
    document.getElementById("batch-results-analyzed");


/*
 * Some earlier frontend versions used slightly different
 * batch button/status IDs. Resolve those safely if present.
 */
const resolvedBatchButton =
    batchButton ||
    document.getElementById("validate-batch-button");

const resolvedBatchStatus =
    batchStatus ||
    document.getElementById("batch-validation-status");


/* =========================================================
   STATE
   ========================================================= */

let selectedBatchFile = null;

let currentBatchTickets = [];

let currentBatchResponse = null;


/* =========================================================
   GENERAL UI
   ========================================================= */

function showError(message) {
    if (!errorMessage) {
        return;
    }

    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}


function clearError() {
    if (!errorMessage) {
        return;
    }

    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}


function setLoadingState(isLoading) {
    if (!analyzeButton) {
        return;
    }

    analyzeButton.disabled = isLoading;

    analyzeButton.textContent =
        isLoading
            ? "ANALYZING..."
            : "ANALYZE TICKET";
}


function setBatchLoadingState(isLoading) {
    if (!resolvedBatchButton) {
        return;
    }

    resolvedBatchButton.disabled = isLoading;

    resolvedBatchButton.textContent =
        isLoading
            ? "ANALYZING BATCH..."
            : "ANALYZE BATCH";
}


function setBatchStatus(message, isError = false) {
    if (!resolvedBatchStatus) {
        return;
    }

    resolvedBatchStatus.textContent = message;

    resolvedBatchStatus.classList.toggle(
        "error-message",
        isError
    );

    resolvedBatchStatus.classList.remove("hidden");
}


function hideBatchStatus() {
    if (!resolvedBatchStatus) {
        return;
    }

    resolvedBatchStatus.textContent = "";
    resolvedBatchStatus.classList.add("hidden");
}


function hideResults() {
    if (resultSection) {
        resultSection.classList.add("hidden");
    }

    if (evidenceSection) {
        evidenceSection.classList.add("hidden");
    }

    if (pipelineSection) {
        pipelineSection.classList.add("hidden");
    }

    if (reviewSection) {
        reviewSection.classList.add("hidden");
    }

    if (limitationsSection) {
        limitationsSection.classList.add("hidden");
    }

    if (explanationSection) {
        explanationSection.classList.add("hidden");
    }
}


function showResults() {
    if (resultSection) {
        resultSection.classList.remove("hidden");
    }

    if (evidenceSection) {
        evidenceSection.classList.remove("hidden");
    }

    if (pipelineSection) {
        pipelineSection.classList.remove("hidden");
    }

    if (reviewSection) {
        reviewSection.classList.remove("hidden");
    }

    if (limitationsSection) {
        limitationsSection.classList.remove("hidden");
    }

    if (explanationSection) {
        explanationSection.classList.remove("hidden");
    }
}


function showBatchResults() {
    if (batchResultsPanel) {
        batchResultsPanel.classList.remove("hidden");
    }

    if (batchResultsTable) {
        batchResultsTable.classList.remove("hidden");
    }
}


function hideBatchResults() {
    if (batchResultsPanel) {
        batchResultsPanel.classList.add("hidden");
    }

    if (batchResultsTableBody) {
        batchResultsTableBody.innerHTML = "";
    }
}


/* =========================================================
   VALUE HELPERS
   ========================================================= */

function stringifyValue(value) {
    if (
        value === null ||
        value === undefined
    ) {
        return "—";
    }

    if (typeof value === "object") {
        return JSON.stringify(
            value,
            null,
            2
        );
    }

    return String(value);
}


function getSemanticValue(
    task,
    keys,
    fallback = "—"
) {
    if (
        !task ||
        typeof task !== "object"
    ) {
        return fallback;
    }

    for (const key of keys) {
        const value = task[key];

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {
            return value;
        }
    }

    return fallback;
}


/* =========================================================
   SINGLE-TICKET INPUT
   ========================================================= */

function getTicketPayload() {
    return {
        ticket_id:
            document
                .getElementById("ticket_id")
                .value
                .trim(),

        creation_time:
            document
                .getElementById("creation_time")
                .value
                .trim(),

        creator:
            document
                .getElementById("creator")
                .value
                .trim(),

        creator_detail:
            document
                .getElementById("creator_detail")
                .value
                .trim(),

        summary:
            document
                .getElementById("summary")
                .value
                .trim(),

        description:
            document
                .getElementById("description")
                .value
                .trim()
    };
}


function validateTicketPayload(ticket) {
    const missingFields =
        REQUIRED_TICKET_FIELDS.filter(
            (field) => !ticket[field]
        );

    return {
        valid:
            missingFields.length === 0,

        missingFields
    };
}


/* =========================================================
   SINGLE-TICKET SUMMARY
   ========================================================= */

function renderSummary(response) {
    const tasks =
        response.tasks || {};

    const finalResult =
        response.final || {};

    const t1 =
        tasks.T1 || {};

    const t2 =
        tasks.T2 || {};

    const t3 =
        tasks.T3 || {};

    const t8 =
        tasks.T8 || {};

    const t10 =
        tasks.T10 || {};

    const t11 =
        tasks.T11 || {};


    const category =
        getSemanticValue(
            t1,
            [
                "prediction",
                "predicted_class",
                "class",
                "category",
                "result"
            ]
        );


    const priority =
        getSemanticValue(
            t2,
            [
                "prediction",
                "predicted_class",
                "priority",
                "result"
            ]
        );


    const severity =
        getSemanticValue(
            t3,
            [
                "prediction",
                "predicted_class",
                "severity",
                "result"
            ]
        );


    const evidenceState =
        getSemanticValue(
            t8,
            [
                "evidence_state",
                "support_status"
            ],
            null
        ) ||
        getSemanticValue(
            finalResult,
            [
                "evidence_state",
                "support_status"
            ],
            "—"
        );


    const requiredAction =
        getSemanticValue(
            t10,
            [
                "decision",
                "action",
                "required_action"
            ],
            null
        ) ||
        getSemanticValue(
            finalResult,
            [
                "decision",
                "action",
                "required_action"
            ],
            "—"
        );


    const lifecycle =
        getSemanticValue(
            t11,
            [
                "lifecycle_status",
                "lifecycle",
                "outcome_status",
                "feedback"
            ],
            null
        ) ||
        getSemanticValue(
            finalResult,
            [
                "lifecycle_status",
                "lifecycle",
                "outcome_status"
            ],
            "—"
        );


    document.getElementById(
        "summary-category"
    ).textContent =
        stringifyValue(category);


    document.getElementById(
        "summary-priority"
    ).textContent =
        stringifyValue(priority);


    document.getElementById(
        "summary-severity"
    ).textContent =
        stringifyValue(severity);


    document.getElementById(
        "summary-evidence-state"
    ).textContent =
        stringifyValue(evidenceState);


    document.getElementById(
        "summary-action"
    ).textContent =
        stringifyValue(requiredAction);


    document.getElementById(
        "summary-lifecycle"
    ).textContent =
        stringifyValue(lifecycle);
}


/* =========================================================
   EVIDENCE
   ========================================================= */

function createEvidenceTextCard(
    title,
    text,
    state = "normal"
) {
    const card =
        document.createElement("div");

    card.className =
        "evidence-item";

    card.dataset.state =
        state;

    const heading =
        document.createElement("h3");

    heading.textContent =
        title;


    const paragraph =
        document.createElement("p");

    paragraph.textContent =
        text;


    card.appendChild(
        heading
    );

    card.appendChild(
        paragraph
    );

    return card;
}


function createHistoricalCandidate(
    candidate
) {
    const row =
        document.createElement("div");

    row.className =
        "evidence-row";


    const main =
        document.createElement("div");

    main.className =
        "evidence-row-main";

    main.textContent =
        `Ticket ${candidate.id ?? "—"}`;


    const similarity =
        document.createElement("div");

    similarity.className =
        "evidence-row-meta";


    if (
        candidate.distance !== undefined &&
        candidate.distance !== null
    ) {
        const similarityValue =
            Math.max(
                0,
                Math.min(
                    1,
                    1 -
                        Number(
                            candidate.distance
                        )
                )
            );

        similarity.textContent =
            `Similarity ${similarityValue.toFixed(3)}`;
    } else {
        similarity.textContent =
            "Similarity —";
    }


    const assignee =
        document.createElement("div");

    assignee.className =
        "evidence-row-meta";

    assignee.textContent =
        `Historical assignee: ${
            candidate.target_assignee ?? "—"
        }`;


    const summary =
        document.createElement("div");

    summary.className =
        "evidence-row-summary";

    summary.textContent =
        candidate.summary ??
        "No historical summary available.";


    row.appendChild(main);
    row.appendChild(similarity);
    row.appendChild(assignee);
    row.appendChild(summary);

    return row;
}


function renderT4Evidence(task) {
    const card =
        document.createElement("div");

    card.className =
        "evidence-item";


    const heading =
        document.createElement("h3");

    heading.textContent =
        "Historical Routing Evidence";


    const description =
        document.createElement("p");


    const results =
        Array.isArray(task.results)
            ? task.results
            : [];


    description.textContent =
        `${results.length} historical related-ticket ` +
        `candidate${
            results.length === 1
                ? ""
                : "s"
        } were retrieved.`;


    card.appendChild(
        heading
    );

    card.appendChild(
        description
    );


    if (results.length > 0) {
        const list =
            document.createElement("div");

        list.className =
            "evidence-list";


        for (const candidate of results) {
            list.appendChild(
                createHistoricalCandidate(
                    candidate
                )
            );
        }


        card.appendChild(
            list
        );


        const note =
            document.createElement("p");

        note.className =
            "evidence-note";

        note.textContent =
            "Historical evidence only — it does not establish current operational assignment.";


        card.appendChild(
            note
        );
    }


    return card;
}


function renderT5Evidence(task) {
    const duplicateEvidence =
        task.duplicate_evidence ??
        task.probability ??
        task.score ??
        0;


    const thresholdUsed =
        task.threshold_used === true;


    const text =
        `Duplicate evidence: ${
            Number(
                duplicateEvidence
            ).toFixed(4)
        }. ` +
        (
            thresholdUsed
                ? "An operational duplicate threshold was applied."
                : "No operational duplicate threshold was applied."
        );


    return createEvidenceTextCard(
        "Duplicate Evidence",
        text
    );
}


function renderT6Evidence(task) {
    const status =
        task.status ??
        "UNAVAILABLE";


    const fullHybrid =
        task.full_mod010_hybrid_available;


    let text;


    if (fullHybrid === false) {
        text =
            "Runtime status: PARTIAL NATIVE RUNTIME. " +
            "Full MOD-010 hybrid semantic retrieval is unavailable " +
            "for this genuinely new ticket runtime. " +
            (
                task.reason ??
                "No semantic score was fabricated."
            );
    } else {
        text =
            `Runtime status: ${status}. ` +
            (
                task.reason ??
                "Native semantic evidence was preserved."
            );
    }


    return createEvidenceTextCard(
        "Semantic Evidence",
        text,
        "limited"
    );
}


function renderT7Evidence(task) {
    const median =
        task.median_seconds ??
        task.resolution_median_seconds;


    const temporalSupport =
        task.temporal_support ??
        "—";


    const creationYear =
        task.creation_year ??
        "—";


    const trainingMin =
        task.training_year_min ??
        "—";


    const trainingMax =
        task.training_year_max ??
        "—";


    const estimateText =
        median !== undefined &&
        median !== null
            ? `Median resolution-time estimate: ${
                Number(
                    median
                ).toFixed(2)
              } seconds.`
            : "Median resolution-time estimate: —.";


    const text =
        `${estimateText} ` +
        `Ticket creation year: ${creationYear}. ` +
        `Observed training range: ${trainingMin}–${trainingMax}. ` +
        `Temporal support: ${temporalSupport}.`;


    return createEvidenceTextCard(
        "Resolution Evidence",
        text,
        "limited"
    );
}


function renderT8Evidence(task) {
    const evidenceState =
        task.evidence_state ??
        "—";


    const available =
        Array.isArray(task.available)
            ? task.available.join(", ")
            : "—";


    const partial =
        Array.isArray(task.partial)
            ? task.partial.join(", ")
            : "—";


    const missingIsNotNegative =
        task.missing_evidence_is_not_negative === true;


    const text =
        `Integrated evidence state: ${evidenceState}. ` +
        `Available: ${available}. ` +
        `Partial: ${partial}. ` +
        (
            missingIsNotNegative
                ? "Missing evidence is not treated as negative evidence."
                : ""
        );


    return createEvidenceTextCard(
        "Evidence Integration",
        text,
        "limited"
    );
}


function renderEvidence(response) {
    const container =
        document.getElementById(
            "evidence-content"
        );

    container.innerHTML = "";


    const tasks =
        response.tasks || {};


    if (tasks.T4) {
        container.appendChild(
            renderT4Evidence(
                tasks.T4
            )
        );
    }


    if (tasks.T5) {
        container.appendChild(
            renderT5Evidence(
                tasks.T5
            )
        );
    }


    if (tasks.T6) {
        container.appendChild(
            renderT6Evidence(
                tasks.T6
            )
        );
    }


    if (tasks.T7) {
        container.appendChild(
            renderT7Evidence(
                tasks.T7
            )
        );
    }


    if (tasks.T8) {
        container.appendChild(
            renderT8Evidence(
                tasks.T8
            )
        );
    }


    if (!container.children.length) {
        container.appendChild(
            createEvidenceTextCard(
                "Evidence",
                "No evidence section data was returned."
            )
        );
    }
}


/* =========================================================
   PIPELINE TRACE
   ========================================================= */

function getTaskDisplayState(
    taskId,
    task
) {
    if (!task) {
        return "UNAVAILABLE";
    }


    switch (taskId) {
        case "T6":
            if (
                task.full_mod010_hybrid_available === false
            ) {
                return "PARTIAL NATIVE RUNTIME";
            }

            return getSemanticValue(
                task,
                [
                    "support_status",
                    "status"
                ],
                "EXECUTED"
            );


        case "T7":
            return getSemanticValue(
                task,
                [
                    "temporal_support",
                    "status"
                ],
                "EXECUTED"
            );


        case "T8":
            return getSemanticValue(
                task,
                [
                    "evidence_state",
                    "support_status",
                    "status"
                ],
                "EXECUTED"
            );


        case "T10":
            return getSemanticValue(
                task,
                [
                    "decision",
                    "action",
                    "required_action"
                ],
                "EXECUTED"
            );


        case "T11":
            return getSemanticValue(
                task,
                [
                    "lifecycle_status",
                    "lifecycle",
                    "outcome_status",
                    "feedback"
                ],
                "EXECUTED"
            );


        default:
            return getSemanticValue(
                task,
                [
                    "status",
                    "execution_status"
                ],
                "EXECUTED"
            );
    }
}


function getTaskTitle(taskId) {
    const titles = {
        T1: "CATEGORY",
        T2: "PRIORITY",
        T3: "SEVERITY",
        T4: "ROUTING",
        T5: "DUPLICATE",
        T6: "SEMANTIC",
        T7: "RESOLUTION",
        T8: "INTEGRATION",
        T9: "SEMANTICS",
        T10: "SYSTEM ACTION",
        T11: "LIFECYCLE"
    };

    return (
        titles[taskId] ||
        "TASK"
    );
}


function getTaskStateClass(
    taskId,
    task
) {
    if (!task) {
        return "";
    }


    if (
        taskId === "T6" &&
        task.full_mod010_hybrid_available === false
    ) {
        return "limited";
    }


    if (
        taskId === "T7" &&
        typeof task.temporal_support === "string" &&
        task.temporal_support !== "SUPPORTED"
    ) {
        return "limited";
    }


    if (
        taskId === "T8" &&
        task.evidence_state ===
            "SUPPORTED_WITH_LIMITATIONS"
    ) {
        return "limited";
    }


    if (taskId === "T10") {
        return "human-action";
    }


    if (taskId === "T11") {
        return "lifecycle";
    }


    return "";
}


function getTaskDescription(
    taskId,
    task
) {
    switch (taskId) {
        case "T1":
            return "Category evidence produced.";


        case "T2":
            return "Priority evidence produced.";


        case "T3":
            return "Severity evidence produced.";


        case "T4": {
            const count =
                Array.isArray(
                    task?.results
                )
                    ? task.results.length
                    : 0;


            return (
                `${count} historical related-ticket ` +
                `candidate${
                    count === 1
                        ? ""
                        : "s"
                } retrieved.`
            );
        }


        case "T5":
            return (
                `Duplicate evidence: ${
                    Number(
                        task?.duplicate_evidence ?? 0
                    ).toFixed(4)
                }.`
            );


        case "T6":
            if (
                task?.full_mod010_hybrid_available === false
            ) {
                return "PARTIAL NATIVE RUNTIME";
            }

            return "Semantic evidence available.";


        case "T7":
            return (
                task?.temporal_support ??
                "Resolution evidence produced."
            );


        case "T8":
            return (
                task?.evidence_state ??
                "Evidence integration completed."
            );


        case "T9":
            return "Native task semantics preserved.";


        case "T10":
            return (
                task?.action ??
                task?.decision ??
                "HUMAN_DECISION_REQUIRED"
            );


        case "T11":
            return (
                task?.feedback ??
                task?.lifecycle ??
                task?.lifecycle_status ??
                "AWAITING_OUTCOME"
            );


        default:
            return getTaskDisplayState(
                taskId,
                task
            );
    }
}


function renderPipeline(response) {
    const container =
        document.getElementById(
            "pipeline-content"
        );

    container.innerHTML = "";


    const tasks =
        response.tasks || {};


    for (const taskId of TASK_IDS) {
        const task =
            tasks[taskId];


        const card =
            document.createElement("div");

        card.className =
            "pipeline-card";


        const stateClass =
            getTaskStateClass(
                taskId,
                task
            );


        if (stateClass) {
            card.dataset.state =
                stateClass;
        }


        const taskLabel =
            document.createElement("span");

        taskLabel.className =
            "task-id";

        taskLabel.textContent =
            taskId;


        const taskTitle =
            document.createElement("strong");

        taskTitle.textContent =
            getTaskTitle(
                taskId
            );


        const taskState =
            document.createElement("span");

        taskState.className =
            "task-state";

        taskState.textContent =
            getTaskDisplayState(
                taskId,
                task
            );


        const description =
            document.createElement("p");

        description.textContent =
            getTaskDescription(
                taskId,
                task
            );        card.appendChild(
            taskLabel
        );

        card.appendChild(
            taskTitle
        );

        card.appendChild(
            taskState
        );

        // Show the description only when it adds information
        // beyond the displayed task state.
        if (
            description.textContent.trim() !==
            taskState.textContent.trim()
        ) {
            card.appendChild(
                description
            );
        }


        container.appendChild(
            card
        );
    }
}


/* =========================================================
   LIMITATIONS
   ========================================================= */

function renderLimitations(response) {
    const list =
        document.getElementById(
            "limitations-content"
        );

    list.innerHTML = "";


    const tasks =
        response.tasks || {};


    const limitations = [];


    if (
        tasks.T4
    ) {
        limitations.push(
            "T4 provides historical retrieval evidence only; it does not establish current operational assignment."
        );
    }


    if (
        tasks.T5
    ) {
        limitations.push(
            "T5 duplicate evidence does not establish an operational duplicate decision unless an explicit threshold exists."
        );
    }


    if (
        tasks.T6
    ) {
        limitations.push(
            "T6 may provide only partial native semantic runtime evidence for a genuinely new ticket."
        );
    }


    if (
        tasks.T7
    ) {
        limitations.push(
            "T7 resolution evidence may carry a temporal-support limitation when the ticket lies outside the observed training range."
        );
    }


    if (
        tasks.T8
    ) {
        limitations.push(
            "T8 preserves native evidence semantics; missing evidence is not treated as negative evidence."
        );
    }


    if (
        tasks.T9
    ) {
        limitations.push(
            "T9 does not establish a universal cross-task confidence or risk score."
        );
    }


    if (
        tasks.T10
    ) {
        limitations.push(
            "T10 preserves the human-decision boundary."
        );
    }


    if (
        tasks.T11
    ) {
        limitations.push(
            "T11 remains at the appropriate lifecycle boundary until a genuine human outcome exists."
        );
    }


    for (
        const limitation
        of limitations
    ) {
        const item =
            document.createElement("li");

        item.textContent =
            limitation;

        list.appendChild(
            item
        );
    }
}


/* =========================================================
   HUMAN REVIEW
   ========================================================= */

function renderReviewBoundary(
    response
) {
    const t10 =
        response.tasks?.T10 || {};

    const t11 =
        response.tasks?.T11 || {};

    const action =
        t10.action ??
        t10.decision ??
        "HUMAN_DECISION_REQUIRED";

    const lifecycle =
        t11.lifecycle_status ??
        t11.lifecycle ??
        t11.feedback ??
        "AWAITING_OUTCOME";


    const reviewSectionElement =
        document.getElementById(
            "human-review-content"
        );

    if (!reviewSectionElement) {
        return;
    }


    const existing =
        reviewSectionElement.querySelector(
            ".review-runtime-status"
        );


    if (existing) {
        existing.remove();
    }


    const status =
        document.createElement("div");

    status.className =
        "review-runtime-status";


    const systemLine =
        document.createElement("p");

    systemLine.textContent =
        "System action: " +
        stringifyValue(action);


    const humanLine =
        document.createElement("p");

    humanLine.textContent =
        "Human review boundary: the system provides evidence; the human makes the operational decision.";


    const lifecycleLine =
        document.createElement("p");

    lifecycleLine.textContent =
        "Lifecycle: " +
        stringifyValue(lifecycle);


    status.appendChild(
        systemLine
    );

    status.appendChild(
        humanLine
    );

    status.appendChild(
        lifecycleLine
    );


    reviewSectionElement.appendChild(
        status
    );
}


/* =========================================================
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
   ========================================================= */

function renderAnalysisResponse(
    response
) {
    if (
        !response ||
        typeof response !== "object"
    ) {
        throw new Error(
            "Invalid analysis response."
        );
    }


    renderSummary(
        response
    );

    renderEvidence(
        response
    );

    renderPipeline(
        response
    );

    renderLimitations(
        response
    );

    renderReviewBoundary(
        response
    );

    renderExplanation(
        response
    );


    showResults();


    /*
     * When a batch row is selected, bring the
     * detailed analysis view into focus.
     */
    if (
        currentBatchResponse !== null
    ) {
        if (
            resultSection &&
            typeof resultSection.scrollIntoView ===
                "function"
        ) {
            resultSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    }
}


/* =========================================================
   SINGLE-TICKET API
   ========================================================= */

async function analyzeTicket(
    ticket
) {
    const response =
        await fetch(
            `${API_BASE_URL}/tickets/analyze`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        ticket
                    )
            }
        );


    let responseBody;


    try {
        responseBody =
            await response.json();
    } catch (error) {
        throw new Error(
            `API returned HTTP ${response.status}, ` +
            "but the response was not valid JSON."
        );
    }


    if (!response.ok) {
        const detail =
            responseBody &&
            responseBody.detail
                ? responseBody.detail
                : "API request failed.";


        throw new Error(
            `API request failed with HTTP ${response.status}: ` +
            `${stringifyValue(detail)}`
        );
    }


    return responseBody;
}


/* =========================================================
   SINGLE-TICKET FORM SUBMISSION
   ========================================================= */

async function handleFormSubmit(
    event
) {
    event.preventDefault();


    clearError();

    hideResults();


    const ticket =
        getTicketPayload();


    const validation =
        validateTicketPayload(
            ticket
        );


    if (!validation.valid) {
        showError(
            "Please provide all required ticket fields: " +
            validation.missingFields.join(
                ", "
            )
        );

        return;
    }


    setLoadingState(
        true
    );


    try {
        const response =
            await analyzeTicket(
                ticket
            );


        currentBatchResponse =
            null;


        renderAnalysisResponse(
            response
        );


        console.info(
            "DEPLOY-OP-012 single-ticket analysis completed.",
            response
        );
    } catch (error) {
        console.error(
            "DEPLOY-OP-012 single-ticket analysis failed.",
            error
        );


        showError(
            error instanceof Error
                ? error.message
                : "Unable to analyze the ticket."
        );
    } finally {
        setLoadingState(
            false
        );
    }
}


/* =========================================================
   BATCH FILE PARSING
   ========================================================= */

function parseCSVLine(
    line
) {
    const values = [];

    let current = "";

    let insideQuotes =
        false;


    for (
        let index = 0;
        index < line.length;
        index += 1
    ) {
        const character =
            line[index];


        if (
            character === '"'
        ) {
            if (
                insideQuotes &&
                line[index + 1] === '"'
            ) {
                current += '"';
                index += 1;
            } else {
                insideQuotes =
                    !insideQuotes;
            }

            continue;
        }


        if (
            character === "," &&
            !insideQuotes
        ) {
            values.push(
                current.trim()
            );

            current = "";

            continue;
        }


        current +=
            character;
    }


    values.push(
        current.trim()
    );


    return values;
}


function parseCSV(
    text
) {
    const lines =
        text
            .split(/\r?\n/)
            .filter(
                (line) =>
                    line.trim() !== ""
            );


    if (!lines.length) {
        throw new Error(
            "CSV file is empty."
        );
    }


    const headers =
        parseCSVLine(
            lines[0]
        );


    const normalizedHeaders =
        headers.map(
            (header) =>
                header
                    .trim()
                    .replace(/^"|"$/g, "")
        );


    const missingHeaders =
        REQUIRED_TICKET_FIELDS.filter(
            (field) =>
                !normalizedHeaders.includes(
                    field
                )
        );


    if (
        missingHeaders.length > 0
    ) {
        throw new Error(
            "CSV is missing required fields: " +
            missingHeaders.join(", ")
        );
    }


    const tickets = [];


    for (
        let rowIndex = 1;
        rowIndex < lines.length;
        rowIndex += 1
    ) {
        const values =
            parseCSVLine(
                lines[rowIndex]
            );


        const ticket = {};


        for (
            let columnIndex = 0;
            columnIndex <
                normalizedHeaders.length;
            columnIndex += 1
        ) {
            ticket[
                normalizedHeaders[
                    columnIndex
                ]
            ] =
                values[columnIndex] ??
                "";
        }


        tickets.push(
            ticket
        );
    }


    return tickets;
}


function parseJSONBatch(
    text
) {
    let parsed;


    try {
        parsed =
            JSON.parse(
                text
            );
    } catch (error) {
        throw new Error(
            "Selected file is not valid JSON."
        );
    }


    if (
        Array.isArray(parsed)
    ) {
        return parsed;
    }


    if (
        parsed &&
        Array.isArray(
            parsed.tickets
        )
    ) {
        return parsed.tickets;
    }


    throw new Error(
        "JSON must be an array of ticket objects or an object containing a tickets array."
    );
}


function validateBatchTickets(
    tickets
) {
    if (
        !Array.isArray(tickets)
    ) {
        return {
            valid: false,
            message:
                "Batch input must contain a ticket array."
        };
    }


    if (
        tickets.length === 0
    ) {
        return {
            valid: false,
            message:
                "Batch input contains no tickets."
        };
    }


    const errors = [];


    tickets.forEach(
        (
            ticket,
            index
        ) => {
            if (
                !ticket ||
                typeof ticket !==
                    "object" ||
                Array.isArray(ticket)
            ) {
                errors.push(
                    `Ticket ${index + 1} is not a valid object.`
                );

                return;
            }


            const missingFields =
                REQUIRED_TICKET_FIELDS.filter(
                    (field) =>
                        ticket[field] ===
                            undefined ||
                        ticket[field] ===
                            null ||
                        String(
                            ticket[field]
                        ).trim() === ""
                );


            if (
                missingFields.length > 0
            ) {
                errors.push(
                    `Ticket ${
                        index + 1
                    } is missing: ${
                        missingFields.join(
                            ", "
                        )
                    }`
                );
            }
        }
    );


    if (
        errors.length > 0
    ) {
        return {
            valid: false,
            message:
                errors.join(" ")
        };
    }


    return {
        valid: true,
        message:
            `${tickets.length} tickets validated and ready for batch analysis.`
    };
}


async function parseBatchFile(
    file
) {
    const text =
        await file.text();


    const filename =
        file.name.toLowerCase();


    let tickets;


    if (
        filename.endsWith(".json")
    ) {
        tickets =
            parseJSONBatch(
                text
            );
    } else if (
        filename.endsWith(".csv")
    ) {
        tickets =
            parseCSV(
                text
            );
    } else {
        throw new Error(
            "Unsupported file type. Please select a JSON or CSV file."
        );
    }


    const validation =
        validateBatchTickets(
            tickets
        );


    if (
        !validation.valid
    ) {
        throw new Error(
            validation.message
        );
    }


    return tickets;
}


/* =========================================================
   BATCH API
   ========================================================= */

async function analyzeBatch(
    tickets
) {
    const response =
        await fetch(
            `${API_BASE_URL}/tickets/analyze-batch`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify({
                        tickets
                    })
            }
        );


    let responseBody;


    try {
        responseBody =
            await response.json();
    } catch (error) {
        throw new Error(
            `Batch API returned HTTP ${response.status}, ` +
            "but the response was not valid JSON."
        );
    }


    if (!response.ok) {
        const detail =
            responseBody &&
            responseBody.detail
                ? responseBody.detail
                : "Batch API request failed.";


        throw new Error(
            `Batch API request failed with HTTP ${response.status}: ` +
            `${stringifyValue(detail)}`
        );
    }


    if (
        !responseBody ||
        !Array.isArray(
            responseBody.results
        )
    ) {
        throw new Error(
            "Batch API returned an invalid result structure."
        );
    }


    return responseBody;
}


/* =========================================================
   BATCH RESULT HELPERS
   ========================================================= */

function getBatchCategory(
    ticketResponse
) {
    return getSemanticValue(
        ticketResponse?.tasks?.T1,
        [
            "prediction",
            "predicted_class",
            "class",
            "category",
            "result"
        ]
    );
}


function getBatchPriority(
    ticketResponse
) {
    return getSemanticValue(
        ticketResponse?.tasks?.T2,
        [
            "prediction",
            "predicted_class",
            "priority",
            "result"
        ]
    );
}


function getBatchSeverity(
    ticketResponse
) {
    return getSemanticValue(
        ticketResponse?.tasks?.T3,
        [
            "prediction",
            "predicted_class",
            "severity",
            "result"
        ]
    );
}


function getBatchEvidenceState(
    ticketResponse
) {
    const t8 =
        ticketResponse?.tasks?.T8 ||
        {};

    const finalResult =
        ticketResponse?.final ||
        {};


    return (
        getSemanticValue(
            t8,
            [
                "evidence_state",
                "support_status"
            ],
            null
        ) ||
        getSemanticValue(
            finalResult,
            [
                "evidence_state",
                "support_status"
            ],
            "—"
        )
    );
}


function getBatchAction(
    ticketResponse
) {
    const t10 =
        ticketResponse?.tasks?.T10 ||
        {};

    const finalResult =
        ticketResponse?.final ||
        {};


    return (
        getSemanticValue(
            t10,
            [
                "decision",
                "action",
                "required_action"
            ],
            null
        ) ||
        getSemanticValue(
            finalResult,
            [
                "decision",
                "action",
                "required_action"
            ],
            "—"
        )
    );
}


function createBatchResultRow(
    ticketResponse,
    index
) {
    const row =
        document.createElement("tr");


    row.className =
        "batch-result-row";


    row.tabIndex =
        0;


    row.dataset.index =
        String(index);


    const ticketId =
        ticketResponse?.ticket?.ticket_id ??
        "—";


    const values = [
        ticketId,
        getBatchCategory(
            ticketResponse
        ),
        getBatchPriority(
            ticketResponse
        ),
        getBatchSeverity(
            ticketResponse
        ),
        getBatchEvidenceState(
            ticketResponse
        ),
        getBatchAction(
            ticketResponse
        )
    ];


    for (
        const value
        of values
    ) {
        const cell =
            document.createElement("td");

        cell.textContent =
            stringifyValue(
                value
            );

        row.appendChild(
            cell
        );
    }


    const openDetails =
        () => {
            selectBatchTicket(
                index
            );
        };


    row.addEventListener(
        "click",
        openDetails
    );


    row.addEventListener(
        "keydown",
        (event) => {
            if (
                event.key ===
                    "Enter" ||
                event.key ===
                    " "
            ) {
                event.preventDefault();

                openDetails();
            }
        }
    );


    return row;
}


function renderBatchResults(
    response
) {
    if (
        !batchResultsTableBody
    ) {
        return;
    }


    batchResultsTableBody.innerHTML = "";


    const results =
        Array.isArray(
            response.results
        )
            ? response.results
            : [];

    if (batchResultsAnalyzed) {
        batchResultsAnalyzed.textContent =
            String(results.length);
    }


    results.forEach(
        (
            ticketResponse,
            index
        ) => {
            batchResultsTableBody.appendChild(
                createBatchResultRow(
                    ticketResponse,
                    index
                )
            );
        }
    );


    showBatchResults();
}


function selectBatchTicket(
    index
) {
    if (
        !currentBatchResponse
    ) {
        return;
    }


    const results =
        currentBatchResponse.results;


    if (
        !Array.isArray(results) ||
        !results[index]
    ) {
        return;
    }


    const ticketResponse =
        results[index];


    currentBatchResponse =
        currentBatchResponse;


    /*
     * Reuse the existing detailed
     * single-ticket renderer.
     *
     * No second analysis request is made.
     * The already-returned ticket result
     * is rendered directly.
     */
    renderAnalysisResponse(
        ticketResponse
    );


    console.info(
        "Batch ticket selected:",
        ticketResponse?.ticket?.ticket_id
    );
}


/* =========================================================
   BATCH WORKFLOW
   ========================================================= */

/*
 * IMPORTANT:
 *
 * There is intentionally NO separate
 * "validate then analyze" button state.
 *
 * One click performs:
 *
 * file selection
 *      ↓
 * internal parsing
 *      ↓
 * internal validation
 *      ↓
 * batch API request
 *      ↓
 * batch result table
 */
async function handleBatchAnalysis() {
    clearError();
    hideBatchStatus();


    if (
        !batchFileInput
    ) {
        showError(
            "Batch file input is not available."
        );

        return;
    }


    const file =
        batchFileInput.files?.[0];


    if (!file) {
        showError(
            "Please select a JSON or CSV batch file."
        );

        return;
    }


    hideResults();
    hideBatchResults();


    setBatchLoadingState(
        true
    );


    try {
        setBatchStatus(
            "Validating batch input..."
        );


        const tickets =
            await parseBatchFile(
                file
            );


        currentBatchTickets =
            tickets;


        setBatchStatus(
            `${tickets.length} tickets validated. Running batch analysis...`
        );


        const response =
            await analyzeBatch(
                tickets
            );


        currentBatchResponse =
            response;


        renderBatchResults(
            response
        );


        const summary =
            response.batch || {};


        const submitted =
            summary.submitted ??
            tickets.length;


        const analyzed =
            summary.analyzed ??
            response.results.length;


        const failed =
            summary.failed ??
            0;


        setBatchStatus(
            `${response.results.length} batch tickets analyzed successfully — ` +
            `submitted: ${submitted}, ` +
            `analyzed: ${analyzed}, ` +
            `failed: ${failed}.`
        );


        console.info(
            "DEPLOY-OP-012 batch analysis completed.",
            response
        );
    } catch (error) {
        currentBatchTickets =
            [];

        currentBatchResponse =
            null;


        console.error(
            "DEPLOY-OP-012 batch analysis failed.",
            error
        );


        setBatchStatus(
            error instanceof Error
                ? error.message
                : "Unable to analyze the batch.",
            true
        );


        showError(
            error instanceof Error
                ? error.message
                : "Unable to analyze the batch."
        );
    } finally {
        setBatchLoadingState(
            false
        );
    }
}


/* =========================================================
   FILE SELECTION
   ========================================================= */

function handleBatchFileChange() {
    clearError();
    hideBatchStatus();
    hideBatchResults();


    currentBatchTickets =
        [];

    currentBatchResponse =
        null;


    const file =
        batchFileInput?.files?.[0];


    selectedBatchFile =
        file || null;


    if (!file) {
        if (resolvedBatchButton) {
            resolvedBatchButton.disabled = true;
            resolvedBatchButton.textContent =
                "ANALYZE BATCH";
        }

        if (batchFileName) {
            batchFileName.textContent =
                "No file selected.";
        }

        return;
    }


    if (resolvedBatchButton) {
        resolvedBatchButton.disabled = false;
        resolvedBatchButton.textContent =
            "ANALYZE BATCH";
    }

    if (batchFileName) {
        batchFileName.textContent =
            `Selected file: ${file.name}`;
    }


    setBatchStatus(
        `Selected file: ${file.name}`
    );
}


/* =========================================================
   RESET
   ========================================================= */

function resetDashboard() {
    hideResults();

    hideBatchResults();

    clearError();

    hideBatchStatus();


    currentBatchTickets =
        [];

    currentBatchResponse =
        null;
}


/* =========================================================
   EVENT LISTENERS
   ========================================================= */

if (form) {
    form.addEventListener(
        "submit",
        handleFormSubmit
    );
}


if (batchFileInput) {
    batchFileInput.addEventListener(
        "change",
        handleBatchFileChange
    );
}


if (resolvedBatchButton) {
    /*
     * The batch button now ALWAYS means:
     * ANALYZE BATCH
     *
     * Validation is performed internally.
     */
    resolvedBatchButton.addEventListener(
        "click",
        (event) => {
            event.preventDefault();

            handleBatchAnalysis();
        }
    );
}


/* =========================================================
   INITIAL STATE
   ========================================================= */

hideResults();

hideBatchResults();

hideBatchStatus();


if (resolvedBatchButton) {
    resolvedBatchButton.disabled =
        !batchFileInput?.files?.[0];

    resolvedBatchButton.textContent =
        "ANALYZE BATCH";
}


/* =========================================================
   PUBLIC DEBUG / TEST INTERFACE
   ========================================================= */

window.ITTicketDashboard = {
    getTicketPayload,
    validateTicketPayload,
    analyzeTicket,
    analyzeBatch,
    validateBatchTickets,
    parseJSONBatch,
    parseCSV,
    renderAnalysisResponse,
    renderBatchResults,
    selectBatchTicket,
    resetDashboard
};


console.info(
    "IT Ticket Intelligence System dashboard loaded — DEPLOY-OP-012."
);

/* ============================================================
   DEPLOY-OP-047 — PROJECT INFORMATION ARCHITECTURE
   ------------------------------------------------------------
   Navigation only.
   Does not modify ticket analysis, batch processing,
   rendering, pipeline logic, API calls, or model behaviour.
   ============================================================ */

/* ============================================================
   DEPLOY-OP-056 — FIXED VIEWPORT HOME + WORKSPACE NAVIGATION
   ------------------------------------------------------------
   Home and Research Workspace behave as fixed application views.
   Analysis Workspace retains normal document scrolling.
   ============================================================ */

function applyApplicationViewState(view) {
    document.body.classList.remove(
        "app-view-landing",
        "app-view-workspace",
        "app-view-analysis",
        "app-view-research"
    );

    document.body.classList.add(view);
}


function showProjectLanding() {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );

    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }

    landing.classList.remove("hidden");
    home.classList.add("hidden");
    analysis.classList.add("hidden");
    research.classList.add("hidden");

    applyApplicationViewState(
        "app-view-landing"
    );
}


function showWorkspaceHome() {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );

    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }

    landing.classList.add("hidden");
    home.classList.remove("hidden");
    analysis.classList.add("hidden");
    research.classList.add("hidden");

    applyApplicationViewState(
        "app-view-workspace"
    );
}


function showAnalysisWorkspace(targetId = null) {
    const landing = document.getElementById(
        "project-landing"
    );

    const home = document.getElementById(
        "workspace-home"
    );

    const analysis = document.getElementById(
        "analysis-workspace"
    );

    const research = document.getElementById(
        "research-overview"
    );

    if (
        !landing ||
        !home ||
        !analysis ||
        !research
    ) {
        return;
    }

    landing.classList.add("hidden");
    home.classList.add("hidden");
    analysis.classList.remove("hidden");
    research.classList.add("hidden");

    applyApplicationViewState(
        "app-view-analysis"
    );

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    if (targetId) {
        window.setTimeout(() => {
            const target =
                document.getElementById(targetId);

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }, 120);
    }
}



    /* ============================================================
       DEPLOY-OP-067 — RESEARCH VIEW NAVIGATION
       ------------------------------------------------------------
       Research presentation navigation only.
       Does not modify ticket analysis, batch processing,
       rendering, API calls, or model behaviour.
       ============================================================ */

    function showResearchOverview() {

        const landing = document.getElementById(
            "project-landing"
        );

        const home = document.getElementById(
            "workspace-home"
        );

        const analysis = document.getElementById(
            "analysis-workspace"
        );

        const research = document.getElementById(
            "research-overview"
        );

        if (
            !landing ||
            !home ||
            !analysis ||
            !research
        ) {
            return;
        }

        landing.classList.add("hidden");
        home.classList.add("hidden");
        analysis.classList.add("hidden");
        research.classList.remove("hidden");

        applyApplicationViewState(
            "app-view-research"
        );

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
    

function initializeProjectNavigation() {
    const enterSystemButton =
        document.getElementById(
            "enter-system-button"
        );

    const viewResearchButton =
        document.getElementById(
            "view-research-button"
        );

    const openAnalysisWorkspaceButton =
        document.getElementById(
            "open-analysis-workspace-button"
        );

    const workspaceHomeButton =
        document.getElementById(
            "workspace-home-button"
        );

    const analysisHomeButton =
        document.getElementById(
            "analysis-home-button"
        );

    const projectOverviewButton =
        document.getElementById(
            "project-overview-button"
        );

    const resetDashboardButton =
        document.getElementById(
            "reset-dashboard-button"
        );


    if (enterSystemButton) {
        enterSystemButton.addEventListener(
            "click",
            showWorkspaceHome
        );
    }


    if (viewResearchButton) {
            viewResearchButton.addEventListener(
                "click",
                showResearchOverview
            );
        }
    

        const researchHomeButton =
            document.getElementById(
                "research-home-button"
            );

        const researchHomeFooterButton =
            document.getElementById(
                "research-home-button-footer"
            );

        if (researchHomeButton) {
            researchHomeButton.addEventListener(
                "click",
                showProjectLanding
            );
        }

        if (researchHomeFooterButton) {
            researchHomeFooterButton.addEventListener(
                "click",
                showProjectLanding
            );
        }
    

    if (openAnalysisWorkspaceButton) {
        openAnalysisWorkspaceButton.addEventListener(
            "click",
            showAnalysisWorkspace
        );
    }

    if (workspaceHomeButton) {
        workspaceHomeButton.addEventListener(
            "click",
            showProjectLanding
        );
    }


    if (analysisHomeButton) {
        analysisHomeButton.addEventListener(
            "click",
            showWorkspaceHome
        );
    }


    if (projectOverviewButton) {
        projectOverviewButton.addEventListener(
            "click",
            showProjectLanding
        );
    }


    if (resetDashboardButton) {
        resetDashboardButton.addEventListener(
            "click",
            () => {
                window.setTimeout(
                    showWorkspaceHome,
                    50
                );
            }
        );
    }


    showProjectLanding();
}


initializeProjectNavigation();


/* ============================================================
   END DEPLOY-OP-056
   ============================================================ */
