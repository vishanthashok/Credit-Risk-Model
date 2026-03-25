# Credit Risk Model (Streamlit)

A portfolio-ready Streamlit app that estimates probability of default (PD), assigns a risk category, and produces a 0-100 credit score from borrower financials.

## Features
- Sidebar borrower inputs and dashboard outputs
- Derived ratio calculations
- Logistic-regression-style scoring function
- Gauge chart and factor contribution chart
- Sensitivity analysis for debt and EBITDA
- Improvement simulation scenarios
- CSV export of results
- Batch scoring via CSV upload

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Batch CSV format
Required columns:
- `Revenue`
- `EBITDA`
- `Debt`
- `Interest Expense`
- `Current Assets`
- `Current Liabilities`
