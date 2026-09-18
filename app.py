import requests
import streamlit as st

from src.claim_engine.evaluation.public_case_rules import evaluate_public_case
from src.claim_engine.evaluation.expense_calculator import calculate_expenses


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/analyze",
)

st.set_page_config(
    page_title="Aptino Claim Decision Engine",
    page_icon="🏥",
    layout="wide",
)

st.title("Aptino Claim Decision Engine")
st.write(
    "Enter claim information to receive a transparent preliminary "
    "insurance-claim assessment."
)

st.warning(
    "This is a prototype. Results are preliminary and require verification "
    "of policy terms, documents, medical evidence, and applicable limits."
)


with st.form("claim_form"):
    st.subheader("Claim details")

    case_id = st.text_input("Claim ID", value="MANUAL-001")
    policy_start_date = st.date_input("Policy start date")
    claim_date = st.date_input("Claim date")

    patient_age = st.number_input(
        "Patient age",
        min_value=0,
        max_value=120,
        value=40,
    )

    hospital_name = st.text_input(
        "Hospital name",
        value="Example Hospital",
    )

    treatment_type = st.selectbox(
        "Treatment type",
        ["inpatient", "day_care", "domiciliary"],
    )

    admission_hours = st.number_input(
        "Admission duration in hours",
        min_value=0,
        value=24,
    )

    diagnosis = st.text_input(
        "Diagnosis",
        value="Not specified",
    )

    procedure = st.text_input(
        "Procedure",
        value="Not specified",
    )

    pre_existing = st.checkbox("Pre-existing condition")
    experimental = st.checkbox("Experimental treatment")

    hospital_room_unavailable = st.checkbox("Hospital room unavailable")
    patient_cannot_be_moved = st.checkbox(
        "Patient cannot be moved to a hospital"
    )

    st.subheader("Coverage details")

    policy_id = st.text_input(
        "Policy ID",
        value="USGIC-CSC-2017-2018",
    )

    sum_insured = st.number_input(
        "Sum insured (INR)",
        min_value=0,
        value=500000,
    )

    continuous_coverage_months = st.number_input(
        "Continuous coverage (months)",
        min_value=0,
        value=0,
    )

    prior_coverage_years = st.number_input(
        "Qualifying previous coverage (years)",
        min_value=0,
        value=0,
    )

    st.subheader("Expenses")

    room = st.number_input("Room expenses (INR)", min_value=0, value=0)
    doctor_fees = st.number_input("Doctor fees (INR)", min_value=0, value=0)
    medicines_diagnostics = st.number_input(
        "Medicines and diagnostics (INR)",
        min_value=0,
        value=0,
    )
    pre_hospitalization = st.number_input(
        "Pre-hospitalization (INR)",
        min_value=0,
        value=0,
    )
    post_hospitalization = st.number_input(
        "Post-hospitalization (INR)",
        min_value=0,
        value=0,
    )
    ambulance = st.number_input("Ambulance (INR)", min_value=0, value=0)

    submitted = st.form_submit_button("Analyze claim")


