
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

# Average Daily Revenue by Month

st.divider()
st.subheader("📅 Average Daily Revenue by Month")

avg_daily = monthly[["TransactionDate", "TransactionAmount"]].copy()

# Get the number of days in each month
avg_daily["Days in Month"] = (
    avg_daily["TransactionDate"].dt.days_in_month
)

# Calculate average daily revenue
avg_daily["Average Daily Revenue"] = (
    avg_daily["TransactionAmount"] / avg_daily["Days in Month"]
)

# Identify the month with the highest average daily revenue
best_daily_month = avg_daily.loc[
    avg_daily["Average Daily Revenue"].idxmax()
]

st.metric(
    "Highest Average Daily Revenue",
    f"${best_daily_month['Average Daily Revenue']:,.0f}/day",
    best_daily_month["TransactionDate"].strftime("%B %Y")
)

# Create chart
fig3 = px.bar(
    avg_daily,
    x="TransactionDate",
    y="Average Daily Revenue",
    title="Average Daily Revenue per Month",
    labels={
        "TransactionDate": "Month",
        "Average Daily Revenue": "Average Daily Revenue ($)"
    }
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# Revenue by Day of the Week

st.divider()
st.subheader("📆 Revenue by Day of the Week")

# Map weekday numbers to names
weekday_names = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

weekday_sales = df.groupby("day_of_week").agg(
    Average_Revenue=("TransactionAmount", "mean"),
    Total_Revenue=("TransactionAmount", "sum"),
    Number_of_Days=("TransactionAmount", "count")
).reset_index()

weekday_sales["Day"] = weekday_sales["day_of_week"].map(weekday_names)

# Ensure days appear in calendar order
weekday_sales = weekday_sales.sort_values("day_of_week")

# Find the weekday with the highest average revenue
best_weekday = weekday_sales.loc[
    weekday_sales["Average_Revenue"].idxmax()
]

st.metric(
    "Highest Average Revenue Day",
    best_weekday["Day"],
    f"${best_weekday['Average_Revenue']:,.0f} average revenue"
)

# Average revenue chart
fig4 = px.bar(
    weekday_sales,
    x="Day",
    y="Average_Revenue",
    title="Average Daily Revenue by Weekday",
    labels={
        "Day": "Day of Week",
        "Average_Revenue": "Average Revenue ($)"
    }
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# Detailed weekday breakdown
st.subheader("Weekday Revenue Breakdown")

weekday_display = weekday_sales[
    ["Day", "Average_Revenue", "Total_Revenue", "Number_of_Days"]
].rename(columns={
    "Average_Revenue": "Average Daily Revenue ($)",
    "Total_Revenue": "Total Revenue ($)",
    "Number_of_Days": "Days Recorded"
})

st.dataframe(
    weekday_display.style.format({
        "Average Daily Revenue ($)": "${:,.0f}",
        "Total Revenue ($)": "${:,.0f}",
        "Days Recorded": "{:,.0f}"
    }),
    use_container_width=True,
    hide_index=True
)
