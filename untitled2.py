import streamlit as st
import pandas as pd
import numpy as np

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Smart Traffic Management with Emission Reduction",
    layout="wide"
)

st.title("🚦 Smart Traffic Management System with Emission Reduction")
st.markdown("---")

# =========================
# FILE UPLOAD (CLOUD SAFE)
# =========================
st.sidebar.header("📂 Upload Dataset")
uploaded_csv = st.sidebar.file_uploader(
    "Upload traffic_emission_merge.csv",
    type="csv"
)

if uploaded_csv is None:
    st.info("⬅ Upload the dataset to start")
    st.stop()

traffic_emission = pd.read_csv(uploaded_csv).dropna()

# =========================
# LAYOUT
# =========================
left_col, right_col = st.columns(2)

# =====================================================
# LEFT COLUMN → TRAFFIC PREDICTION (DEMO MODE)
# =====================================================
with left_col:
    st.subheader("🚦 Smart Traffic Management (Demo Mode)")

    hour = st.number_input("Hour (0–23)", 0, 23, 12)
    temp = st.number_input("Temperature (°C)", value=30.0)
    rain = st.number_input("Rain in last 1 hour (mm)", value=0.0)
    snow = st.number_input("Snow in last 1 hour (mm)", value=0.0)
    clouds = st.number_input("Cloud Coverage (%)", 0, 100, 50)

    # ---- Simulated Prediction (Cloud-safe) ----
    traffic_volume = (
        1000
        + hour * 20
        - rain * 50
        - snow * 100
        + clouds * 2
    )

    st.success(
        f"🚗 Estimated Traffic Volume: {int(max(traffic_volume, 100))} vehicles/hour"
    )

    # =========================
    # ACTUAL VS PREDICTED (REBUILT)
    # =========================
    st.markdown("### 📈 Actual vs Predicted Traffic")

    if "traffic_volume" in traffic_emission.columns:
        traffic_emission["Predicted"] = (
            traffic_emission["traffic_volume"].mean()
        )

        st.scatter_chart(
            traffic_emission[["traffic_volume", "Predicted"]]
            .rename(columns={"traffic_volume": "Actual"})
        )

# =====================================================
# RIGHT COLUMN → EMISSION REDUCTION
# =====================================================
with right_col:
    st.subheader("🌱 Emission Reduction")

    emission_factor = st.number_input(
        "Emission Factor (kg CO₂ / vehicle / hour)",
        min_value=0.05,
        max_value=1.0,
        value=0.25
    )

    reduction_rate = st.slider(
        "Traffic Optimization Reduction (%)",
        5, 50, 20
    ) / 100

    traffic_emission["CO2_before"] = (
        traffic_emission["traffic_volume"] * emission_factor
    )

    traffic_emission["CO2_after"] = (
        traffic_emission["CO2_before"] * (1 - reduction_rate)
    )

    traffic_emission["CO2_saved"] = (
        traffic_emission["CO2_before"] - traffic_emission["CO2_after"]
    )

    st.markdown("### 📊 Emission Summary")

    st.metric(
        "Total CO₂ Before (kg)",
        f"{traffic_emission['CO2_before'].sum():,.0f}"
    )
    st.metric(
        "Total CO₂ After (kg)",
        f"{traffic_emission['CO2_after'].sum():,.0f}"
    )
    st.metric(
        "Total CO₂ Saved (kg)",
        f"{traffic_emission['CO2_saved'].sum():,.0f}"
    )

    # =========================
    # HOURLY CO₂ (HISTORICAL)
    # =========================
    if "hour" in traffic_emission.columns:
        hourly_co2 = (
            traffic_emission
            .groupby("hour")["CO2_before"]
            .mean()
        )

        st.line_chart(hourly_co2)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Smart Traffic Management System with Emission Reduction (Cloud Demo)")
