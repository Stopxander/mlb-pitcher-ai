import streamlit as st
import requests

st.title("⚾ MLB Pitcher AI")

schedule_url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

data = requests.get(schedule_url).json()

def get_live_pitcher(gamePk, side):
    try:
        url = f"https://statsapi.mlb.com/api/v1/game/{gamePk}/boxscore"
        box = requests.get(url).json()

        pitchers = box["teams"][side]["pitchers"]

        if pitchers:
            pitcher_id = pitchers[0]
            return box["teams"][side]["players"][f"ID{pitcher_id}"]["person"]["fullName"]

    except:
        pass

    return "TBD"


if data["dates"]:

    games = data["dates"][0]["games"]

    for game in games:

        gamePk = game["gamePk"]

        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        status = game["status"]["detailedState"]

        home_pitcher = game["teams"]["home"].get("probablePitcher")
        away_pitcher = game["teams"]["away"].get("probablePitcher")

        # Si el juego ya empezó → buscar pitcher real
        if status in ["In Progress", "Live", "Final"]:

            home_name = get_live_pitcher(gamePk, "home")
            away_name = get_live_pitcher(gamePk, "away")

        else:
            home_name = home_pitcher["fullName"] if home_pitcher else "TBD"
            away_name = away_pitcher["fullName"] if away_pitcher else "TBD"

        st.markdown(f"""
        ### {away} vs {home}
        🧢 Visitante: **{away_name}**
        🧢 Local: **{home_name}**
        📡 Estado: {status}
        """)

else:
    st.write("No hay juegos hoy.")
