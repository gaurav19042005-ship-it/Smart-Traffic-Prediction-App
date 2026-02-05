import streamlit as st
import pandas as pd
import numpy as np
import joblib as jb

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
# LOAD DATA & MODELS
# =========================
traffic_emission = pd.read_csv(
    r"C:\Users\gaura\Downloads\city data.csv\traffic_emission_merge.csv"
).dropna()

traffic_model = jb.load(
    r"C:\Users\gaura\Downloads\city data.csv\hourly traffic.pkl"
)

feature_importance_model = jb.load(
    r"C:\Users\gaura\Downloads\city data.csv\feature importance.pkl"
)

# =========================
# LAYOUT
# =========================
left_col, right_col = st.columns(2)

# =====================================================
# LEFT COLUMN → TRAFFIC PREDICTION
# =====================================================
with left_col:
    st.subheader("🚦 Smart Traffic Management")

    hour = st.number_input("Hour (0–23)", 0, 23, 12)
    temp = st.number_input("Temperature (°C)", value=30.0)
    rain = st.number_input("Rain in last 1 hour (mm)", value=0.0)
    snow = st.number_input("Snow in last 1 hour (mm)", value=0.0)
    clouds = st.number_input("Cloud Coverage (%)", 0, 100, 50)

    if st.button("Predict Traffic Volume"):
        X_user = np.array([[hour, temp, rain, snow, clouds]])
        pred = traffic_model.predict(X_user)
        st.success(f"🚗 Predicted Traffic Volume: {int(pred[0])} vehicles/hour")

    # =========================
    # FEATURE IMPORTANCE
    # =========================
    st.markdown("### 📊 Feature Importance")

    fi_df = pd.DataFrame({
        "Feature": ["hour", "temp", "rain_1h", "snow_1h", "clouds_all"],
        "Importance": feature_importance_model.feature_importances_
    })

    st.bar_chart(fi_df.set_index("Feature"))

    # =========================
    # ACTUAL VS PREDICTED (REBUILT – CORRECT)
    # =========================
    st.markdown("### 📈 Actual vs Predicted Traffic")

    required_cols = ["hour", "temp", "rain_1h", "snow_1h", "clouds_all", "traffic_volume"]

    if all(col in traffic_emission.columns for col in required_cols):
        X_hist = traffic_emission[
            ["hour", "temp", "rain_1h", "snow_1h", "clouds_all"]
        ]
        y_actual = traffic_emission["traffic_volume"]
        y_pred = traffic_model.predict(X_hist)

        avp_df = pd.DataFrame({
            "Actual": y_actual,
            "Predicted": y_pred
        })

        st.scatter_chart(avp_df)
    else:
        st.info("Required historical features not found for Actual vs Predicted plot.")

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

    # =========================
    # EMISSION CALCULATIONS
    # =========================
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
    # HOURLY CO₂ SAVINGS
    # =========================
    st.markdown("### ⏱ Hourly CO₂ Savings")

    hourly_saved = (
        traffic_emission
        .groupby("hour")["CO2_saved"]
        .mean()
    )

    st.line_chart(hourly_saved)

    # =========================
    # HOURLY CO₂ (HISTORICAL – FIXED)
    # =========================
    st.markdown("### 🕒 Hourly CO₂ Emission (Historical)")

    hourly_co2_df = (
        traffic_emission
        .groupby("hour")["CO2_before"]
        .mean()
        .reset_index()
    )

    hourly_co2_df.columns = ["Hour", "CO2"]

    st.line_chart(hourly_co2_df.set_index("Hour"))

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("Smart Traffic Management System with Emission Reduction")
