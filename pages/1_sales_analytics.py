
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Sales Analytics")

df = pd.read_csv(
    "daily_sales_features.csv"
)

df["TransactionDate"] = pd.to_datetime(
    df["TransactionDate"]
)

# KPIs

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Revenue",
        f"${df['TransactionAmount'].sum():,.0f}"
    )

with col2:
    st.metric(
        "Average Revenue",
        f"${df['TransactionAmount'].mean():,.0f}"
    )

with col3:
    st.metric(
        "Peak Revenue",
        f"${df['TransactionAmount'].max():,.0f}"
    )

st.divider()

# Revenue Trend

fig = px.line(
    df,
    x="TransactionDate",
    y="TransactionAmount",
    title="Daily Revenue Trend"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# Monthly Revenue

monthly = (
    df
    .set_index("TransactionDate")
    .resample("ME")
    .sum(numeric_only=True)
    .reset_index()
)

fig2 = px.bar(
    monthly,
    x="TransactionDate",
    y="TransactionAmount",
    title="Monthly Revenue"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# Monthly Sales Performance & Growth

st.divider()
st.subheader("📈 Monthly Sales Performance & Growth")

monthly_perf = monthly[["TransactionDate", "TransactionAmount"]].copy()

monthly_perf["Revenue Change ($)"] = (
    monthly_perf["TransactionAmount"].diff()
)

monthly_perf["MoM Growth (%)"] = (
    monthly_perf["TransactionAmount"].pct_change() * 100
)

monthly_perf["Month"] = (
    monthly_perf["TransactionDate"].dt.strftime("%B %Y")
)

# Best and worst performing months

best_month = monthly_perf.loc[
    monthly_perf["TransactionAmount"].idxmax()
]

worst_month = monthly_perf.loc[
    monthly_perf["TransactionAmount"].idxmin()
]

# Performance KPIs

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Best Sales Month",
        best_month["Month"],
        f"${best_month['TransactionAmount']:,.0f}"
    )

with col2:
    st.metric(
        "Lowest Sales Month",
        worst_month["Month"],
        f"${worst_month['TransactionAmount']:,.0f}"
    )

# Monthly Growth Table

monthly_display = monthly_perf[
    ["Month", "TransactionAmount", "Revenue Change ($)", "MoM Growth (%)"]
].copy()

monthly_display = monthly_display.rename(
    columns={"TransactionAmount": "Monthly Revenue ($)"}
)

st.dataframe(
    monthly_display.style.format({
        "Monthly Revenue ($)": "${:,.0f}",
        "Revenue Change ($)": "${:+,.0f}",
        "MoM Growth (%)": "{:+.2f}%"
    }, na_rep="—"),
    use_container_width=True,
    hide_index=True
)
