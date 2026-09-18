# Aptino Claim Engine

An AI-assisted health-insurance claim assessment system that combines policy-document retrieval, specialized analysis agents, rule-based evaluation, and expense calculation to produce explainable claim-review results.

The system is designed as a conservative decision-support tool. When the available information is insufficient to support a reliable automatic determination, it returns `NEEDS_REVIEW` or `INSUFFICIENT_EVIDENCE`.

> This system is an assessment aid and does not replace a qualified claims examiner.


## Live Demo

- **Frontend (Streamlit):** https://aptino-claim-engine-7qrsyaknhcixwfs5otwryq.streamlit.app/
- **Backend API (Render):** https://aptino-claim-engine-38n8.onrender.com


## 1. Project Overview

The Aptino Claim Engine evaluates health-insurance claims using:

- A health-insurance policy PDF
- Structured claim information
- Policy ingestion and meaningful chunking
- Sparse BM25 retrieval
- Dense semantic retrieval
- Hybrid retrieval using Reciprocal Rank Fusion
- Cross-encoder reranking
- Specialized claim-analysis agents
- Rule-based claim checks
- Expense calculation
- Evidence and policy citations
- Structured execution traces
- Streamlit frontend
- FastAPI backend

The architecture separates evidence retrieval, specialized analysis, deterministic rule checks, and final decision aggregation.

The system intentionally favors manual review when the available evidence does not support a reliable automatic conclusion.

---

## 2. Main Features

### Policy and Retrieval

- PDF policy ingestion
- Policy text extraction
- Meaningful policy chunking
- Page and section metadata
- Chunk identifiers for citation
- BM25 lexical retrieval
- Dense semantic retrieval
- Hybrid retrieval using Reciprocal Rank Fusion
- Cross-encoder reranking
- Retrieval metadata including ranks and scores

### Multi-Agent Analysis

Three specialized agents are implemented:

- `CoverageAgent`
- `HospitalizationAgent`
- `DocumentationAgent`

Each agent has a separate responsibility and returns structured `AgentDecision` output.

### Decision and Evaluation

- Structured Pydantic models
- Conservative decision aggregation
- Abstention / manual-review behavior
- Initial waiting-period checks
- Pre-existing condition waiting-period checks
- Previous continuous coverage handling
- Experimental-treatment checks
- Inpatient treatment checks
- Day-care treatment checks
- Domiciliary treatment checks
- Hospital-registration checks
- Medical-necessity verification flags
- Expense breakdown
- Domiciliary sublimit calculation

### Explainability

The system exposes:

- Agent-specific reasoning
- Retrieved policy evidence
- Policy chunk identifiers
- Page and section metadata
- Retrieval method
- BM25 rank
- Dense rank
- Hybrid score
- Reranking score
- Key findings
- Applicable limits
- Missing evidence
- Execution trace
- Abstention / review explanation

---

## 3. Technology Stack

- Python 3.12
- FastAPI
- Streamlit
- PyMuPDF
- Pydantic
- Rank-BM25
- Sentence Transformers
- Scikit-learn
- NumPy
- Pytest

Retrieval models:

```text
Dense embedding model:
all-MiniLM-L6-v2

Reranker:
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The project uses a lightweight custom Python orchestration approach rather than introducing an additional agent framework.

This keeps the implementation small and makes the agent boundaries, state flow, and decision aggregation explicit.

---

## 4. Project Structure

```text
aptino-claim-engine/
│
├── app.py
├── README.md
├── requirements.txt
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
├── artifacts/
│   ├── policy_text.txt
│   ├── policy_chunks.jsonl
│   └── evaluation_results.json
│
├── scripts/
│   ├── evaluate.py
│   ├── ingest_policy.py
│   └── inspect_cases.py
│
├── src/
│   └── claim_engine/
│       │
│       ├── agents/
│       │   ├── models.py
│       │   ├── coverage_agent.py
│       │   ├── hospitalization_agent.py
│       │   ├── documentation_agent.py
│       │   └── decision_engine.py
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
│           ├── dense_retriever.py
│           ├── hybrid_retriever.py
│           └── reranker.py
│
└── tests/
    └── test_public_case_rules.py
```

---

## 5. Setup

### Create the virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 6. Policy Ingestion

The policy PDF is converted into searchable text and structured policy chunks.

Run:

```powershell
python scripts\ingest_policy.py
```

Generated artifacts:

```text
artifacts/policy_text.txt
artifacts/policy_chunks.jsonl
```

Each policy chunk contains metadata such as:

- Chunk identifier
- Page number
- Section
- Policy text

Chunk identifiers are used to connect retrieved evidence to policy citations shown to the reviewer.

---

## 7. Running the Application

The system has two application components:

- FastAPI backend
- Streamlit frontend

### Start FastAPI

From the project root:

```powershell
uvicorn src.claim_engine.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Health endpoint:

