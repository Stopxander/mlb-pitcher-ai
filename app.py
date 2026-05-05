import streamlit as st

st.set_page_config(page_title="MLB Pitcher Vulnerability", layout="centered")

st.title("⚾ MLB Pitcher Vulnerability Model")

st.markdown("Introduce los datos del pitcher")

# INPUTS
hr9 = st.number_input("HR/9", value=1.10)
barrel = st.number_input("Barrel %", value=8.5)
flyball = st.number_input("Flyball %", value=36.0)
woba = st.number_input("Split wOBA", value=0.320)
iso = st.number_input("Lineup ISO", value=0.170)
park = st.number_input("Ballpark HR Factor", value=1.00)

sharp = st.slider(
    "Sharp Money Index",
    0,
    100,
    50,
    help="70+ dinero profesional contra el pitcher"
)

# MODELO
score = (
    hr9 * 15 +
    barrel * 2 +
    flyball * 0.6 +
    woba * 100 +
    iso * 120 +
    park * 25 +
    sharp * 0.4
)

score = min(score / 10, 100)

st.subheader(f"Vulnerability Score: {round(score,1)}")

# CLASIFICACION
if score >= 75:
    st.error("🔥 ELITE TARGET → Over / Team Total / HR Props")
elif score >= 60:
    st.warning("⚠️ Pitcher Vulnerable")
elif score >= 45:
    st.info("🟡 Neutral Spot")
else:
    st.success("✅ Pitcher Safe")
