# CareLoop

> **From medical records to unfinished care.**

CareLoop is an **agentic healthcare coordination platform** that transforms
fragmented medical records into a continuously updated patient care state,
identifies care actions that appear incomplete, verifies them against evidence,
and turns verified gaps into actionable tasks for authorized healthcare staff.

The core idea is simple:

> **Healthcare records tell us what happened. CareLoop finds what still needs to
> happen.**

---

## Table of Contents

- [Overview](#overview)
- [Problem](#problem)
- [Solution](#solution)
- [Core Concept](#core-concept)
- [Key Features](#key-features)
- [How CareLoop Works](#how-careloop-works)
- [System Architecture](#system-architecture)
- [Microservices](#microservices)
- [Agentic AI Architecture](#agentic-ai-architecture)
- [Care State Graph](#care-state-graph)
- [Database Architecture](#database-architecture)
- [Event-Driven Architecture](#event-driven-architecture)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Data Flow](#data-flow)
- [Example Workflow](#example-workflow)
- [API Overview](#api-overview)
- [AI Model Strategy](#ai-model-strategy)
- [Healthcare Safety](#healthcare-safety)
- [Local Development](#local-development)
- [Docker Infrastructure](#docker-infrastructure)
- [Development Roadmap](#development-roadmap)
- [Demo Scenario](#demo-scenario)
- [Future Scope](#future-scope)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

---

# Overview

Healthcare information is often fragmented across:

- consultation notes
- discharge summaries
- prescriptions
- laboratory reports
- imaging reports
- referrals
- appointment records
- follow-up notes
- scanned documents
- external specialist reports

A patient's record may clearly indicate that something **should happen**, but
there may be no system-level mechanism ensuring that the action actually reaches
completion.

For example:

> "Refer patient to cardiology and follow up in two weeks."

The referral may be documented.

But did the patient actually see the cardiologist?

Did the appointment happen?

Was the specialist report received?

Did the original physician review it?

Did the next follow-up happen?

CareLoop is designed to identify these unfinished chains.

---

# Problem

## Healthcare does not only have a data problem.

It also has a **closure problem**.

A medical record can contain hundreds of events, but important actions can fall
through the cracks.

### Example

```text
Doctor consultation
        ↓
Cardiology referral
        ↓
Appointment?
        ↓
Specialist consultation?
        ↓
Specialist report?
        ↓
Original doctor review?
        ↓
Next care decision?
```

A conventional document management system can store these records.

A search system can retrieve them.

A summarizer can summarize them.

But CareLoop asks a different question:

> **What important care actions appear unfinished?**

---

# Solution

CareLoop creates an intelligent layer over healthcare records.

```text
Medical Records
      ↓
Document Intelligence
      ↓
Clinical Events
      ↓
Patient Timeline
      ↓
Care Intentions
      ↓
Care State
      ↓
Care Gap Detection
      ↓
Evidence Verification
      ↓
Action Recommendation
      ↓
Human Review
      ↓
Task Execution
      ↓
Care Closure
```

The system does not attempt to replace clinicians.

Instead, it acts as an **operational intelligence and coordination layer**.

---

# Core Concept

The fundamental CareLoop data model is:

```text
Document
    ↓
Clinical Event
    ↓
Care Intent
    ↓
Expected Outcome
    ↓
Observed Outcome
    ↓
Care Gap
    ↓
Evidence
    ↓
Task
    ↓
Resolution
```

### Example

A discharge summary contains:

> "Repeat HbA1c in 3 months."

CareLoop converts this into:

```text
CARE INTENT

Action:
Repeat HbA1c

Expected:
Within 3 months

Status:
Pending
```

Three months later, the system searches the patient's available records.

If no corresponding HbA1c result is found:

```text
CARE GAP

Missing HbA1c result

Confidence:
91%

Status:
Needs verification
```

The Evidence Agent searches supporting records.

If the gap is confirmed:

```text
TASK

Verify whether HbA1c was completed externally.

Assigned to:
Care Coordinator

Priority:
Medium
```

Once resolved:

```text
✓ CARE LOOP CLOSED
```

---

# Key Features

## 1. Medical Document Ingestion

CareLoop accepts fragmented healthcare documents such as:

- PDF files
- scanned reports
- prescriptions
- laboratory reports
- discharge summaries
- consultation notes
- referral letters
- imaging reports

Documents are stored in object storage while metadata is maintained in
PostgreSQL.

---

## 2. Document Intelligence

Documents are processed using:

```text
Document
   ↓
OCR / Text Extraction
   ↓
Document Classification
   ↓
Clinical Information Extraction
   ↓
Structured Events
```

The system extracts information such as:

- diagnoses
- medications
- tests
- results
- referrals
- follow-up instructions
- appointments
- procedures
- care recommendations

---

## 3. Patient Timeline

CareLoop reconstructs a chronological view of the patient's healthcare journey.

Example:

```text
Aug 01
Consultation

Aug 03
HbA1c ordered

Aug 04
Cardiology referral

Aug 05
Medication changed

Aug 18
Follow-up

Aug 31
⚠ Missing HbA1c result
⚠ Cardiology referral unresolved
```

---

## 4. Care Intent Extraction

The system identifies actions that healthcare providers intended to happen.

Examples:

```text
"Follow up in 2 weeks."

"Repeat CT in 3 months."

"Refer to cardiology."

"Review pathology results."

"Repeat blood test."

"Continue medication and reassess."
```

These become structured **Care Intent** objects.

---

## 5. Care Gap Detection

The Care Gap Agent compares:

```text
Expected Care
      VS
Observed Care
```

Possible gaps include:

- unresolved referrals
- missing laboratory results
- overdue follow-ups
- missing specialist reports
- missed appointments
- incomplete procedures
- unresolved investigations
- medication inconsistencies
- unreviewed results

---

## 6. Evidence Verification

AI-generated findings should not automatically become healthcare actions.

CareLoop therefore uses an Evidence Agent.

It asks:

> **Is there sufficient evidence that this care gap actually exists?**

The agent searches:

- documents
- document chunks
- clinical events
- patient timeline
- related care events

It identifies evidence supporting or contradicting the potential gap.

---

## 7. Explainable Care Gaps

Each detected gap contains evidence.

Example:

```text
CARE GAP
────────────────────────

Cardiology referral appears unresolved.

Created:
August 4

Expected:
August 18

Evidence:

✓ Referral document found
✓ Referral event extracted
✓ No cardiology consultation found
✓ No specialist report found

Confidence:
94%

[View Evidence]
[Review]
```

CareLoop does not merely say:

> "The AI thinks this is a gap."

It shows **why the system flagged it**.

---

## 8. Action Recommendations

Once a care gap is verified, the Action Agent recommends an operational next
step.

Examples:

### Missing laboratory result

```text
Verify whether the test was completed
outside the current healthcare system.
```

### Unresolved referral

```text
Verify referral status and appointment.
```

### Missing specialist report

```text
Request or verify receipt of the specialist report.
```

### Medication discrepancy

```text
Escalate discrepancy for clinician review.
```

The system does not independently change medications, diagnose patients, or make
treatment decisions.

---

## 9. Task Management

Verified care gaps become operational tasks.

```text
Care Gap
    ↓
Action Recommendation
    ↓
Human Approval
    ↓
Task
```

Tasks can contain:

- patient
- care gap
- assigned user
- priority
- due date
- description
- status
- completion notes

---

## 10. Closed-Loop Tracking

CareLoop tracks the entire lifecycle:

```text
Detected
   ↓
Verified
   ↓
Task Created
   ↓
Assigned
   ↓
In Progress
   ↓
Completed
   ↓
Verified Resolution
   ↓
✓ CLOSED
```

This is the central idea behind the name **CareLoop**.

---

# System Architecture

```text
                         ┌──────────────────────┐
                         │      Next.js UI      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     API Gateway      │
                         │        FastAPI       │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
     │ Document        │   │ Patient State   │   │ Task            │
     │ Service         │   │ Service         │   │ Service         │
     └────────┬────────┘   └────────┬────────┘   └─────────────────┘
              │                     │
              ▼                     │
     ┌─────────────────┐            │
     │ Document        │            │
     │ Intelligence    │            │
     └────────┬────────┘            │
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌─────────────────┐
                │    LangGraph    │
                │   Orchestrator  │
                └────────┬────────┘
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
        ┌────────┐  ┌──────────┐  ┌──────────┐
        │ Care   │  │ Evidence │  │ Action   │
        │ Gap    │  │ Agent    │  │ Agent    │
        │ Agent  │  │          │  │          │
        └────┬───┘  └────┬─────┘  └────┬─────┘
             │           │             │
             └───────────┼─────────────┘
                         ▼
                  ┌──────────────┐
                  │ Human Review │
                  └───────┬──────┘
                          │
                          ▼
                     Task Service


       ┌─────────────────────────────────────────────┐
       │                 DATA LAYER                   │
       │                                             │
       │ PostgreSQL + pgvector                       │
       │ Redis                                       │
       │ MinIO                                       │
       └─────────────────────────────────────────────┘
```

---

# Microservices

CareLoop uses a microservice architecture so individual capabilities can evolve
independently.

---

## 1. API Gateway

### Responsibility

The API Gateway is the external entry point for the application.

It handles:

- frontend requests
- authentication
- authorization
- routing
- request validation
- aggregation of service responses

### Example endpoints

```text
/api/documents
/api/patients
/api/timeline
/api/care-gaps
/api/tasks
```

### Technology

- FastAPI
- Python

---

## 2. Document Service

### Responsibility

Manages healthcare documents.

It handles:

- uploads
- document metadata
- storage references
- retrieval
- deletion
- processing state

### Example

```text
POST /documents
```

receives:

```text
discharge_summary.pdf
```

and stores:

```text
MinIO:
patients/P001/documents/D001.pdf

PostgreSQL:
document metadata
```

### Technology

- FastAPI
- PostgreSQL
- MinIO
- Python

---

## 3. Document Intelligence Service

### Responsibility

Converts unstructured documents into structured healthcare events.

Pipeline:

```text
PDF/Image
   ↓
OCR
   ↓
Text
   ↓
Classification
   ↓
LLM Extraction
   ↓
Clinical Events
```

### Output

```json
{
  "event_type": "referral",
  "specialty": "cardiology",
  "date": "2026-08-04",
  "confidence": 0.96
}
```

### Technology

- Python
- OCR
- LLM
- Pydantic
- PostgreSQL

---

## 4. Patient State Service

### Responsibility

Maintains the longitudinal patient state.

It combines:

- clinical events
- encounters
- conditions
- medications
- referrals
- investigations
- follow-ups

into a coherent patient timeline.

### Example

```text
Patient P001

        │
        ├── Consultation
        │
        ├── Referral
        │
        ├── Investigation
        │
        ├── Medication
        │
        └── Follow-up
```

### Technology

- FastAPI
- PostgreSQL
- SQLAlchemy

---

## 5. Care Gap Agent

### Responsibility

Identifies potentially unfinished care.

It compares:

```text
Care Intentions
        +
Observed Clinical Events
        ↓
Potential Care Gaps
```

Example:

```text
Intent:
Cardiology consultation

Observed:
No cardiology consultation found

        ↓

Potential Gap
```

This is one of the primary reasoning agents in CareLoop.

---

## 6. Evidence Agent

### Responsibility

Validates potential care gaps.

It retrieves relevant evidence from:

- documents
- chunks
- embeddings
- clinical events
- timeline

and determines whether the evidence:

```text
Supports the gap
       OR
Contradicts the gap
       OR
Is insufficient
```

This reduces false positives.

---

## 7. Action Agent

### Responsibility

Determines an appropriate **operational next step** for a verified gap.

Example:

```text
Gap:
Missing specialist report

↓

Action:
Verify whether the report was received
and request it if necessary.
```

The Action Agent does not autonomously perform high-risk clinical decisions.

---

## 8. Task Service

### Responsibility

Converts approved actions into trackable work.

Handles:

- task creation
- assignment
- priorities
- due dates
- status
- completion
- task history

Example:

```text
Task:
Verify cardiology referral

Assigned:
Care Coordinator

Priority:
HIGH

Status:
OPEN
```

---

# Agentic AI Architecture

CareLoop uses **LangGraph** to orchestrate specialized reasoning agents.

```text
                     START
                       │
                       ▼
                Load Patient State
                       │
                       ▼
                Care Gap Agent
                       │
                 Potential Gap?
                  /           \
                NO             YES
                │               │
               END              ▼
                         Evidence Agent
                               │
                          Verified?
                          /       \
                        NO         YES
                        │           │
                 Human Review      ▼
                              Action Agent
                                   │
                                   ▼
                              Human Approval
                                   │
                                   ▼
                              Task Service
                                   │
                                   ▼
                                  END
```

---

# Why LangGraph?

LangGraph provides:

- stateful workflows
- conditional execution
- agent orchestration
- retries
- human-in-the-loop workflows
- persistent state
- controlled agent execution

CareLoop does **not** make every component an agent.

Normal deterministic software handles:

- file uploads
- database operations
- authentication
- task persistence
- API routing

AI agents are used where reasoning is actually required.

---

# Care State Graph

A central concept in CareLoop is the **Care State Graph**.

Instead of viewing medical records as isolated documents, CareLoop connects
related events.

```text
Patient
   │
   ▼
Consultation
   │
   ▼
Referral
   │
   ▼
Appointment
   │
   ▼
Specialist Consultation
   │
   ▼
Specialist Report
   │
   ▼
Doctor Review
   │
   ▼
Next Care Action
```

If a required connection is missing:

```text
Referral
   │
   ▼
Appointment
   │
   ✗
Missing specialist consultation
```

CareLoop can surface this as a potential care gap.

---

# Database Architecture

CareLoop uses PostgreSQL with pgvector.

## Core tables

```text
patients
documents
document_chunks
document_embeddings
clinical_events
care_intents
care_gaps
gap_evidence
care_relationships
tasks
task_events
providers
organizations
encounters
medications
ai_runs
audit_logs
```

---

## Core data relationship

```text
PATIENT
   │
   ├── DOCUMENTS
   │       │
   │       └── DOCUMENT CHUNKS
   │               │
   │               └── EMBEDDINGS
   │
   ├── CLINICAL EVENTS
   │       │
   │       └── CARE INTENTS
   │               │
   │               └── CARE GAPS
   │                       │
   │                       └── GAP EVIDENCE
   │
   └── TASKS
           │
           └── TASK EVENTS
```

---

# Event-Driven Architecture

Redis is used for lightweight event communication and caching.

A document lifecycle can generate:

```text
DOCUMENT_UPLOADED
        ↓
DOCUMENT_PROCESSING_STARTED
        ↓
DOCUMENT_PROCESSED
        ↓
CLINICAL_EVENTS_EXTRACTED
        ↓
PATIENT_STATE_UPDATED
        ↓
CARE_GAP_ANALYSIS_STARTED
        ↓
CARE_GAP_DETECTED
        ↓
EVIDENCE_VERIFIED
        ↓
TASK_CREATED
        ↓
TASK_COMPLETED
        ↓
CARE_LOOP_CLOSED
```

This allows services to remain loosely coupled.

---

# Project Structure

```text
careloop/
│
├── infrastructure/
│   ├── postgres/
│   │   ├── init.sql
│   │   └── migrations/
│   │
│   ├── redis/
│   │
│   └── minio/
│
├── services/
│   │
│   ├── api-gateway/
│   │   ├── app/
│   │   │   ├── routes/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   ├── document-service/
│   │   ├── app/
│   │   │   ├── routes/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   ├── document-intelligence/
│   │   ├── app/
│   │   │   ├── extraction/
│   │   │   ├── classification/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   ├── patient-state/
│   │   ├── app/
│   │   │   ├── routes/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   ├── care-gap-agent/
│   │   ├── app/
│   │   │   ├── agents/
│   │   │   ├── prompts/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   ├── evidence-agent/
│   │   ├── app/
│   │   │   ├── agents/
│   │   │   ├── retrieval/
│   │   │   ├── prompts/
│   │   │   └── main.py
│   │   └── Dockerfile
│   │
│   └── task-service/
│       ├── app/
│       │   ├── routes/
│       │   ├── schemas/
│       │   ├── services/
│       │   ├── repositories/
│       │   └── main.py
│       └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   └── ...
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

# Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Recharts / graph visualization library

---

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

---

## AI

- LangGraph
- LangChain where useful
- LLM APIs
- Embedding model
- OCR
- Structured output / JSON schemas

---

## Database

### PostgreSQL

Primary relational database.

Stores:

- patients
- clinical events
- care intents
- care gaps
- evidence
- tasks

### pgvector

Stores document embeddings for semantic retrieval.

---

## Infrastructure

### Redis

Used for:

- event communication
- caching
- asynchronous processing where needed

### MinIO

S3-compatible object storage for:

- PDFs
- scanned documents
- images
- medical reports

---

## Containerization

- Docker
- Docker Compose

Kubernetes is intentionally excluded from the MVP to keep development focused on
product functionality.

---

# Data Flow

The complete CareLoop pipeline is:

```text
                  USER
                   │
                   ▼
            Upload Document
                   │
                   ▼
           Document Service
                   │
                   ├──────────────► MinIO
                   │
                   ▼
       Document Intelligence
                   │
                   ▼
           Clinical Events
                   │
                   ▼
          Patient State Service
                   │
                   ▼
            Patient Timeline
                   │
                   ▼
            Care Intent Agent
                   │
                   ▼
             Care Gap Agent
                   │
                   ▼
            Evidence Agent
                   │
             ┌─────┴─────┐
             │           │
         Confirmed    Contradicted
             │           │
             ▼           ▼
       Action Agent    Dismiss
             │
             ▼
       Human Approval
             │
             ▼
        Task Service
             │
             ▼
       Task Completed
             │
             ▼
       Care Gap Resolved
             │
             ▼
        ✓ CARE CLOSED
```

---

# Example Workflow

Consider a synthetic patient.

## Input documents

```text
discharge_summary.pdf
referral_letter.pdf
lab_report.pdf
followup_note.pdf
```

---

## Step 1 — Document ingestion

CareLoop stores the documents.

```text
4 documents received
```

---

## Step 2 — Extraction

The Document Intelligence Service identifies:

```text
Cardiology referral
HbA1c ordered
Follow-up required
Medication change
```

---

## Step 3 — Care intentions

CareLoop creates:

```text
CI001
Consult cardiology
Expected: Aug 18

CI002
Complete HbA1c
Expected: Aug 30
```

---

## Step 4 — Gap detection

The Care Gap Agent compares expected and observed events.

It discovers:

```text
Potential Gap 1
Cardiology referral unresolved

Potential Gap 2
HbA1c result missing
```

---

## Step 5 — Evidence verification

The Evidence Agent searches the patient's records.

For the cardiology referral:

```text
✓ Referral exists
✓ Follow-up indicates referral was expected
✗ No consultation found
✗ No specialist report found
```

Result:

```text
VERIFIED CARE GAP
Confidence: 94%
```

---

## Step 6 — Action generation

The Action Agent recommends:

```text
Verify referral status and determine
whether the patient completed the consultation.
```

---

## Step 7 — Human approval

A care coordinator reviews the finding.

```text
[Approve Task]
```

---

## Step 8 — Task creation

```text
TASK

Verify cardiology referral

Priority:
HIGH

Assigned:
Care Coordinator

Status:
OPEN
```

---

## Step 9 — Resolution

The coordinator verifies the appointment.

```text
Status:
COMPLETED
```

CareLoop updates:

```text
Care Gap:
RESOLVED

Care Loop:
✓ CLOSED
```

---

# API Overview

## Document Service

```http
POST /documents
GET /documents/{id}
GET /patients/{id}/documents
DELETE /documents/{id}
```

---

## Patient Service

```http
GET /patients/{id}
GET /patients/{id}/timeline
GET /patients/{id}/state
```

---

## Care Gap Service

```http
GET /patients/{id}/care-gaps
GET /care-gaps/{id}
POST /care-gaps/{id}/verify
POST /care-gaps/{id}/dismiss
```

---

## Task Service

```http
POST /tasks
GET /tasks
GET /tasks/{id}
PATCH /tasks/{id}
POST /tasks/{id}/complete
```

---

# AI Model Strategy

CareLoop is designed to minimize unnecessary LLM usage.

Not every operation requires an expensive model.

## Tier 1 — Small / low-cost models

Use for:

- document classification
- information extraction
- entity normalization
- simple summarization
- structured JSON generation

```text
100 documents
      ↓
Small model
      ↓
Structured events
```

---

## Tier 2 — Strong reasoning models

Use only when required:

- ambiguous care gaps
- cross-document reasoning
- contradiction analysis
- evidence verification
- complex action planning

```text
100 documents
      ↓
Cheap processing
      ↓
10 potential gaps
      ↓
Strong reasoning model
      ↓
3 verified gaps
```

This reduces:

- token usage
- latency
- API cost

while reserving expensive reasoning for the tasks that actually need it.

---

# Healthcare Safety

CareLoop is designed as a **care coordination and information intelligence
system**, not an autonomous medical decision-maker.

The system should:

### Do

- identify potentially incomplete workflows
- surface evidence
- summarize records
- identify inconsistencies
- recommend operational tasks
- prioritize administrative follow-up
- request human review

### Not do

- independently diagnose patients
- prescribe medications
- change medication doses
- determine treatment plans
- autonomously make high-risk clinical decisions

For potentially consequential findings, CareLoop routes the issue to an
authorized human.

---

# Human-in-the-Loop

The core safety model is:

```text
AI
 ↓
Detect
 ↓
Explain
 ↓
Recommend
 ↓
Human Review
 ↓
Approve
 ↓
Execute
```

Rather than:

```text
AI
 ↓
Make medical decision
 ↓
Execute automatically
```

---

# Local Development

## Prerequisites

Install:

- Docker Desktop
- Git
- Python 3.11+
- Node.js 20+
- npm / pnpm

---

## Clone repository

```bash
git clone <repository-url>
cd careloop
```

---

## Environment variables

Create:

```bash
cp .env.example .env
```

Example:

```env
POSTGRES_DB=careloop
POSTGRES_USER=careloop
POSTGRES_PASSWORD=careloop_dev_password

POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

MINIO_ROOT_USER=careloop
MINIO_ROOT_PASSWORD=careloop_minio_password

MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
```

AI provider credentials should also be configured through environment variables.

---

# Docker Infrastructure

The initial infrastructure contains:

```text
Docker Compose
│
├── PostgreSQL + pgvector
├── Redis
├── MinIO
└── Docker Network
```

Start infrastructure:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

---

## PostgreSQL

Default:

```text
Host:
localhost

Port:
5432

Database:
careloop
```

Inside Docker:

```text
postgres:5432
```

---

## Redis

Default:

```text
localhost:6379
```

Inside Docker:

```text
redis:6379
```

---

## MinIO

API:

```text
localhost:9000
```

Console:

```text
localhost:9001
```

Inside Docker:

```text
minio:9000
```

---

# Development Roadmap

## Phase 1 — Infrastructure

- Docker Compose
- PostgreSQL
- pgvector
- Redis
- MinIO

---

## Phase 2 — Document Pipeline

```text
Upload
 ↓
Storage
 ↓
OCR
 ↓
Extraction
 ↓
Clinical Events
```

---

## Phase 3 — Patient State

```text
Clinical Events
 ↓
Patient Timeline
 ↓
Care State
```

---

## Phase 4 — Agentic Intelligence

```text
Care Intent Agent
 ↓
Care Gap Agent
 ↓
Evidence Agent
 ↓
Action Agent
```

---

## Phase 5 — Task Management

```text
Care Gap
 ↓
Action
 ↓
Human Approval
 ↓
Task
 ↓
Resolution
```

---

## Phase 6 — Product UI

Build:

1. Dashboard
2. Patient overview
3. Timeline
4. Care State Graph
5. Care gaps
6. Evidence panel
7. Task queue
8. Closure tracking

---

# 5-Day MVP

The minimum successful demo should support:

```text
10–20 synthetic healthcare documents
             ↓
Document ingestion
             ↓
Clinical extraction
             ↓
Patient timeline
             ↓
Care intent detection
             ↓
Care gap detection
             ↓
Evidence verification
             ↓
Action recommendation
             ↓
Human approval
             ↓
Task creation
             ↓
Task completion
             ↓
✓ Care Loop Closed
```

Do not attempt to build the entire healthcare ecosystem in five days.

The critical vertical slice is:

> **Document → Timeline → Gap → Evidence → Action → Closure**

---

# Demo Scenario

The ideal demonstration begins with a messy patient record.

```text
12 Medical Documents
4 Encounters
3 Providers
Multiple care actions
```

CareLoop processes the records.

It identifies:

```text
42 clinical events
8 care intentions
6 completed actions
3 potential care gaps
```

Then:

```text
🔴 Unresolved cardiology referral
🟠 Missing HbA1c result
🟠 Medication discrepancy
```

Clicking the cardiology gap shows:

```text
WHY WAS THIS FLAGGED?

✓ Referral found
✓ Follow-up instruction found
✗ Consultation not found
✗ Specialist report not found

Confidence: 94%
```

The Evidence Agent verifies the gap.

The Action Agent recommends:

```text
Verify referral status.
```

The care coordinator approves.

A task is created.

After completion:

```text
Cardiology referral
       ↓
Verified
       ↓
Task completed
       ↓
✓ CARE LOOP CLOSED
```

---

# Future Scope

CareLoop can eventually evolve beyond document-based workflows.

## Healthcare interoperability

Support:

- FHIR
- ABDM
- EHR integrations
- hospital information systems
- laboratory systems
- pharmacy systems

---

## Multilingual healthcare

Support patient and staff workflows in languages commonly used in India.

Potential capabilities include:

- multilingual document processing
- regional-language summaries
- patient communication
- voice-based workflows

---

## External care detection

Patients frequently receive care outside a single hospital.

Future versions could identify:

```text
Internal records
        +
External documents
        +
Patient-provided records
        ↓
Unified Care State
```

---

## Automated coordination

Future versions could support:

- appointment coordination
- referral status requests
- patient reminders
- document requests
- escalation workflows

with appropriate authorization and human oversight.

---

## Population-level care management

CareLoop can eventually move from:

```text
One Patient
```

to:

```text
Hospital
 ↓
Thousands of Patients
 ↓
Care Gap Prioritization
```

Example:

```text
1,240 patients

🔴 43 critical gaps
🟠 127 high-priority gaps
🟡 291 pending gaps
🟢 779 on track
```

---

# What Makes CareLoop Different?

CareLoop is not intended to be another:

- medical chatbot
- PDF summarizer
- EHR
- generic task manager
- referral tracker

Its core purpose is:

> **Discovering unfinished care from fragmented evidence.**

The distinction is:

```text
Traditional System

"What documents do we have?"
            ↓
"What happened?"
```

CareLoop asks:

```text
"What was supposed to happen?"
            ↓
"Did it happen?"
            ↓
"What evidence supports that?"
            ↓
"If it didn't happen, what needs to happen now?"
            ↓
"Has the loop been closed?"
```

---

# Project Philosophy

CareLoop follows five principles:

### 1. Evidence before action

AI-generated findings should be grounded in source information.

### 2. Human before high-risk action

Consequential healthcare decisions remain under human control.

### 3. Small models where possible

Use inexpensive models for routine extraction and reserve powerful models for
complex reasoning.

### 4. Events over isolated documents

The system should understand the patient's longitudinal journey rather than
treating every document independently.

### 5. Closure over notification

The goal isn't simply:

> "Something is missing."

The goal is:

> **"Something was missing → someone acted → it was resolved."**

---

# Final Architecture

```text
                              CARELOOP
                    AI FOR CLOSED-LOOP CARE
                                  │
                                  ▼
                    ┌────────────────────────┐
                    │   Healthcare Records   │
                    │ PDF • Scan • Reports   │
                    │ Referrals • Notes      │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │ Document Intelligence   │
                    │ OCR + Extraction + NLP │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │    Clinical Events     │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │    Patient Care State  │
                    │   Timeline + Graph     │
                    └───────────┬────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    LangGraph    │
                       │   Orchestrator  │
                       └────────┬────────┘
                                │
               ┌────────────────┼────────────────┐
               │                │                │
               ▼                ▼                ▼
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │ Care Gap   │   │ Evidence   │   │  Action    │
        │   Agent    │   │   Agent    │   │   Agent    │
        └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                       ┌───────────────┐
                       │ Human Review  │
                       └───────┬───────┘
                               │
                               ▼
                       ┌───────────────┐
                       │ Task Service  │
                       └───────┬───────┘
                               │
                               ▼
                         TASK COMPLETED
                               │
                               ▼
                       ┌───────────────┐
                       │  CARE CLOSED  │
                       └───────────────┘


        ┌─────────────────────────────────────────────┐
        │                  DATA LAYER                 │
        │                                             │
        │ PostgreSQL + pgvector                       │
        │ Redis                                       │
        │ MinIO                                       │
        └─────────────────────────────────────────────┘
```

---

# CareLoop in One Sentence

> **CareLoop is an agentic healthcare coordination platform that transforms
> fragmented medical records into a longitudinal care state, discovers
> unfinished care, verifies each gap with evidence, and helps healthcare teams
> close the loop through human-approved actions.**

---

**Status:** 🚧 Active Development **Project Type:** Agentic AI + Healthcare +
Microservices **Primary Architecture:** Event-driven microservices **AI
Orchestration:** LangGraph **Backend:** FastAPI / Python **Frontend:** Next.js /
TypeScript **Database:** PostgreSQL + pgvector **Cache / Events:** Redis
**Object Storage:** MinIO **Deployment:** Docker Compose for MVP
