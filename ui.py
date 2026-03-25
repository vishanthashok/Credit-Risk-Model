"""UI helper functions for the Streamlit credit risk app."""

from __future__ import annotations

from typing import Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_sidebar_inputs() -> Dict[str, float]:
    """Render sidebar controls and return base financial inputs."""

    st.sidebar.header("Borrower Financial Inputs")

    revenue = st.sidebar.number_input("Revenue", min_value=0.0, value=12_000_000.0, step=100_000.0)
    ebitda = st.sidebar.number_input("EBITDA", min_value=0.0, value=2_000_000.0, step=50_000.0)
    ebitda_margin = st.sidebar.number_input(
        "EBITDA Margin (%)", min_value=0.0, max_value=100.0, value=16.7, step=0.1
    )
    debt = st.sidebar.number_input("Debt", min_value=0.0, value=7_500_000.0, step=50_000.0)
    interest_expense = st.sidebar.number_input(
        "Interest Expense", min_value=0.0, value=400_000.0, step=10_000.0
    )
    total_assets = st.sidebar.number_input("Total Assets", min_value=0.0, value=20_000_000.0, step=100_000.0)
    current_assets = st.sidebar.number_input(
        "Current Assets", min_value=0.0, value=6_000_000.0, step=50_000.0
    )
    current_liabilities = st.sidebar.number_input(
        "Current Liabilities", min_value=0.0, value=3_500_000.0, step=50_000.0
    )

    use_margin_override = st.sidebar.checkbox(
        "Use EBITDA Margin to recalculate EBITDA", value=False,
        help="If enabled, EBITDA will be overwritten as Revenue × EBITDA Margin.",
    )

    if use_margin_override:
        ebitda = revenue * (ebitda_margin / 100.0)

    return {
        "revenue": revenue,
        "ebitda": ebitda,
        "ebitda_margin": ebitda_margin,
        "debt": debt,
        "interest_expense": interest_expense,
        "total_assets": total_assets,
        "current_assets": current_assets,
        "current_liabilities": current_liabilities,
    }


def render_gauge(score: float) -> None:
    """Display gauge chart for the credit score."""

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Credit Score (0-100)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#2E86AB"},
                "steps": [
                    {"range": [0, 40], "color": "#f8d7da"},
                    {"range": [40, 70], "color": "#fff3cd"},
                    {"range": [70, 100], "color": "#d1e7dd"},
                ],
            },
        )
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_contribution_chart(contributions: Dict[str, float]) -> None:
    """Display bar chart for weighted factor contributions."""

    contrib_df = pd.DataFrame(
        {"Factor": list(contributions.keys()), "Contribution": list(contributions.values())}
    )
    fig = go.Figure(
        go.Bar(
            x=contrib_df["Factor"],
            y=contrib_df["Contribution"],
            marker_color=["#d62728", "#ff7f0e", "#1f77b4", "#2ca02c"],
        )
    )
    fig.update_layout(title="Risk Contribution by Factor", xaxis_title="Factor", yaxis_title="Weighted Impact")
    st.plotly_chart(fig, use_container_width=True)


def render_metrics_table(metrics: Dict[str, float]) -> None:
    """Render a formatted table for key ratios."""

    table_df = pd.DataFrame(
        {
            "Metric": list(metrics.keys()),
            "Value": [round(v, 3) for v in metrics.values()],
        }
    )
    st.dataframe(table_df, use_container_width=True, hide_index=True)
