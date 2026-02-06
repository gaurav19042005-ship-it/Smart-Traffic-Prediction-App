import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Smart Traffic Management with Emission Reduction",
    layout="wide"
)

st.title("🚦 Smart Traffic Management System with Emission Reduction")
st.markdown("---")

DATA_FILE = "traffic_emission_merge.csv"

try:
    traffic_emission = pd.read_csv(DATA_FILE).dropna()
except FileNotFoundError:
    st.error("❌ traffic_emission_merge.csv not found in project folder")
    st.stop()

required_cols = ["traffic_volume", "hour"]
missing = [c for c in required_cols if c not in traffic_emission.columns]

if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🚦 Smart Traffic Management")

    hour = st.number_input("Hour (0–23)", 0, 23, 12)
    temp = st.number_input("Temperature (°C)", value=30.0)
    rain = st.number_input("Rain in last 1 hour (mm)", value=0.0)
    snow = st.number_input("Snow in last 1 hour (mm)", value=0.0)
    clouds = st.number_input("Cloud Coverage (%)", 0, 100, 50)

    estimated_traffic = (
        traffic_emission["traffic_volume"].mean()
        + hour * 15
        - rain * 40
        - snow * 80
        + clouds * 1.5
    )

    estimated_traffic = max(estimated_traffic, 100)

    st.success(
        f"🚗 Estimated Traffic Volume: {int(estimated_traffic)} vehicles/hour"
    )

    st.markdown("### 📈 Actual vs Estimated Traffic")

    traffic_emission["Estimated"] = traffic_emission["traffic_volume"].mean()

    avp_df = traffic_emission[["traffic_volume", "Estimated"]].rename(
        columns={"traffic_volume": "Actual"}
    )

    st.scatter_chart(avp_df)

with right_col:
    st.subheader("🌱 Emission Reduction")

    emission_factor = st.number_input(
        "Emission Factor (kg CO₂ / vehicle / hour)",
        0.05, 1.0, 0.25
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

    st.markdown("### 🕒 Hourly CO₂ Emission")

    hourly_co2 = (
        traffic_emission
        .groupby("hour")["CO2_before"]
        .mean()
    )

    st.line_chart(hourly_co2)

st.markdown("---")
st.caption("Smart Traffic Management System with Emission Reduction")
