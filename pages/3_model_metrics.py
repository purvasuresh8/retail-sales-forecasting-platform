
import streamlit as st
import pandas as pd
import plotly.express as px

from xgboost import XGBRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import numpy as np

# ----------------------------------
# PAGE CONFIG
# ----------------------------------

st.set_page_config(
    page_title="Model Metrics",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Model Performance")

# ----------------------------------
# LOAD DATA
# ----------------------------------

df = pd.read_csv(
    "daily_sales_features.csv"
)

df["TransactionDate"] = pd.to_datetime(
    df["TransactionDate"]
)

df = df.sort_values("TransactionDate").reset_index(drop=True)

# ----------------------------------
# FEATURES
# ----------------------------------

features = [
    "lag_1",
    "lag_7",
    "rolling_mean_7",
    "rolling_mean_30"
]

# Remove rows with missing model features
df = df.dropna(subset=features + ["TransactionAmount"])

X = df[features]
y = df["TransactionAmount"]

# ----------------------------------
# CHRONOLOGICAL TRAIN / TEST SPLIT
# ----------------------------------

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

test_dates = df["TransactionDate"].iloc[split_index:]

# ----------------------------------
# TRAIN MODEL
# ----------------------------------

model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

predictions = model.predict(X_test)

# ----------------------------------
# METRICS
# ----------------------------------

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

# Average prediction bias
bias = np.mean(
    predictions - y_test
)

# ----------------------------------
# KPI CARDS
# ----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Mean Absolute Error (MAE)",
        f"${mae:,.0f}"
    )

with col2:
    st.metric(
        "Root Mean Squared Error (RMSE)",
        f"${rmse:,.0f}"
    )

with col3:
    st.metric(
        "R² Score",
        f"{r2:.4f}"
    )

with col4:
    st.metric(
        "Average Prediction Bias",
        f"${bias:+,.0f}"
    )

st.caption(
    "Metrics are calculated on the final 20% of chronologically ordered data, "
    "which is held out from model training."
)

st.divider()

# ----------------------------------
# FEATURE IMPORTANCE
# ----------------------------------

st.subheader("📊 Feature Importance")

importance_df = pd.DataFrame(
    {
        "Feature": features,
        "Importance": model.feature_importances_
    }
)

importance_df = importance_df.sort_values(
    "Importance",
    ascending=True
)

fig = px.bar(
    importance_df,
    x="Importance",
    y="Feature",
    orientation="h",
    title="XGBoost Feature Importance",
    color="Importance",
    color_continuous_scale="Blues"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------
# FEATURE TABLE
# ----------------------------------

st.subheader("📋 Importance Values")

st.dataframe(
    importance_df.sort_values(
        "Importance",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------------
# ACTUAL VS PREDICTED REVENUE
# ----------------------------------

st.subheader("🔍 Actual vs Predicted Revenue (Test Data)")

comparison_df = pd.DataFrame(
    {
        "TransactionDate": test_dates.values,
        "Actual Revenue": y_test.values,
        "Predicted Revenue": predictions
    }
)

fig2 = px.line(
    comparison_df,
    x="TransactionDate",
    y=["Actual Revenue", "Predicted Revenue"],
    title="Actual vs Predicted Daily Revenue",
    labels={
        "value": "Revenue ($)",
        "TransactionDate": "Date",
        "variable": "Legend"
    }
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.divider()

# ----------------------------------
# PREDICTION ERROR
# ----------------------------------

st.subheader("📉 Forecast Error Analysis")

comparison_df["Error ($)"] = (
    comparison_df["Predicted Revenue"]
    - comparison_df["Actual Revenue"]
)

comparison_df["Absolute Error ($)"] = (
    comparison_df["Error ($)"].abs()
)

comparison_df["Prediction Direction"] = np.where(
    comparison_df["Error ($)"] > 0,
    "Overprediction",
    np.where(
        comparison_df["Error ($)"] < 0,
        "Underprediction",
        "Exact Prediction"
    )
)

fig3 = px.bar(
    comparison_df,
    x="TransactionDate",
    y="Error ($)",
    title="Daily Prediction Error",
    labels={
        "Error ($)": "Error ($)",
        "TransactionDate": "Date"
    }
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ----------------------------------
# ERROR SUMMARY
# ----------------------------------

over_predictions = (
    comparison_df["Prediction Direction"] == "Overprediction"
).sum()

under_predictions = (
    comparison_df["Prediction Direction"] == "Underprediction"
).sum()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Days Overpredicted",
        f"{over_predictions:,}"
    )

with col2:
    st.metric(
        "Days Underpredicted",
        f"{under_predictions:,}"
    )

# ----------------------------------
# DETAILED TEST RESULTS
# ----------------------------------

st.subheader("📋 Test Prediction Details")

st.dataframe(
    comparison_df.style.format({
        "Actual Revenue": "${:,.2f}",
        "Predicted Revenue": "${:,.2f}",
        "Error ($)": "${:+,.2f}",
        "Absolute Error ($)": "${:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)
