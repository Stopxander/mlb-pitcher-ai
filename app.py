import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# -----------------------------
# MODELO
# -----------------------------

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


# -----------------------------
# OBTENER JUEGOS MLB
# -----------------------------

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"
data = requests.get(url).json()

if "pitcher_data" not in st.session_state:
    st.session_state.pitcher_data = {}

if data["dates"]:

    games = data["dates"][0]["games"]

    game_map = {}

    for g in games:
        away = g["teams"]["away"]["team"]["name"]
        home = g["teams"]["home"]["team"]["name"]

        away_pitcher = g["teams"]["away"].get("probablePitcher")
        home_pitcher = g["teams"]["home"].get("probablePitcher")

        game_name = f"{away} vs {home}"

        game_map[game_name] = {
            "away_pitcher": away_pitcher["fullName"] if away_pitcher else "TBD",
            "home_pitcher": home_pitcher["fullName"] if home_pitcher else "TBD"
        }

    selected_game = st.selectbox("Selecciona juego", list(game_map.keys()))

    pitchers = [
        f"Visitante — {game_map[selected_game]['away_pitcher']}",
        f"Local — {game_map[selected_game]['home_pitcher']}"
    ]

    selected_pitcher = st.selectbox("Selecciona Pitcher", pitchers)

    key = selected_game + selected_pitcher

    if key not in st.session_state.pitcher_data:
        st.session_state.pitcher_data[key] = {
            "hr9":1.2,
            "barrel":8.0,
            "woba":0.320,
            "iso":0.170,
            "park":1.05,
            "sharp":50
        }

    pdata = st.session_state.pitcher_data[key]

    st.subheader(f"📊 Analizando: {selected_pitcher}")

    col1, col2, col3 = st.columns(3)

    pdata["hr9"] = col1.number_input("HR/9", value=pdata["hr9"], key=key+"hr9")
    pdata["barrel"] = col2.number_input("Barrel %", value=pdata["barrel"], key=key+"barrel")
    pdata["woba"] = col3.number_input("Split wOBA Allowed", value=pdata["woba"], key=key+"woba")

    pdata["iso"] = col1.number_input("Lineup ISO vs Hand", value=pdata["iso"], key=key+"iso")
    pdata["park"] = col2.number_input("Ballpark HR Factor", value=pdata["park"], key=key+"park")
    pdata["sharp"] = col3.slider("Sharp Money Index",0,100,pdata["sharp"], key=key+"sharp")

    hr_score, hit_score, label = calculate_scores(
        pdata["hr9"],
        pdata["barrel"],
        pdata["woba"],
        pdata["iso"],
        pdata["park"],
        pdata["sharp"]
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