if submitted:
    claim_date_text = claim_date.isoformat()
    policy_start_date_text = policy_start_date.isoformat()

    case = {
        "case_id": case_id,
        "policy_id": policy_id,
        "policy_start_date": policy_start_date_text,
        "claim_date": claim_date_text,
        "sum_insured_inr": sum_insured,
        "continuous_coverage_months": continuous_coverage_months,
        "prior_insurer_continuous_years": prior_coverage_years,
        "patient": {"age": patient_age},
        "hospital": {
            "name": hospital_name,
            "network_provider": False,
        },
        "treatment": {
            "type": treatment_type,
            "admission_hours": admission_hours,
            "diagnosis": diagnosis,
            "procedure": procedure,
            "pre_existing": pre_existing,
            "experimental": experimental,
            "hospital_room_unavailable": hospital_room_unavailable,
            "patient_cannot_be_moved": patient_cannot_be_moved,
        },
        "expenses_inr": {
            "room": room,
            "doctor_fees": doctor_fees,
            "medicines_diagnostics": medicines_diagnostics,
            "pre_hospitalization": pre_hospitalization,
            "post_hospitalization": post_hospitalization,
            "ambulance": ambulance,
        },
        "documents": [],
    }

    st.divider()
    st.subheader("Assessment result")

    try:
        api_claim = {
            "claim_id": case_id,
            "patient_age": patient_age,
            "diagnosis": diagnosis,
            "treatment": (
                f"{treatment_type}: {procedure}; "
                f"admission duration: {admission_hours} hours"
            ),
            "hospital_name": hospital_name,
            "admission_date": claim_date_text,
            "discharge_date": claim_date_text,
            "claimed_amount": sum(
                [
                    room,
                    doctor_fees,
                    medicines_diagnostics,
                    pre_hospitalization,
                    post_hospitalization,
                    ambulance,
                ]
            ),
            "policy_start_date": policy_start_date_text,
            "notes": (
                f"Policy ID: {policy_id}; "
                f"Experimental: {experimental}; "
                f"Pre-existing: {pre_existing}; "
                f"Hospital room unavailable: "
                f"{hospital_room_unavailable}; "
                f"Patient cannot be moved: "
                f"{patient_cannot_be_moved}"
            ),
        }

        response = requests.post(
            API_URL,
            json=api_claim,
            timeout=120,
        )
        response.raise_for_status()
        agent_result = response.json()

        decision = agent_result.get("decision", "NEEDS_REVIEW")

        if decision == "REJECT":
            st.error(f"Decision: {decision}")
        elif decision == "APPROVE":
            st.success(f"Decision: {decision}")
        else:
            st.warning(f"Decision: {decision}")

        st.metric(
            "Confidence",
            f"{agent_result.get('confidence', 0.0):.2f}",
        )

        st.subheader("Reasoning")
        st.write(agent_result.get("reasoning", "No reasoning returned."))

        st.subheader("Key findings")
        findings = agent_result.get("key_findings", [])
        if findings:
            for finding in findings:
                st.write(f"- {finding}")
        else:
            st.info("No key findings returned.")

        st.subheader("Applicable limits")
        limits = agent_result.get("applicable_limits", [])
        if limits:
            for limit in limits:
                st.write(f"- {limit}")
        else:
            st.info("No applicable limits returned.")

        st.subheader("Missing evidence")
        missing = agent_result.get("missing_evidence", [])
        if missing:
            for item in missing:
                st.write(f"- {item}")
        else:
            st.info("No missing evidence returned.")

        st.subheader("Policy citations")
        citations = agent_result.get("policy_citations", [])
        if citations:
            for citation in citations:
                st.write(f"- `{citation}`")
        else:
            st.info("No policy citations returned.")

        st.subheader("Agent decisions")

        for agent in agent_result.get("agent_decisions", []):
            with st.expander(agent.get("agent_name", "Agent")):
                st.write(f"**Decision:** {agent.get('decision')}")
                st.write(f"**Confidence:** {agent.get('confidence')}")
                st.write(f"**Reasoning:** {agent.get('reasoning')}")

                st.write("**Evidence:**")
                for evidence in agent.get("evidence", []):
                    st.json(evidence)

        st.subheader("Execution trace")

        trace = agent_result.get("execution_trace", [])
        if trace:
            for index, step in enumerate(trace, start=1):
                st.write(f"{index}. {step}")
        else:
            st.info("No execution trace returned.")

        abstention_reason = agent_result.get("abstention_reason")

        if abstention_reason:
            st.subheader("Abstention or review explanation")
            st.warning(abstention_reason)

    except requests.exceptions.RequestException as error:
        st.error(
            "Could not connect to FastAPI. Confirm that the backend is "
            "running at http://127.0.0.1:8000."
        )
        st.exception(error)

    st.subheader("Rule-based evaluation and expenses")

    rule_result = evaluate_public_case(case)
    expense_result = calculate_expenses(case)

    st.write("Rule-based decision:", rule_result.get("decision"))

    st.metric(
        "Total claimed amount",
        f"₹{expense_result['total_claimed_inr']:,.2f}",
    )

    st.json(expense_result)

    with st.expander("Full API result"):
        st.json(agent_result)

    with st.expander("Full rule-based result"):
        st.json(rule_result)