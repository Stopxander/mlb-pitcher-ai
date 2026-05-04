
import streamlit as st
import pandas as pd

st.title("MLB Pitcher Vulnerability Model (MVP)")

st.markdown("Introduce las métricas del pitcher y del lineup para calcular riesgo de HR y Hits.")

# Pitcher inputs
st.header("Pitcher Metrics")
hr9 = st.number_input("HR/9", value=1.2)
flyball = st.number_input("Fly Ball %", value=35.0)
barrel = st.number_input("Barrel %", value=8.0)
split_woba = st.number_input("Split wOBA Allowed", value=0.320)

# Lineup inputs
st.header("Opponent Lineup Metrics")
lineup_iso = st.number_input("Lineup ISO vs Pitcher Hand", value=0.170)

# Park factor
park_factor = st.number_input("Ballpark HR Factor", value=1.00)

# Market input
sharp_money = st.number_input("Sharp Money Index (0-100)", value=50.0)

# Model calculation
hr_risk = (
    0.25 * hr9 +
    0.20 * flyball/100 +
    0.15 * barrel/100 +
    0.15 * split_woba +
    0.10 * lineup_iso +
    0.10 * park_factor +
    0.05 * sharp_money/100
)

hit_risk = hr_risk * 1.35

st.header("Model Output")
st.metric("HR Risk Score", round(hr_risk*100,2))
st.metric("Hit Risk Score", round(hit_risk*100,2))

if hr_risk > 0.9:
    st.error("🔥 Pitcher ALTAMENTE ATACABLE")
elif hr_risk > 0.6:
    st.warning("⚠️ Pitcher Vulnerable")
else:
    st.success("✅ Pitcher estable")

