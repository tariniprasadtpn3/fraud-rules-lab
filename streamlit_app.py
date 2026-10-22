"""Streamlit UI for the fraud rules lab.  Run:  streamlit run streamlit_app.py

Generates synthetic transactions, applies the selected rules and shows
precision/recall plus the flagged transactions. All data is synthetic.
"""

from __future__ import annotations

import streamlit as st

from src.ui import available_rules, flagged_frame, metrics_frame, run_pipeline

st.set_page_config(page_title="Fraud rules lab", layout="wide")
st.title("Fraud rules lab")
st.caption("A toy rule engine on synthetic data. Nothing here is real customer or bank data.")

with st.sidebar:
    st.header("Data")
    seed = st.number_input("Seed", min_value=0, value=42, step=1)
    n_accounts = st.slider("Accounts", 10, 300, 50)
    days = st.slider("Days", 6, 90, 30)
    ratio = st.slider("Fraud account ratio", 0.0, 1.0, 0.2, 0.05)
    st.header("Rules")
    names = available_rules()
    selected = st.multiselect("Active rules", names, default=names)
    min_rules = st.slider("Minimum rules that must agree", 1, max(1, len(selected)), 1)

if not selected:
    st.warning("Select at least one rule in the sidebar.")
    st.stop()

result = run_pipeline(n_accounts, days, ratio, int(seed), selected, min_rules)
metrics = metrics_frame(result.metrics)
flagged = flagged_frame(result.flagged)

overall = result.metrics["overall"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Transactions", len(result.transactions))
c2.metric("Flagged", len(result.flagged))
c3.metric("Precision", f"{overall.precision:.2f}")
c4.metric("Recall", f"{overall.recall:.2f}")

st.subheader("Precision and recall per rule")
per_rule = metrics.drop(index="overall", errors="ignore")
st.bar_chart(per_rule[["precision", "recall"]])
st.dataframe(metrics.style.format({"precision": "{:.2f}", "recall": "{:.2f}", "f1": "{:.2f}"}),
             use_container_width=True)

st.subheader("Flagged transactions")
only_fraud = st.checkbox("Only show true fraud")
only_false = st.checkbox("Only show false positives")
view = flagged
if only_fraud:
    view = view[view["is_fraud"]]
if only_false:
    view = view[~view["is_fraud"]]
st.dataframe(view, use_container_width=True, hide_index=True)
st.download_button("Download flagged CSV", view.to_csv(index=False), "flagged.csv", "text/csv")