```text
GET /health
```

Example:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "aptino-claim-engine"
}
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Start Streamlit

In a second terminal:

```powershell
streamlit run app.py --server.fileWatcherType none
```

Open:

```text
http://localhost:8501
```

The frontend displays:

- Final assessment decision
- Confidence
- Reasoning
- Key findings
- Applicable limits
- Missing evidence
- Policy citations
- Individual agent decisions
- Execution trace
- Rule-based evaluation
- Expense breakdown
- Full assessment results

---

## 8. API

### `GET /health`

Used as a lightweight service health check.

Example response:

```json
{
  "status": "healthy",
  "service": "aptino-claim-engine"
}
```

### `POST /analyze`

Accepts a structured claim and returns a machine-readable assessment.

Example request:

```json
{
  "claim_id": "TEST-001",
  "patient_age": 45,
  "diagnosis": "appendicitis",
  "treatment": "inpatient hospitalization",
  "hospital_name": "Test Hospital",
  "admission_date": "2025-06-10",
  "discharge_date": "2025-06-12",
  "claimed_amount": 50000,
  "policy_start_date": "2024-01-01",
  "notes": "Routine inpatient treatment"
}
```

Example response structure:

```json
{
  "claim_id": "TEST-001",
  "decision": "NEEDS_REVIEW",
  "confidence": 0.583,
  "reasoning": "...",
  "key_findings": [],
  "applicable_limits": [],
  "missing_evidence": [],
  "agent_decisions": [],
  "citations": [],
  "policy_citations": [],
  "execution_trace": [],
  "abstention_reason": "..."
}
```

The exact response contains the evidence and structured outputs produced by the specialized agents.

---

## 9. Architecture

The system follows this high-level flow:

```text
                     ┌──────────────────────┐
                     │      Claim Input     │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   Pydantic Validation│
                     └──────────┬───────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │      Specialized Agents       │
                └───────────────┬───────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
       CoverageAgent     HospitalizationAgent  DocumentationAgent
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Structured Agent     │
                     │ Decisions + Evidence │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │   Decision Engine    │
                     │ Conservative         │
                     │ Aggregation          │
                     └──────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
             Final Decision          Review / Abstention
                    │
                    ▼
             Streamlit / API
```

### Agent Boundaries

#### CoverageAgent

Responsible for policy retrieval related to:

- Diagnosis
- Treatment
- Coverage eligibility
- Exclusions
- Waiting periods

It retrieves and reranks policy evidence and identifies areas requiring verification.

#### HospitalizationAgent

Responsible for:

- Hospitalization-related policy evidence
- Inpatient treatment
- Admission duration
- The 24-hour hospitalization threshold
- Admission/discharge documentation

It does not independently approve a claim.

#### DocumentationAgent

Responsible for checking whether important claim information is present, including:

- Claimed amount
- Admission date
- Discharge date
- Hospital name
- Supporting documents
- Bills and receipts
- Medical records
- Treatment notes

If required claim information is absent, it can return `INSUFFICIENT_EVIDENCE`.

---

## 10. Structured State

The system uses Pydantic models to exchange structured state between components.

Core models include:

```text
ClaimInput
Evidence
AgentDecision
FinalDecision
```

`AgentDecision` contains:

- Agent name
- Decision
- Reasoning
- Evidence
- Confidence
- Key findings
- Applicable limits
- Missing evidence
- Policy citations

`FinalDecision` aggregates these results and additionally contains:

- Claim ID
- Final decision
- Confidence
- Aggregated findings
- Aggregated limits
- Missing evidence
- Agent decisions
- Citations
- Policy citations
- Execution trace
- Abstention reason

This prevents the final decision from depending on unstructured text alone.

---

## 11. Retrieval Pipeline

The retrieval system uses multiple stages.

### 11.1 BM25 Sparse Retrieval

BM25 performs lexical matching between the claim query and policy chunks.

This is useful when important claim or policy terminology appears directly in the policy.

### 11.2 Dense Retrieval

Dense retrieval uses:

```text
all-MiniLM-L6-v2
```

It retrieves semantically related policy passages even when the wording differs from the claim.

### 11.3 Hybrid Retrieval

BM25 and dense retrieval are combined using Reciprocal Rank Fusion (RRF).

