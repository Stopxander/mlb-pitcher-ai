import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MLB Pitcher AI", layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# ======================
# CONFIG
# ======================

TODAY = "2024-06-01"   # puedes cambiar fecha manualmente

SCOREBOARD_URL = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={TODAY}"

# ======================
# FUNCTIONS
# ======================

def get_games():

    data = requests.get(SCOREBOARD_URL).json()

    games = []

    if not data["dates"]:
        return []

    for g in data["dates"][0]["games"]:

        away = g["teams"]["away"]["team"]["name"]
        home = g["teams"]["home"]["team"]["name"]

        away_pitcher = g["teams"]["away"].get("probablePitcher", {})
        home_pitcher = g["teams"]["home"].get("probablePitcher", {})

        games.append({
            "label": f"{away} @ {home}",
            "away_team": away,
            "home_team": home,
            "away_pitcher": away_pitcher.get("fullName", "TBD"),
            "home_pitcher": home_pitcher.get("fullName", "TBD"),
        })

    return games


def calculate_scores(hr9, flyball, barrel, woba, iso, park, sharp):

    hr_score = (
        hr9 * 18 +
        flyball * 0.5 +
        barrel * 2 +
        park * 12 +
        iso * 80
    )

    hit_score = (
        woba * 250 +
        sharp * 0.4 +
        flyball * 0.3
    )

    return round(hr_score,1), round(hit_score,1)


def classify_pitcher(hr_score, hit_score):

    if hr_score >= 70 or hit_score >= 100:
        return "🔴 Pitcher Vulnerable"

    elif hr_score >= 55:
        return "🟡 Neutral Pitcher"

    else:
        return "🟢 Pitcher Stable"


# ======================
# LOAD GAMES
# ======================

games = get_games()

if not games:
    st.warning("Aún no hay pitchers confirmados.")
    st.stop()

game_choice = st.selectbox(
    "Selecciona Juego",
    games,
    format_func=lambda x: x["label"]
)

# ======================
# SELECT PITCHER
# ======================

pitcher_side = st.radio(
    "Selecciona Pitcher a Analizar",
    ["Local", "Visitante"]
)

if pitcher_side == "Local":
    pname = game_choice["home_pitcher"]
else:
    pname = game_choice["away_pitcher"]

st.subheader(f"Analizando: {pname}")

# ======================
# INPUT DATA
# ======================

col1, col2 = st.columns(2)

with col1:
    hr9 = st.number_input("HR/9", value=1.2)
    flyball = st.number_input("Fly Ball %", value=38.0)
    barrel = st.number_input("Barrel %", value=7.5)

with col2:
    woba = st.number_input("Split wOBA Allowed", value=0.320)
    iso = st.number_input("Lineup ISO vs pitcher hand", value=0.170)
    park = st.number_input("Ballpark HR Factor", value=1.05)

sharp = st.slider("Sharp Money Index (0-100)",0,100,50)

# ======================
# CALCULATE
# ======================

hr_score, hit_score = calculate_scores(
    hr9, flyball, barrel, woba, iso, park, sharp
)

status = classify_pitcher(hr_score, hit_score)

# ======================
# RESULTS
# ======================

st.markdown("---")

c1,c2,c3 = st.columns(3)

c1.metric("HR Risk Score", hr_score)
c2.metric("Hit Risk Score", hit_score)
c3.markdown(f"### {status}")
