"""Utility functions for sensitivity analysis, simulation, and batch scoring."""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from model import compute_derived_metrics, risk_category, score_credit_risk


REQUIRED_COLUMNS = [
    "Revenue",
    "EBITDA",
    "Debt",
    "Interest Expense",
    "Current Assets",
    "Current Liabilities",
]


def build_result_row(financials: Dict[str, float]) -> Dict[str, float | str]:
    """Build one output row from raw financial fields."""

    metrics = compute_derived_metrics(
        revenue=financials["revenue"],
        ebitda=financials["ebitda"],
        debt=financials["debt"],
        interest_expense=financials["interest_expense"],
        current_assets=financials["current_assets"],
        current_liabilities=financials["current_liabilities"],
    )
    probability_of_default, credit_score, _ = score_credit_risk(metrics)

    return {
        "Revenue": financials["revenue"],
        "EBITDA": financials["ebitda"],
        "Debt": financials["debt"],
        "Interest Expense": financials["interest_expense"],
        "Current Assets": financials["current_assets"],
        "Current Liabilities": financials["current_liabilities"],
        "Debt to EBITDA": metrics["Debt to EBITDA"],
        "Interest Coverage": metrics["Interest Coverage"],
        "Current Ratio": metrics["Current Ratio"],
        "Profit Margin": metrics["Profit Margin"],
        "Probability of Default": probability_of_default,
        "Credit Score": credit_score,
        "Risk Category": risk_category(probability_of_default),
    }


def run_sensitivity_analysis(base_inputs: Dict[str, float]) -> pd.DataFrame:
    """Scenario grid for debt and EBITDA shocks around baseline."""

    debt_multipliers = np.array([0.8, 0.9, 1.0, 1.1, 1.2])
    ebitda_multipliers = np.array([0.8, 0.9, 1.0, 1.1, 1.2])

    rows = []
    for d_mult in debt_multipliers:
        for e_mult in ebitda_multipliers:
            scenario = base_inputs.copy()
            scenario["debt"] = base_inputs["debt"] * d_mult
            scenario["ebitda"] = base_inputs["ebitda"] * e_mult
            result = build_result_row(scenario)
            result["Debt Multiplier"] = d_mult
            result["EBITDA Multiplier"] = e_mult
            rows.append(result)

    return pd.DataFrame(rows)


def apply_financial_improvements(
    base_inputs: Dict[str, float], debt_reduction_pct: float, ebitda_improvement_pct: float
) -> Dict[str, float]:
    """Apply user-defined improvements to debt and EBITDA."""

    improved = base_inputs.copy()
    improved["debt"] = base_inputs["debt"] * (1 - debt_reduction_pct / 100.0)
    improved["ebitda"] = base_inputs["ebitda"] * (1 + ebitda_improvement_pct / 100.0)
    return improved


def score_uploaded_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Score a batch CSV of companies using required column names."""

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    scored_rows = []
    for _, row in df.iterrows():
        financials = {
            "revenue": float(row["Revenue"]),
            "ebitda": float(row["EBITDA"]),
            "debt": float(row["Debt"]),
            "interest_expense": float(row["Interest Expense"]),
            "current_assets": float(row["Current Assets"]),
            "current_liabilities": float(row["Current Liabilities"]),
        }
        scored_rows.append(build_result_row(financials))

    return pd.DataFrame(scored_rows)
