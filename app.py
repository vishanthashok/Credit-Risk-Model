"""Production-ready Streamlit credit risk scoring app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from model import compute_derived_metrics, risk_category, score_credit_risk
from ui import (
    render_contribution_chart,
    render_gauge,
    render_metrics_table,
    render_sidebar_inputs,
)
from utils import (
    REQUIRED_COLUMNS,
    apply_financial_improvements,
    build_result_row,
    run_sensitivity_analysis,
    score_uploaded_companies,
)


st.set_page_config(page_title="Credit Risk Model", page_icon="📉", layout="wide")
st.title("📉 Credit Risk Model App")
st.caption("Estimate probability of default, risk category, and a 0-100 credit score.")


base_inputs = render_sidebar_inputs()

metrics = compute_derived_metrics(
    revenue=base_inputs["revenue"],
    ebitda=base_inputs["ebitda"],
    debt=base_inputs["debt"],
    interest_expense=base_inputs["interest_expense"],
    current_assets=base_inputs["current_assets"],
    current_liabilities=base_inputs["current_liabilities"],
)

probability_of_default, credit_score, contributions = score_credit_risk(metrics)
category = risk_category(probability_of_default)

col1, col2, col3 = st.columns(3)
col1.metric("Probability of Default", f"{probability_of_default:.1%}")
col2.metric("Risk Category", category)
col3.metric("Credit Score", f"{credit_score:.1f}")

left, right = st.columns([1, 1])
with left:
    render_gauge(credit_score)
with right:
    render_contribution_chart(contributions)

st.subheader("Key Derived Metrics")
render_metrics_table(metrics)

results_row = build_result_row(base_inputs)
results_df = pd.DataFrame([results_row])

st.download_button(
    label="Download current result as CSV",
    data=results_df.to_csv(index=False),
    file_name="credit_risk_result.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Sensitivity Analysis (Debt and EBITDA)")
sensitivity_df = run_sensitivity_analysis(base_inputs)
st.dataframe(
    sensitivity_df[
        [
            "Debt Multiplier",
            "EBITDA Multiplier",
            "Probability of Default",
            "Credit Score",
            "Risk Category",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("Simulate Financial Improvements")
sim_col1, sim_col2 = st.columns(2)
debt_reduction_pct = sim_col1.slider("Debt Reduction (%)", min_value=0, max_value=50, value=10, step=1)
ebitda_improvement_pct = sim_col2.slider(
    "EBITDA Improvement (%)", min_value=0, max_value=50, value=10, step=1
)

improved_inputs = apply_financial_improvements(base_inputs, debt_reduction_pct, ebitda_improvement_pct)
improved_row = build_result_row(improved_inputs)
comparison_df = pd.DataFrame(
    [
        {
            "Scenario": "Current",
            "Probability of Default": results_row["Probability of Default"],
            "Credit Score": results_row["Credit Score"],
            "Risk Category": results_row["Risk Category"],
        },
        {
            "Scenario": "Improved",
            "Probability of Default": improved_row["Probability of Default"],
            "Credit Score": improved_row["Credit Score"],
            "Risk Category": improved_row["Risk Category"],
        },
    ]
)
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Batch Scoring: Upload Multiple Companies (CSV)")
st.caption(f"Required columns: {', '.join(REQUIRED_COLUMNS)}")

uploaded = st.file_uploader("Upload company financials CSV", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        batch_results = score_uploaded_companies(uploaded_df)
        st.success(f"Scored {len(batch_results)} companies.")
        st.dataframe(batch_results, use_container_width=True, hide_index=True)
        st.download_button(
            label="Download batch results as CSV",
            data=batch_results.to_csv(index=False),
            file_name="batch_credit_risk_results.csv",
            mime="text/csv",
        )
    except Exception as exc:  # pragma: no cover - streamlit runtime feedback
        st.error(f"Unable to process file: {exc}")
