import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MLB Pitcher AI", layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# ===============================
# ESPN SCOREBOARD API
# ===============================

def get_games():

    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

    data = requests.get(url).json()

    games = []

    for event in data["events"]:

        comp = event["competitions"][0]

        home = comp["competitors"][0]
        away = comp["competitors"][1]

        home_pitcher = home.get("probables", [{}])
        away_pitcher = away.get("probables", [{}])

        games.append({
            "game": f'{away["team"]["displayName"]} vs {home["team"]["displayName"]}',
            "home_team": home["team"]["displayName"],
            "away_team": away["team"]["displayName"],
            "home_pitcher": home_pitcher[0].get("athlete", {}).get("displayName","TBD"),
            "away_pitcher": away_pitcher[0].get("athlete", {}).get("displayName","TBD"),
        })

    return games


games = get_games()

game_names = [g["game"] for g in games]

selected_game = st.selectbox("Selecciona Juego", game_names)

game = next(g for g in games if g["game"] == selected_game)

st.subheader(selected_game)

# ===============================
# INPUTS
# ===============================

def pitcher_inputs(name):

    st.markdown(f"### {name}")

    col
