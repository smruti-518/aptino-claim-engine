# Aptino Claim Engine

An AI-assisted health-insurance claim assessment system that combines policy-document retrieval, specialized analysis agents, rule-based evaluation, and expense calculation to produce explainable claim-review results.

The system is designed as a modular claim-assessment pipeline with separate components for policy ingestion, retrieval, agent-based analysis, deterministic rule evaluation, expense calculation, API serving, and a Streamlit user interface.

## Live Demo

* **Frontend (Streamlit):** [https://aptino-claim-engine-7qrsyaknhcixwfs5otwryq.streamlit.app/]
* **Backend API (Render):** [https://aptino-claim-engine-38n8.onrender.com]

The Streamlit frontend sends claim requests to the deployed FastAPI backend.

> **Deployment note:** The deployed retrieval path uses lightweight BM25 retrieval so that the application can run within the memory constraints of the free Render deployment tier.

---

## Project Overview

The Aptino Claim Engine processes health-insurance claims against a provided insurance policy document.

The system performs the following high-level steps:

1. Ingest the insurance policy PDF.
2. Extract and chunk policy text.
3. Index policy chunks for retrieval.
4. Retrieve relevant policy evidence for a claim.
5. Run multiple specialized claim-analysis agents.
6. Combine agent outputs into a final assessment.
7. Perform deterministic rule-based evaluation.
8. Calculate applicable expenses and limits.
9. Return an explainable result with policy citations and execution trace.
10. Present the result through a Streamlit interface.

The system is designed to favor **traceability and human review** rather than making unsupported automatic claim approvals or rejections.

---

## Architecture

```text
                    ┌─────────────────────────┐
                    │      Policy PDF         │
                    │  Insurance Policy Docs  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Policy Ingestion      │
                    │  Text Extraction +      │
                    │  Chunking + Metadata    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     BM25 Retriever      │
                    │    Policy Evidence      │
                    │       Retrieval         │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
       │ Coverage Agent │ │Hospitalization │ │ Documentation  │
       │                │ │     Agent      │ │     Agent      │
       └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
                │                  │                  │
                └──────────────────┼──────────────────┘
                                   ▼
                    ┌─────────────────────────┐
                    │    Decision Engine      │
                    │ Agent Aggregation +     │
                    │ Confidence + Trace      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │ Rule-Based       │      │ Expense          │
          │ Evaluation       │      │ Calculator       │
          └────────┬─────────┘      └────────┬─────────┘
                   │                         │
                   └────────────┬────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │       FastAPI API       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Streamlit Frontend   │
                    └─────────────────────────┘
```

---

## Key Components

### 1. Policy Ingestion

The policy PDF is processed into structured policy chunks containing:

* Chunk ID
* Page number
* Section
* Policy text

The ingestion pipeline produces reusable artifacts consumed by the retrieval layer.

Relevant files:

```text
scripts/ingest_policy.py
src/claim_engine/ingestion/policy_ingestion.py
```

Generated artifacts:

```text
artifacts/policy_text.txt
artifacts/policy_chunks.jsonl
```

---

### 2. Policy Retrieval

The deployed system uses **BM25 lexical retrieval** to identify policy sections relevant to each claim.

BM25 is useful for this task because insurance policies contain domain-specific terminology such as:

* hospitalization
* waiting period
* pre-existing disease
* day-care procedures
* domiciliary treatment
* exclusions
* medical necessity
* claim documentation

The retriever returns policy chunks together with retrieval metadata and policy citations.

Relevant file:

```text
src/claim_engine/retrieval/bm25_retriever.py
```

The project also retains a lightweight hybrid-retrieval interface so that retrieval metadata remains compatible with the broader architecture.

The active deployment does **not** load large transformer-based embedding or cross-encoder models. This keeps startup time and memory usage suitable for the free Render environment.

---

## Specialized Agents

The system uses multiple specialized agents so that different aspects of a claim can be assessed independently.

### CoverageAgent

Focuses on:

* Policy coverage
* Treatment-related exclusions
* Relevant policy evidence
* Potential coverage concerns

It retrieves relevant policy evidence and produces an explainable assessment.

File:

```text
src/claim_engine/agents/coverage_agent.py
```

### HospitalizationAgent

Focuses on:

* Hospitalization requirements
* Inpatient treatment
* Hospitalization-related policy conditions
* Whether sufficient information exists to assess hospitalization eligibility

File:

```text
src/claim_engine/agents/hospitalization_agent.py
```

### DocumentationAgent

Focuses on whether the claim contains sufficient basic information for assessment.

It checks fields such as:

* Claimed amount
* Admission date
* Discharge date
* Hospital name

It also identifies the need for supporting documentation such as:

* Bills
* Receipts
* Medical records
* Other claim documents

File:

```text
src/claim_engine/agents/documentation_agent.py
```

---

## Decision Engine

The `ClaimDecisionEngine` orchestrates the specialized agents and combines their outputs.

The engine records:

* Individual agent decisions
* Agent confidence
* Key findings
* Applicable limits
* Missing evidence
* Policy citations
* Execution trace
* Final decision
* Abstention/review reason

File:

```text
src/claim_engine/agents/decision_engine.py
```

The engine is intentionally conservative. When required information is missing or the available evidence does not support a reliable automatic determination, the system returns a review-oriented outcome rather than inventing a conclusion.

---

## Decision Statuses

The current implementation uses the following decision values:

```text
APPROVE
REJECT
NEEDS_REVIEW
INSUFFICIENT_EVIDENCE
```

In the current evaluation workflow, many cases are routed to `NEEDS_REVIEW` because the system is designed to surface policy evidence and verification requirements rather than automatically approve claims without sufficient supporting information.

---

## Rule-Based Evaluation

In addition to the agent-based assessment, the project includes deterministic rule-based evaluation for known policy conditions.

The rule evaluator checks claim information against documented policy rules, including conditions such as:

* Initial waiting periods
* Pre-existing condition waiting periods
* Domiciliary treatment conditions
* Day-care treatment requirements
* Experimental treatment exclusions
* Hospitalization-related requirements

Relevant file:

```text
src/claim_engine/evaluation/public_case_rules.py
```

This provides a deterministic comparison layer alongside the retrieval-and-agent pipeline.

---

## Expense Calculation

The project also includes an expense calculator for claim-related financial calculations.

It can calculate or expose information such as:

* Claimed amount
* Applicable sublimits
* Potential deductions
* Provisional payable amount
* Policy-based expense limits

Relevant file:

```text
src/claim_engine/evaluation/expense_calculator.py
```

The expense calculation is kept separate from the policy-retrieval and agent-analysis layers so that financial calculations remain independently testable.

---

## Explainability

Explainability is a core part of the system.

### Policy Evidence

Retrieved policy chunks include:

* Chunk ID
* Page
* Section
* Text
* Retrieval score

### Policy Citations

The final result includes references to the policy chunks used during analysis.

Example:

```text
page_11_chunk_36
page_2_chunk_6
```

### Agent Decisions

Each specialized agent reports:

* Agent name
* Decision
* Reasoning
* Confidence
* Evidence

### Execution Trace

The decision engine records the major stages of execution, for example:

```text
Received and validated claim input.
Started CoverageAgent analysis.
CoverageAgent completed policy retrieval and coverage analysis.
Started HospitalizationAgent analysis.
HospitalizationAgent completed hospitalization analysis.
Started DocumentationAgent analysis.
DocumentationAgent completed documentation analysis.
Aggregated specialized-agent decisions.
Validation status: input validated successfully.
Elapsed analysis time: ...
Final decision generated: ...
```

This makes the system easier to inspect and debug.

---

## API

The backend is implemented using FastAPI.

Main endpoint:

```text
POST /analyze
```

The API accepts structured claim information and returns a structured final assessment.

Example claim input:

```json
{
  "claim_id": "CUSTOM-001",
  "patient_age": 45,
  "diagnosis": "Acute appendicitis",
  "treatment": "Laparoscopic appendectomy",
  "hospital_name": "Example Hospital",
  "admission_date": "2018-05-10",
  "discharge_date": "2018-05-12",
  "claimed_amount": 45000,
  "policy_start_date": "2017-01-01",
  "notes": "Inpatient hospitalization for surgery"
}
```

The API returns structured information including:

```text
claim_id
decision
reasoning
confidence
key_findings
applicable_limits
missing_evidence
agent_decisions
citations
policy_citations
execution_trace
abstention_reason
```

---

## Streamlit Frontend

The Streamlit application provides an interactive interface for submitting claims and viewing the assessment.

The frontend displays:

* Claim assessment
* Decision
* Confidence
* Reasoning
* Key findings
* Applicable limits
* Missing evidence
* Policy citations
* Individual agent results
* Execution trace
* Rule-based evaluation
* Expense calculation
* Full API response

File:

```text
app.py
```

The frontend communicates with the backend through the `API_URL` environment variable.

Example:

```text
API_URL=https://aptino-claim-engine-38n8.onrender.com/analyze
```

---

## Deployment

### Backend

The FastAPI backend is deployed on Render.

Deployment characteristics:

```text
Platform: Render
Service type: Web Service
Plan: Free
CPU: 0.1
Memory: 512 MB
```

The deployment uses Uvicorn:

```bash
uvicorn src.claim_engine.api.main:app --host 0.0.0.0 --port $PORT
```

Live backend:

[https://aptino-claim-engine-38n8.onrender.com](https://aptino-claim-engine-38n8.onrender.com)

### Frontend

The Streamlit frontend is deployed using Streamlit Community Cloud.

Live frontend:

[https://aptino-claim-engine-7qrsyaknhcixwfs5otwryq.streamlit.app/](https://aptino-claim-engine-7qrsyaknhcixwfs5otwryq.streamlit.app/)

The frontend is configured to call the Render backend using the `API_URL` secret.

---

## Low-Memory Deployment Design

The deployed version was optimized for the resource constraints of the free Render tier.

Large transformer-based retrieval and reranking models can require significant memory and startup time. Therefore, the production deployment uses BM25 retrieval rather than loading large embedding and cross-encoder models.

This provides:

* Lower memory usage
* Faster startup
* Smaller deployment footprint
* Fewer heavyweight dependencies
* Better compatibility with low-resource hosting

The retrieval interface remains modular so that a more advanced semantic retrieval layer can be introduced later without redesigning the entire claim-processing architecture.

---

## Project Structure

```text
aptino-claim-engine/
│
├── app.py
├── README.md
├── requirements.txt
├── pytest.ini
│
├── artifacts/
│   ├── policy_text.txt
│   ├── policy_chunks.jsonl
│   └── evaluation_results.json
│
├── data/
│   ├── policy/
│   │   └── USGIC-CSCIndividualHealthInsurance_2017-2018.pdf
│   │
│   ├── claims/
│   │   └── public_test_cases.json
│   │
│   └── additional_cases/
│       └── additional_test_cases.json
│
├── scripts/
│   ├── ingest_policy.py
│   └── evaluate.py
│
├── src/
│   └── claim_engine/
│       │
│       ├── agents/
│       │   ├── coverage_agent.py
│       │   ├── hospitalization_agent.py
│       │   ├── documentation_agent.py
│       │   ├── decision_engine.py
│       │   └── models.py
│       │
│       ├── api/
│       │   └── main.py
│       │
│       ├── evaluation/
│       │   ├── public_case_rules.py
│       │   └── expense_calculator.py
│       │
│       ├── ingestion/
│       │   └── policy_ingestion.py
│       │
│       └── retrieval/
│           ├── bm25_retriever.py
│           ├── hybrid_retriever.py
│           ├── dense_retriever.py
│           └── reranker.py
│
└── tests/
    ├── test_ingestion.py
    ├── test_retrieval.py
    ├── test_agents.py
    ├── test_decision_engine.py
    ├── test_api.py
    ├── test_expense_calculator.py
    ├── test_evaluation.py
    └── test_additional_cases.py
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/smruti-518/aptino-claim-engine.git
cd aptino-claim-engine
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Policy Ingestion

To process the supplied policy document:

```bash
python scripts/ingest_policy.py
```

This generates:

```text
artifacts/policy_text.txt
artifacts/policy_chunks.jsonl
```

These artifacts are then used by the retrieval layer.

---

## Running the Backend Locally

Start the FastAPI server:

```bash
uvicorn src.claim_engine.api.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

The analysis endpoint is:

```text
http://127.0.0.1:8000/analyze
```

---

## Running the Frontend Locally

In a second terminal:

```bash
streamlit run app.py
```

The Streamlit interface will open in the browser.

By default, the frontend expects:

```text
http://127.0.0.1:8000/analyze
```

To use a different backend:

Windows PowerShell:

```powershell
$env:API_URL="https://your-backend-url/analyze"
streamlit run app.py
```

Linux/macOS:

```bash
export API_URL="https://your-backend-url/analyze"
streamlit run app.py
```

---

## Running Tests

Run the automated test suite:

```bash
pytest -q
```

Current test suite result:

```text
8 passed
```

The tests cover areas including:

* Policy ingestion
* Retrieval
* Agent behavior
* Decision engine
* API behavior
* Expense calculation
* Rule-based evaluation
* Additional claim cases

---

## Evaluation

The evaluation script processes the supplied public test cases and additional custom cases.

Run:

```bash
python scripts/evaluate.py
```

The current evaluation set contains:

```text
12 public cases
5 additional custom cases
-------------------------
17 total cases
```

Current observed outcomes:

```text
NEEDS_REVIEW            11
REJECT                   6
APPROVE                  0
```

The evaluation results are saved to:

```text
artifacts/evaluation_results.json
```

The evaluation script reports system outcomes for the supplied cases. It does not constitute an accuracy percentage because the evaluator does not compare every generated decision against an expected ground-truth label.

---

## Example Evaluation Cases

The evaluation set includes scenarios involving:

* Inpatient hospitalization
* Initial waiting periods
* Pre-existing conditions
* Domiciliary treatment
* Day-care procedures
* Experimental treatment
* Missing or incomplete claim information
* Unknown treatment types

Examples of deterministic policy outcomes observed in the evaluation include:

```text
PUB-002  -> REJECT
Reason: Initial 30-day waiting period

PUB-003  -> REJECT
Reason: Pre-existing condition waiting-period requirement

PUB-012  -> REJECT
Reason: Experimental treatment

CUSTOM-002 -> REJECT
Reason: Waiting-period condition
```

Other cases are routed to `NEEDS_REVIEW` where additional policy verification or supporting documentation is required.

---

## Configuration

The Streamlit frontend supports configuration through the `API_URL` environment variable.

Example:

```text
API_URL=http://127.0.0.1:8000/analyze
```

For the deployed frontend, the value points to the Render backend.

Secrets and environment files are excluded from Git using `.gitignore`.

---

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### Policy Processing

* PyMuPDF

### Retrieval

* BM25
* rank-bm25
* Lightweight retrieval interface

### Evaluation

* Deterministic rule-based evaluation
* Expense calculation

### Frontend

* Streamlit

### Testing

* pytest

### Deployment

* Render
* Streamlit Community Cloud

---

## Design Principles

### 1. Modular Architecture

Policy ingestion, retrieval, agents, decision aggregation, evaluation, API serving, and frontend presentation are separated into independent components.

This makes individual components easier to test and replace.

### 2. Evidence-Based Decisions

Agent outputs are associated with retrieved policy evidence rather than relying only on free-form reasoning.

### 3. Explainability

The system exposes reasoning, confidence, policy citations, evidence, and execution traces.

### 4. Conservative Automation

When evidence is incomplete, the system favors `NEEDS_REVIEW` or `INSUFFICIENT_EVIDENCE` rather than producing unsupported automatic decisions.

### 5. Deterministic Financial Logic

Expense calculations and explicit policy rules are implemented separately from the retrieval and agent layers.

### 6. Deployment Awareness

The deployed architecture is optimized for low-memory infrastructure while keeping the system modular enough to support more advanced retrieval approaches in the future.

---

## Failure Handling and Abstention

The system is designed to avoid silently treating missing information as evidence.

Examples of conditions that can lead to review or insufficient-evidence outcomes include:

* Missing admission or discharge information
* Missing hospital information
* Missing claimed amount
* Insufficient hospitalization evidence
* Unclear treatment eligibility
* Policy exclusions requiring verification
* Supporting documentation not supplied

When an automatic determination cannot be reliably supported, the system exposes an abstention/review reason.

---

## Rule-Based vs Agent-Based Assessment

The project intentionally maintains two complementary assessment paths.

### Agent-Based Assessment

```text
Policy retrieval
       ↓
CoverageAgent
HospitalizationAgent
DocumentationAgent
       ↓
Decision Engine
```

This provides contextual evidence and explainable reasoning.

### Rule-Based Assessment

The rule evaluator uses explicit deterministic rules for known policy conditions.

This provides a predictable evaluation layer for cases such as waiting periods and explicit exclusions.

The two outputs can be inspected separately through the Streamlit interface.

---

## Future Improvements

Potential future improvements include:

* More comprehensive policy-rule extraction
* Better structured policy representations
* Semantic embedding retrieval
* Cross-encoder reranking
* More specialized claim agents
* Stronger evidence-to-decision validation
* More detailed expense-limit calculations
* Improved document verification
* Human-in-the-loop review workflows
* Additional evaluation datasets
* Automated monitoring and observability
* Production-grade persistence and audit logging

The current deployment intentionally prioritizes reliability and low-resource operation over heavyweight model inference.

---

## Repository

GitHub:

[https://github.com/smruti-518/aptino-claim-engine]
---

## Summary

The Aptino Claim Engine demonstrates an end-to-end AI-assisted insurance claim assessment workflow:

```text
Policy PDF
    ↓
Policy ingestion
    ↓
Policy chunking
    ↓
BM25 retrieval
    ↓
Specialized agents
    ↓
Decision aggregation
    ↓
Rule-based evaluation
    ↓
Expense calculation
    ↓
FastAPI
    ↓
Streamlit
```

The resulting system provides an explainable claim-review workflow with policy evidence, agent-level reasoning, deterministic rule checks, expense calculations, confidence information, and execution tracing.

The application is deployed as a live Streamlit frontend backed by a FastAPI service running on Render.
