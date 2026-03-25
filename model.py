"""Model functions for credit risk scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class RiskFeatures:
    """Container for normalized model features."""

    debt_to_ebitda: float
    interest_coverage: float
    current_ratio: float
    profit_margin: float


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two values and avoid divide-by-zero errors."""

    if denominator == 0:
        return default
    return numerator / denominator


def compute_derived_metrics(
    revenue: float,
    ebitda: float,
    debt: float,
    interest_expense: float,
    current_assets: float,
    current_liabilities: float,
) -> Dict[str, float]:
    """Compute borrower health ratios used by the model."""

    debt_to_ebitda = safe_divide(debt, ebitda, default=10.0)
    interest_coverage = safe_divide(ebitda, interest_expense, default=0.0)
    current_ratio = safe_divide(current_assets, current_liabilities, default=0.0)
    profit_margin = safe_divide(ebitda, revenue, default=0.0)

    return {
        "Debt to EBITDA": debt_to_ebitda,
        "Interest Coverage": interest_coverage,
        "Current Ratio": current_ratio,
        "Profit Margin": profit_margin,
    }


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))


def _normalize_metrics(metrics: Dict[str, float]) -> RiskFeatures:
    """Normalize metrics into 0-1 risk-style features.

    1.0 means riskier condition for each factor.
    """

    debt_norm = float(np.clip((metrics["Debt to EBITDA"] - 1.0) / 7.0, 0.0, 1.0))

    coverage_raw = metrics["Interest Coverage"]
    coverage_norm = float(np.clip((5.0 - coverage_raw) / 5.0, 0.0, 1.0))

    liquidity_raw = metrics["Current Ratio"]
    liquidity_norm = float(np.clip((2.0 - liquidity_raw) / 2.0, 0.0, 1.0))

    margin_raw = metrics["Profit Margin"]
    margin_norm = float(np.clip((0.30 - margin_raw) / 0.30, 0.0, 1.0))

    return RiskFeatures(
        debt_to_ebitda=debt_norm,
        interest_coverage=coverage_norm,
        current_ratio=liquidity_norm,
        profit_margin=margin_norm,
    )


def score_credit_risk(metrics: Dict[str, float]) -> Tuple[float, float, Dict[str, float]]:
    """Estimate probability of default and score from 0-100.

    Returns:
        probability_of_default, credit_score, weighted_contributions
    """

    normalized = _normalize_metrics(metrics)

    weights = {
        "Debt to EBITDA": 1.5,
        "Interest Coverage": 1.3,
        "Current Ratio": 1.0,
        "Profit Margin": 0.8,
    }

    intercept = -1.2
    linear_score = (
        intercept
        + normalized.debt_to_ebitda * weights["Debt to EBITDA"]
        + normalized.interest_coverage * weights["Interest Coverage"]
        + normalized.current_ratio * weights["Current Ratio"]
        + normalized.profit_margin * weights["Profit Margin"]
    )

    pd = float(np.clip(_sigmoid(linear_score), 0.0, 1.0))
    credit_score = float(np.clip((1.0 - pd) * 100.0, 0.0, 100.0))

    contributions = {
        "Debt to EBITDA": normalized.debt_to_ebitda * weights["Debt to EBITDA"],
        "Interest Coverage": normalized.interest_coverage * weights["Interest Coverage"],
        "Current Ratio": normalized.current_ratio * weights["Current Ratio"],
        "Profit Margin": normalized.profit_margin * weights["Profit Margin"],
    }

    return pd, credit_score, contributions


def risk_category(probability_of_default: float) -> str:
    """Map probability of default to a simple category."""

    if probability_of_default < 0.25:
        return "Low"
    if probability_of_default < 0.50:
        return "Medium"
    return "High"