The implementation uses:

```text
RRF contribution = 1 / (60 + rank)
```

For a chunk appearing in both result sets:

```text
hybrid score =
    1 / (60 + BM25 rank)
    +
    1 / (60 + dense rank)
```

This combines lexical and semantic retrieval signals without requiring either retrieval method to be sufficient on its own.

### 11.4 Reranking

The fused candidate set is reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker evaluates the relevance of retrieved policy passages to the claim query.

Evidence records retain metadata such as:

- `chunk_id`
- `page`
- `section`
- `retrieval_method`
- `bm25_rank`
- `dense_rank`
- `hybrid_score`
- `rerank_score`

---

## 12. Retrieval Design Trade-offs

### BM25

Advantages:

- Fast
- Interpretable
- Good for exact policy terminology
- No embedding computation required

Limitation:

- Can miss semantically related passages when wording differs.

### Dense Retrieval

Advantages:

- Captures semantic similarity
- More robust to wording differences

Limitations:

- Depends on embedding-model quality
- Less directly interpretable than lexical matching
- Adds model inference cost

### Hybrid Retrieval

Combining both approaches improves robustness across exact terminology and semantic variations.

The trade-off is additional complexity and computation compared with a single retriever.

### Reranking

Cross-encoder reranking provides another relevance stage after candidate retrieval.

The trade-off is higher inference cost, so reranking is applied only to a bounded candidate set rather than the entire policy.

---

## 13. Decision Logic

The current decision model supports:

```text
APPROVE
REJECT
NEEDS_REVIEW
INSUFFICIENT_EVIDENCE
```

The decision engine uses conservative aggregation:

1. If any specialized agent returns `INSUFFICIENT_EVIDENCE`, the final decision becomes `INSUFFICIENT_EVIDENCE`.

2. Otherwise, if any specialized agent returns `NEEDS_REVIEW`, the final decision becomes `NEEDS_REVIEW`.

3. The current engine does not automatically approve a claim solely because retrieved evidence appears relevant.

4. The final result includes a review or abstention explanation when automatic determination is not supported.

This prioritizes evidence sufficiency and human review over unsupported automation.

---

## 14. Rule-Based Evaluation

A separate deterministic evaluator is used for supplied public and additional test cases.

The evaluator checks:

- Initial waiting period
- Pre-existing disease waiting period
- Previous continuous coverage
- Experimental treatment
- Inpatient hospitalization
- Day-care treatment
- Domiciliary treatment
- Hospital registration
- Medical necessity

Configured rule values include:

```text
Initial waiting period: 30 days
Pre-existing disease waiting period: 48 months
Domiciliary sublimit: 20%
```

### Treatment Types

The evaluator supports:

```text
inpatient
day_care
domiciliary
```

### Inpatient

The evaluator checks whether the admission reaches the configured 24-hour threshold.

Cases below the threshold are sent for review because some procedures may qualify under day-care exceptions.

### Day-care

The evaluator flags the need to verify that the procedure is a listed eligible day-care procedure rather than ordinary outpatient treatment.

### Domiciliary

The evaluator checks conditions including:

- Hospital room unavailability
- Whether the patient can be moved to a hospital
- Medical necessity
- Applicable policy limits
- Supporting evidence

---

## 15. Expense Calculation

The expense calculator summarizes:

- Room
- Doctor fees
- Medicines and diagnostics
- Pre-hospitalization
- Post-hospitalization
- Ambulance

The total claimed amount is calculated as the sum of these expense categories.

For domiciliary treatment, the configured sublimit is:

```text
Domiciliary sublimit =
    Sum insured × 20 / 100
```

Example:

```text
Sum insured: ₹5,00,000
Domiciliary sublimit: 20%

₹5,00,000 × 20%
= ₹1,00,000
```

The sublimit is **not** treated as the final payable amount.

The current implementation leaves:

```text
provisional_payable_inr: null
deductions_inr: null
```

until policy admissibility, supporting documents, medical evidence, and applicable limits can be verified.

---

## 16. Explainability and Citations

Each assessment exposes policy evidence through structured `Evidence` objects.

An evidence record includes:

```text
chunk_id
page
section
text
score
```

The final decision also exposes policy chunk identifiers through:

```text
citations
policy_citations
```

This allows a reviewer to locate the policy passages used by the agents.

The system also preserves retrieval metadata, including:

- BM25 rank
- Dense rank
- Hybrid score
- Reranking score

This makes retrieval behavior inspectable rather than presenting an unsupported conclusion without evidence.

---

## 17. Execution Trace

