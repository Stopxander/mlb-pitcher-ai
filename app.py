import streamlit as st
import pandas as pd
import requests

st.title("⚾ MLB Pitcher AI — Daily Board")

@st.cache_data(ttl=3600)
def get_games():
url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=probablePitcher"
    data = requests.get(url).json()

    games = []

    for date in data["dates"]:
        for game in date["games"]:
            home = game["teams"]["home"]["team"]["name"]
            away = game["teams"]["away"]["team"]["name"]

            try:
                home_pitcher = game["teams"]["home"]["probablePitcher"]["fullName"]
            except:
                home_pitcher = "TBD"

            try:
                away_pitcher = game["teams"]["away"]["probablePitcher"]["fullName"]
            except:
                away_pitcher = "TBD"

            games.append({
                "Away Team": away,
                "Home Team": home,
                "Away Pitcher": away_pitcher,
                "Home Pitcher": home_pitcher
            })

    return pd.DataFrame(games)

df = get_games()

st.subheader("🔥 Today's MLB Games")
st.dataframe(df, use_container_width=True)

st.success("Automatic MLB data loaded.")
