# IT Ticket Intelligence

## IT Ticket Decision Support & Triage System

An evidence-first machine learning and decision-support system for analysing IT support tickets through a traceable T1–T11 task pipeline.

The project takes a real-world IT support problem through a controlled ML engineering and research workflow, covering dataset investigation, audits, formal dataset contracts, dataset-to-task mapping, task-specific modelling, evidence preservation, evidence integration, human decision boundaries, and local deployment.

---

## Problem

IT support tickets are noisy, partially structured, and historically evolving. Different operational questions therefore require different forms of evidence and modelling rather than a single universal prediction.

This project investigates ticket classification, priority and severity assessment, historical routing evidence, duplicate detection, similar-ticket retrieval, resolution-time analysis, evidence integration, task-specific uncertainty, human review boundaries, and feedback lifecycle considerations.

---

## Research and Engineering Workflow

### Dataset Investigation

Multiple real-world software-support datasets were investigated for provenance, structure, identifiers, temporal coverage, duplicates, missingness, historical fields, target availability, and potential leakage.

### Audits

Dataset integrity, provenance, structural consistency, temporal behaviour, duplicate structure, and leakage risks were examined before modelling.

### Formal Dataset Contract

A Formal Dataset Contract was established to document the conditions under which each dataset can legitimately support a modelling task.

This includes target definitions, feature availability, temporal constraints, creation-time information, post-creation information, split requirements, missing evidence, and provenance.

### Dataset-to-Task Mapping

Datasets were evaluated task-by-task rather than assuming that a dataset supports every modelling objective.

This established which populations could provide valid evidence for each T1–T11 task and what limitations applied.

### Task-Specific Modelling

The modelling workflow uses different approaches according to the task, including classification, duplicate analysis, retrieval and ranking, calibration analysis, and survival/time-to-event modelling.

### Evidence Preservation

Task outputs retain their native meaning, evidence grain, uncertainty, missingness, provenance and limitations.

The system does not collapse heterogeneous task outputs into a universal confidence or risk score.

### Evidence Integration

Evidence from the individual tasks is brought together while preserving the identity and limitations of each evidence source.

### Human Decision Boundary

The system is designed for decision support. System findings and evidence are presented separately from the operational decision made by a human reviewer.

---

## T1–T11

| Task | Capability |
|---|---|
| T1 | Ticket classification |
| T2 | Priority prediction |
| T3 | Severity prediction |
| T4 | Historical routing / assignment evidence |
| T5 | Duplicate detection |
| T6 | Similar-ticket retrieval |
| T7 | Resolution-time / survival analysis |
| T8 | Evidence fusion / decision engine |
| T9 | Task-specific confidence and calibration |
| T10 | Automation and human review boundary |
| T11 | Feedback / active-learning lifecycle specification |

The tasks are treated as separate evidence problems. Their outputs are not converted into a universal probability, confidence or risk score.

---

## Dataset Evidence

The project investigated multiple real-world software-support datasets, including:

- Eclipse
- Mozilla CORE
- IT Support
- GitBugs Cassandra
- GitBugs VS Code

The resulting dataset evidence was used to establish task suitability, modelling constraints and limitations.

Key dataset roles included:

- **Mozilla CORE** — primary multi-task source for several T2–T7 investigations and system-level evidence work.
- **IT Support** — independent seven-class population for T1 classification.
- **GitBugs Cassandra** — strong resolution-time evidence with additional task-specific evidence.
- **GitBugs VS Code** — additional evidence for classification, duplicate/retrieval and resolution-related investigations.
- **Eclipse** — retained as audit and dataset-methodology evidence rather than an active modelling population.

---

## Modelling and Evaluation

The project includes task-specific modelling and evaluation evidence such as:

- TF-IDF based classification
- linear classifiers
- duplicate detection
- retrieval and ranking
- BM25-based retrieval evidence
- hybrid retrieval
- calibration analysis
- Kaplan–Meier analysis
- Nelson–Aalen analysis
- accelerated failure-time modelling
- survival calibration
- task-specific uncertainty analysis

The repository contains the corresponding evaluation plots generated during the investigations.

These include confusion matrices, per-class evaluation, retrieval metrics, ranking behaviour, coverage analysis, calibration curves, reliability diagrams, survival curves, cumulative hazard, evidence availability, evidence counts, and decision-state analysis.

---

## System Architecture

The application consists of four main components.

### Interactive Frontend

Provides single-ticket and multi-ticket analysis, evidence views, pipeline traces, explanations, limitations, and the human decision boundary.

### FastAPI Backend

Provides the application API for ticket analysis, batch analysis, and persistence operations.

### Frozen T1–T11 Runtime

Executes the established modelling and evidence pipeline using the frozen deployment artefacts. The deployment layer does not retrain or modify the modelling pipeline.

### PostgreSQL

Stores tickets, ticket analyses, explanation data, and human review outcomes.

---

## Application

### Single Ticket

A ticket can be analysed using:

- Ticket ID
- Creation time
- Creator
- Creator detail
- Summary
- Description

### Multiple Tickets

Structured JSON or CSV input can be submitted for batch analysis. The interface processes the supplied tickets without requiring a predetermined batch size.

### Analysis Workspace

The analysis workspace presents:

- system findings
- T1–T11 evidence
- pipeline trace
- explanation
- limitations
- human decision boundary
- lifecycle state

### Human Review

The system exposes the operational boundary as:

`HUMAN_DECISION_REQUIRED`

Human review outcomes are stored separately from model findings and analysis evidence.

---

## Persistence

PostgreSQL stores three primary entities:

- tickets
- ticket analyses
- human reviews

The analysis record retains structured evidence and explanation information, while human decisions are stored separately against the corresponding analysis.

---

## Deployment

The complete application is containerised with Docker Compose.

The local deployment contains:

- Nginx frontend
- FastAPI backend
- PostgreSQL database
- frozen T1–T11 runtime

The frontend is available locally on port `8080` and the FastAPI service on port `8000`.

---

## Repository Structure

```text
.
├── deployment/
│   ├── backend/
│   ├── frontend/
│   ├── demo/
│   ├── scripts/
│   └── tests/
├── modeling/
│   ├── T1/
│   ├── T2/
│   ├── T3/
│   ├── T4/
│   ├── T5/
│   ├── T6/
│   ├── T7/
│   ├── T8/
│   ├── T9/
│   ├── T10/
│   └── T11/
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