The frontend exposes a high-level execution trace rather than hidden model reasoning.

A verified example includes:

```text
1. Received and validated claim input.
2. Started CoverageAgent analysis.
3. CoverageAgent completed policy retrieval and coverage analysis.
   Retrieved 3 policy chunks.
4. Started HospitalizationAgent analysis.
5. HospitalizationAgent completed hospitalization analysis.
   Retrieved 5 policy chunks.
6. Started DocumentationAgent analysis.
7. DocumentationAgent completed documentation analysis.
   Retrieved 5 policy chunks.
8. Aggregated specialized-agent decisions.
9. Validation status: input validated successfully.
10. Elapsed analysis time: 0.571 seconds.
11. Final decision generated: NEEDS_REVIEW.
```

The trace provides:

- Validation status
- Agent names
- Major actions
- Retrieval result counts
- Aggregation step
- Elapsed analysis time
- Final decision

It intentionally does not expose hidden chain-of-thought.

---

## 18. Abstention and Manual Review

The system is designed to avoid unsupported automatic decisions.

`NEEDS_REVIEW` is used when:

- Policy evidence requires verification
- Medical necessity cannot be established
- Documentation still needs verification
- Treatment eligibility requires additional evidence
- Expense admissibility requires verification
- The decision engine cannot confidently establish automatic approval/rejection

`INSUFFICIENT_EVIDENCE` is used when required claim information or policy evidence is not sufficient for assessment.

The final response includes an `abstention_reason` when the system cannot support a reliable automatic determination.

---

## 19. Evaluation

The reproducible evaluation script is:

```powershell
python scripts\evaluate.py
```

The current verified run processed:

```text
Loaded 12 public cases.
Loaded 5 additional cases.
Total cases: 17
```

Results:

```text
Public cases:      12
Additional cases:   5
Total cases:       17

NEEDS_REVIEW:      11
REJECT:             6
```

The current evaluator does not automatically establish ground-truth accuracy metrics for every case, so these results should be interpreted as **case-processing and decision-output results**, not as an accuracy percentage.

Results are written to:

```text
artifacts/evaluation_results.json
```

### Evaluated scenarios

The test set includes cases covering:

- Inpatient treatment
- Initial waiting-period rejection
- Pre-existing-condition waiting period
- Domiciliary treatment
- Day-care treatment
- Experimental treatment
- Unknown treatment type
- Additional custom scenarios

The additional test set contains five custom cases:

```text
CUSTOM-001
CUSTOM-002
CUSTOM-003
CUSTOM-004
CUSTOM-005
```

---

## 20. Automated Tests

Run:

```powershell
pytest -q
```

Verified test result:

```text
8 passed in 0.06s
```

The tests cover deterministic evaluation and expense-calculation behavior, including:

- Initial waiting-period rejection
- Inpatient claim review
- Experimental-treatment rejection
- Domiciliary-treatment review
- Day-care review
- Expense total calculation
- Domiciliary sublimit calculation
- Non-domiciliary expense behavior

---

## 21. Reliability Scenarios

The implementation is designed around several reliability scenarios relevant to policy-based claim assessment.

### Waiting-period outcome

The deterministic evaluator checks the configured initial waiting period and can reject a claim falling inside that period.

### Pre-existing condition

The evaluator considers the configured 48-month waiting period and prior continuous coverage.

### Hospitalization threshold

The system checks the 24-hour inpatient threshold while allowing review for possible day-care exceptions.

### Category/sub-limit handling

Domiciliary treatment is evaluated separately and the configured 20% sublimit can be calculated from the supplied sum insured.

### Insufficient evidence

Missing claim fields or incomplete policy evidence can lead to `INSUFFICIENT_EVIDENCE` or `NEEDS_REVIEW`.

### Irrelevant or unsupported attributes

The system does not attempt to make a final claim determination from arbitrary attributes that are not supported by the configured rules and retrieved evidence.

---

## 22. Observed Failure Cases and Improvements

### Failure Case 1: Incomplete claim documentation

A claim may contain enough information to retrieve relevant policy evidence but still lack supporting documentation such as medical records, bills, or admission/discharge records.

**Observed behavior:**

The system keeps the claim in manual review rather than treating retrieved policy text as sufficient evidence.

**Root cause:**

Policy retrieval cannot substitute for missing claim documents.

**Improvement:**

Add document upload, OCR, document classification, and structured extraction from bills and medical records.

---

### Failure Case 2: Policy evidence does not establish final admissibility

A retrieved policy passage may establish a general hospitalization requirement without establishing all conditions required for final payment.

