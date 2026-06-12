import streamlit as st
import pandas as pd
from data_utils import (
    generate_payments_dataset, generate_credits_dataset, generate_access_dataset
)
from logic_registry import LOGIC_REGISTRY

# -------------------------------
# Custom CSS for background and aesthetics
# -------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fdfdfd, #eef5fb);
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-size: 28px;
        white-space: nowrap;
    }
    .chart-title {
        font-weight: bold;
        font-size: 18px;
        color: #2c3e50;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=False)  # Removed unsafe HTML rendering

# -------------------------------
# Load datasets
# -------------------------------
try:
    datasets = {
        "payments": generate_payments_dataset(),
        "credits": generate_credits_dataset(),
        "access": generate_access_dataset()
    }
except Exception as e:
    st.error("Error loading datasets. Please try again later.")
    st.stop()

st.title("Customer Risk Logic Dashboard")

# -------------------------------
# Logic selection
# -------------------------------
logic_choice = st.sidebar.selectbox("Choose a logic to run:", list(LOGIC_REGISTRY.keys()))
logic_def = LOGIC_REGISTRY.get(logic_choice)

if not logic_def:
    st.error("Selected logic is not available.")
    st.stop()

# -------------------------------
# Build sidebar inputs dynamically
# -------------------------------
params = {}
for p in logic_def["params"]:
    if p["type"] == "number":
        params[p["name"]] = st.sidebar.number_input(
            p["label"],
            min_value=p.get("min", 0),
            max_value=p.get("max", None),
            value=p["default"]
        )
    elif p["type"] == "select":
        params[p["name"]] = st.sidebar.selectbox(
            p["label"],
            p["options"],
            index=p["options"].index(p["default"])
        )

# -------------------------------
# Run logic dynamically
# -------------------------------
dataset = datasets.get(logic_def["dataset"])
func = logic_def.get("function")

if not dataset or not func:
    st.error("Dataset or function not found for the selected logic.")
    st.stop()

try:
    result, result_ids = func(dataset, **params)
except Exception as e:
    st.error("Error executing logic function. Please check your inputs and try again.")
    st.stop()

# -------------------------------
# Display results
# -------------------------------
st.subheader("Filtered Customers")
st.dataframe(result.reset_index(drop=True))

# -------------------------------
# Render charts dynamically
# -------------------------------
if not result.empty:
    for chart in logic_def.get("charts", []):
        st.markdown(f"<div class='chart-title'>{chart['title']}</div>", unsafe_allow_html=False)

        # Prepare data
        if chart["groupby"]:
            grouped = result.groupby(chart["groupby"])[chart["column"]].sum() if chart["type"] == "bar" else result.groupby(chart["groupby"])[chart["column"]].count()
        else:
            grouped = result[chart["column"]].value_counts()

        # Render chart
        if chart["type"] == "bar":
            st.bar_chart(grouped)
        elif chart["type"] == "line":
            # Ensure datetime for line charts
            if chart["groupby"] and "date" in chart["groupby"]:
                result[chart["groupby"]] = pd.to_datetime(result[chart["groupby"]])
                grouped = result.groupby(chart["groupby"])[chart["column"]].sum()
            st.line_chart(grouped)

# -------------------------------
# Download filtered results
# -------------------------------
if not result.empty:
    csv = result.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered data (CSV)",
        data=csv,
        file_name=f"{logic_choice}_results.csv",
        mime="text/csv"
    )