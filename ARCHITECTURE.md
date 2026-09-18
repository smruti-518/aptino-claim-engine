# Architecture & Design Note

## 1. Overview

The Aptino Claim Decision Engine is a policy-aware claim analysis system designed to assess health-insurance claims against an authoritative policy document.

The system follows a retrieval-augmented, multi-agent architecture. Claim information is validated first, relevant policy evidence is retrieved, specialized agents analyze different dimensions of the claim, and a decision engine aggregates the agent outputs into a structured final assessment.

The policy document is treated as the authoritative source for policy-related reasoning. Claim data is synthetic test data supplied by the assignment or created as additional evaluation cases.

## 2. System Architecture

The system consists of the following major components:

1. Policy ingestion and chunking
2. Policy retrieval
3. Specialized analysis agents
4. Decision aggregation
5. FastAPI backend
6. Streamlit frontend
7. Evaluation and testing pipeline

### Policy ingestion

The policy PDF is processed into text and divided into meaningful policy chunks rather than treating the entire document as a single context.

Each chunk contains traceability metadata including:

- chunk ID
- page number
- section information
- policy text

The generated policy index is stored under `artifacts/`.

### Retrieval

The deployed system uses a lightweight BM25-based retrieval implementation to remain compatible with the low-memory Render deployment environment.

The repository also contains the dense retrieval and reranking components developed during the project. The deployed configuration intentionally avoids loading the large transformer-based models because the selected free deployment environment has a 512 MB memory constraint.

Retrieved policy chunks retain retrieval metadata and are passed to the analysis agents as evidence.

## 3. Multi-Agent Design

The system uses three specialized agents with different responsibilities.

### CoverageAgent

Retrieves policy evidence related to the diagnosis, treatment, coverage conditions, and exclusions.

### HospitalizationAgent

Examines hospitalization-related requirements, including inpatient treatment and hospitalization evidence.

### DocumentationAgent

Checks whether important claim information is available, including claim amount, admission/discharge information, and hospital details.

The agents do not simply repeat the same prompt. Each agent has a different retrieval strategy and analyzes a different claim dimension.

Each agent produces structured output containing:

- decision
- reasoning
- evidence
- confidence
- key findings
- applicable limits
- missing evidence
- policy citations

## 4. Decision Engine

`ClaimDecisionEngine` coordinates the specialized agents.

The workflow is:

1. Validate the claim input.
2. Run CoverageAgent.
3. Run HospitalizationAgent.
4. Run DocumentationAgent.
5. Aggregate the structured agent decisions.
6. Calculate an overall confidence value.
7. Collect evidence and policy citations.
8. Determine whether the claim requires further review or has insufficient evidence.
9. Produce an execution trace.

The system is deliberately conservative. When the available evidence does not support a reliable automatic determination, the engine returns `NEEDS_REVIEW` or `INSUFFICIENT_EVIDENCE` rather than inventing a conclusion.

## 5. Explainability and Traceability

Policy evidence is retained in the final response through chunk IDs, page numbers, section information, and retrieved policy text.

The decision response also contains an execution trace describing major processing steps, including:

- claim validation
- agent execution
- policy retrieval
- evidence aggregation
- validation
- elapsed analysis time
- final decision generation

This makes the system easier to inspect and reproduce.

## 6. API and Frontend

The backend is implemented using FastAPI.

The primary endpoint is:

`POST /analyze`

The service also exposes:

`GET /health`

The Streamlit frontend provides a usable interface for entering a claim and viewing:

- final decision
- confidence
- reasoning
- key findings
- applicable limits
- missing evidence
- policy citations
- individual agent decisions
- execution trace
- rule-based evaluation
- expense information

The frontend communicates with the deployed backend through the `API_URL` environment variable.

## 7. Evaluation

The evaluation pipeline processes all 12 supplied public cases and 5 additional custom cases.

The additional cases cover scenarios including:

- normal inpatient treatment
- waiting-period handling
- domiciliary treatment
- day-care treatment
- an unrecognized treatment type

The evaluation results are written to:

`artifacts/evaluation_results.json`

Automated tests are also included and can be executed with:

```bash
pytest -q

The evaluation script can be reproduced with:

python scripts/evaluate.py
### 8. Deployment and Engineering Tradeoffs

* Backend deployed on **Render**.
* Frontend deployed on **Streamlit Community Cloud**.
* Free Render deployment has a **512 MB memory constraint**.
* Transformer-based dense retrieval and cross-encoder reranking require more memory.
* Therefore, the deployed version uses **lightweight BM25 retrieval** for reliability.
* Dense retrieval and reranking components remain in the repository for future deployment on larger infrastructure.
* This tradeoff prioritizes **reliable deployment and reproducibility**.

### 9. Limitations and Future Improvements

* Dense retrieval is not enabled in the current production deployment.
* Transformer-based reranking is not enabled in production.
* Current agents use deterministic retrieval and rule-based reasoning rather than an external LLM.
* Retrieval-quality and citation-quality metrics could be expanded.
* A larger deployment environment could enable dense retrieval and reranking.
* A stronger policy-grounded reasoning layer could be added.
* Additional validation agents and more granular decision statuses could further improve the architecture.

### 10. Summary

* The system demonstrates:

  * Policy ingestion and chunking
  * Traceable policy evidence retrieval
  * Specialized multi-agent claim analysis
  * Structured decision aggregation
  * Abstention/manual-review behavior
  * FastAPI backend
  * Streamlit frontend
  * Automated testing
  * Reproducible evaluation
* The architecture is modular, allowing retrieval, agents, decision logic, API serving, and evaluation to be extended independently.

Available next action: Create a downloadable PDF file here in this chat containing the finalized decisions and immediate actions above