**Observed behavior:**

The system returns `NEEDS_REVIEW` and reports missing verification requirements.

**Root cause:**

The current retrieval and agent layer is evidence-oriented but does not perform complete medical/admissibility verification.

**Improvement:**

Add more granular policy rules and condition-specific evidence checks, with stronger section-aware retrieval.

---

### Failure Case 3: Rule evaluation and AI assessment can surface different review signals

The system contains both:

1. AI-agent assessment
2. Deterministic public-case evaluation

These are separate evaluation paths and can produce different statuses for the same test case.

For example, a deterministic rule may identify a rejection condition while the broader agent workflow may retain `NEEDS_REVIEW` because it requires policy/document verification.

**Root cause:**

The two pipelines currently serve different purposes: deterministic test-case rules provide explicit case checks, while the agent engine is intentionally conservative and evidence-oriented.

**Improvement:**

Introduce a unified decision-policy layer that explicitly reconciles deterministic rule outcomes with evidence sufficiency before producing the final claim status.

---

## 23. Known Limitations

The current implementation has several deliberate limitations:

- It does not replace a qualified claims examiner.
- It does not independently verify medical records.
- It does not establish medical necessity.
- It does not automatically determine final admissibility in all cases.
- It does not currently calculate a final payable amount after all deductions.
- `provisional_payable_inr` and `deductions_inr` remain unavailable until further verification.
- Policy citations should be verified against the source policy.
- Retrieval quality depends on policy extraction and chunking.
- Dense retrieval and reranking require machine-learning model inference.
- The decision engine is intentionally conservative.
- Domiciliary eligibility requires separate policy and medical verification.
- The current evaluation script reports case outcomes but does not provide a complete ground-truth accuracy benchmark.
- Retrieval-quality metrics such as recall@k and citation-hit rate are not currently calculated automatically.

---

## 24. Design Trade-offs

### Conservative decisions over aggressive automation

The engine defaults to review when evidence is incomplete.

This reduces the risk of unsupported automatic claim decisions but increases the number of cases requiring manual review.

### Lightweight custom orchestration

The project uses explicit Python orchestration rather than adding a large agent framework.

Benefits:

- Simple control flow
- Easy debugging
- Explicit state transitions
- Fewer dependencies
- Clear agent boundaries

Trade-off:

- Less built-in orchestration functionality than a dedicated workflow framework.

### Multiple retrieval methods

Using BM25, dense retrieval, RRF, and reranking adds computational cost.

The benefit is greater retrieval robustness across exact terminology and semantic variations.

### Structured outputs

Pydantic models add schema discipline and make the API response machine-readable.

The trade-off is that every agent must conform to a predefined output structure.

---

## 25. Future Improvements

Possible future improvements include:

- Document upload and OCR
- Extraction from bills and medical records
- More precise section-aware policy retrieval
- Additional policy-specific deterministic rules
- Stronger date and amount validation
- Confidence calibration
- Ground-truth accuracy evaluation
- Precision, recall, and F1 metrics
- Abstention-rate evaluation
- Retrieval recall@k
- Citation-hit-rate evaluation
- Structured audit logging
- Persistent storage
- Automated API integration tests
- Containerized deployment
- Retrieval-quality monitoring
- Human-review feedback loops
- More detailed domiciliary-policy validation
- Unified reconciliation between deterministic rules and agent decisions

---

## 26. Reproducibility

From a fresh project environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ingest the policy:

```powershell
python scripts\ingest_policy.py
```

Run tests:

```powershell
pytest -q
```

Run the complete supplied-case evaluation:

```powershell
python scripts\evaluate.py
```

Start the backend:

```powershell
uvicorn src.claim_engine.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the frontend in a second terminal:

```powershell
streamlit run app.py --server.fileWatcherType none
```

Then open:

```text
http://localhost:8501
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## 27. Conclusion

The Aptino Claim Engine demonstrates a modular approach to AI-assisted health-insurance claim assessment.

It combines:

- Policy ingestion
- Meaningful policy chunking
- Sparse retrieval
- Dense retrieval
- Hybrid retrieval
- Cross-encoder reranking
- Specialized analysis agents
- Structured state
- Deterministic rule evaluation
- Expense calculation
- Evidence traceability
- Policy citations
- Execution tracing
- Conservative abstention behavior
- FastAPI
- Streamlit

The current implementation emphasizes explainability and evidence sufficiency rather than unsupported automation.

It is intended to help a claims reviewer organize relevant policy evidence, identify missing information, and understand why a claim has been routed for further review.