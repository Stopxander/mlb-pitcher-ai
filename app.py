import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# -------------------------
# FUNCION MODELO
# -------------------------

def calculate_scores(hr9, barrel, woba, iso, park, sharp):

    hr_risk = (
        hr9 * 20 +
        barrel * 1.5 +
        woba * 100 +
        iso * 120 +
        park * 15 +
        sharp * 0.3
    )

    hit_risk = (
        woba * 150 +
        iso * 100 +
        barrel * 1.2 +
        sharp * 0.4
    )

    if hr_risk > 70:
        label = "🔥 Pitcher Vulnerable"
    elif hr_risk > 55:
        label = "⚠️ Riesgo Medio"
    else:
        label = "✅ Pitcher Estable"

    return round(hr_risk,2), round(hit_risk,2), label


# -------------------------
# OBTENER JUEGOS MLB
# -------------------------

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

data = requests.get(url).json()

if data["dates"]:

    games = data["dates"][0]["games"]

    game_list = []

    for g in games:
        away = g["teams"]["away"]["team"]["name"]
        home = g["teams"]["home"]["team"]["name"]

        game_list.append(f"{away} vs {home}")

    selected_game = st.selectbox("Selecciona juego", game_list)

    st.divider()

    st.subheader("📊 Datos del Pitcher")

    col1, col2, col3 = st.columns(3)

    hr9 = col1.number_input("HR/9", value=1.2)
    barrel = col2.number_input("Barrel %", value=8.0)
    woba = col3.number_input("Split wOBA Allowed", value=0.320)

    iso = col1.number_input("Lineup ISO vs Hand", value=0.170)
    park = col2.number_input("Ballpark HR Factor", value=1.05)
    sharp = col3.slider("Sharp Money Index",0,100,50)

    hr_score, hit_score, label = calculate_scores(
        hr9, barrel, woba, iso, park, sharp
    )

    st.divider()

    st.metric("HR Risk Score", hr_score)
    st.metric("Hit Risk Score", hit_score)

    if "Vulnerable" in label:
        st.error(label)
    elif "Medio" in label:
        st.warning(label)
    else:
        st.success(label)

else:
    st.write("No hay juegos hoy.")
