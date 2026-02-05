import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib as jb

st.set_page_config(
    page_title="Smart Traffic Management with Emission Reduction",
    layout="wide"
)

st.title("🚦 Smart Traffic Management System with Emission Reduction")
st.markdown("---")

traffic_emission = pd.read_csv(
    r"C:\Users\gaura\Downloads\city_day.csv\traffic_emission_merge.csv"
).dropna()

traffic_model = jb.load(
    r"C:\Users\gaura\Downloads\city_day.csv\hourly traffic.pkl"
)

feature_importance_model = jb.load(
    r"C:\Users\gaura\Downloads\city_day.csv\feature importance.pkl"
)

actual_vs_pred = jb.load(
    r"C:\Users\gaura\Downloads\city_day.csv\Actual vs predicted.pkl"
)

hourly_co2 = jb.load(
    r"C:\Users\gaura\Downloads\city_day.csv\hourly co2.pkl"
)

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🚦 Smart Traffic Management")

    hour = st.number_input("Hour (0–23)", 0, 23, 12)
    temp = st.number_input("Temperature (°C)", value=30.0)
    rain = st.number_input("Rain in last 1 hour (mm)", value=0.0)
    snow = st.number_input("Snow in last 1 hour (mm)", value=0.0)
    clouds = st.number_input("Cloud Coverage (%)", 0, 100, 50)

    if st.button("Predict Traffic Volume"):
        new_data = np.array([[hour, temp, rain, snow, clouds]])
        prediction = traffic_model.predict(new_data)
        st.success(f"🚗 Predicted Traffic Volume: {int(prediction[0])} per/hours")

    st.markdown("### 📊 Feature Importance")

    features = ["hour", "temp", "rain_1h", "snow_1h", "clouds_all"]
    importance = feature_importance_model.feature_importances_

    fig1, ax1 = plt.subplots()
    ax1.bar(features, importance)
    ax1.set_title("Feature Importance")
    ax1.set_ylabel("Importance Score")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    st.markdown("### 📈 Actual vs Predicted Traffic")

    y_test, y_pred = None, None

    try:
        if isinstance(actual_vs_pred, pd.DataFrame):
            y_test = actual_vs_pred.iloc[:, 0].values
            y_pred = actual_vs_pred.iloc[:, 1].values
        else:
            arr = np.array(actual_vs_pred)
            y_test = arr[:, 0]
            y_pred = arr[:, 1]
    except Exception:
        st.warning("Could not auto-parse Actual vs Predicted data")

    if y_test is not None and y_pred is not None:
        fig2, ax2 = plt.subplots()
        ax2.scatter(y_test, y_pred, alpha=0.6)
        ax2.set_xlabel("Actual Traffic Volume")
        ax2.set_ylabel("Predicted Traffic Volume")
        ax2.set_title("Actual vs Predicted Traffic")
        st.pyplot(fig2)

with right_col:
    st.subheader("🌱 Emission Reduction")

    emission_factor = st.number_input(
        "Emission Factor (kg CO₂ / vehicle / hour)",
        min_value=0.05,
        max_value=2.0,
        value=0.25,
        step=0.01
    )

    reduction_rate = st.slider(
        "Traffic Optimization Reduction (%)",
        5, 50, 20
    ) / 100

    traffic_emission["CO2_before"] = traffic_emission["traffic_volume"] * emission_factor
    traffic_emission["CO2_after"] = traffic_emission["CO2_before"] * (1 - reduction_rate)
    traffic_emission["CO2_saved"] = traffic_emission["CO2_before"] - traffic_emission["CO2_after"]

    st.markdown("### 📊 Emission Summary")

    st.metric("Total CO₂ Before (kg)", f"{traffic_emission['CO2_before'].sum():,.0f}")
    st.metric("Total CO₂ After (kg)", f"{traffic_emission['CO2_after'].sum():,.0f}")
    st.metric("Total CO₂ Saved (kg)", f"{traffic_emission['CO2_saved'].sum():,.0f}")

    fig3, ax3 = plt.subplots()
    ax3.bar(["Before", "After"], [
        traffic_emission["CO2_before"].mean(),
        traffic_emission["CO2_after"].mean()
    ])
    ax3.set_title("Average CO₂ Emission Reduction")
    ax3.set_ylabel("CO₂ (kg)")
    st.pyplot(fig3)

    hourly_saved = traffic_emission.groupby("hour")["CO2_saved"].mean()

    fig4, ax4 = plt.subplots()
    ax4.plot(hourly_saved.index, hourly_saved.values, marker="o")
    ax4.set_xlabel("Hour")
    ax4.set_ylabel("CO₂ Saved (kg/hour)")
    ax4.set_title("Hourly CO₂ Emission Savings")
    st.pyplot(fig4)

    st.markdown("### 🕒 Hourly CO₂ Emission (Historical)")

    hc = np.array(hourly_co2)
    if hc.ndim == 2:
        fig5, ax5 = plt.subplots()
        ax5.plot(hc[:, 0], hc[:, 1], marker="o")
        ax5.set_xlabel("Hour")
        ax5.set_ylabel("CO₂ (kg)")
        ax5.set_title("Hourly CO₂ Emission")
        st.pyplot(fig5)

st.markdown("---")
st.caption("Smart Traffic Management System with Emission Reduction")
