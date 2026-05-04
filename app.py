import streamlit as st
import requests

st.title("⚾ MLB Pitcher AI")

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

data = requests.get(url).json()

if data["dates"]:

    games = data["dates"][0]["games"]

    valid_games = []

    for game in games:

        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        home_pitcher = game["teams"]["home"].get("probablePitcher")
        away_pitcher = game["teams"]["away"].get("probablePitcher")

        game_time = game["gameDate"]

        # SOLO juegos con pitchers confirmados
        if home_pitcher and away_pitcher:

            valid_games.append({
                "home": home,
                "away": away,
                "home_pitcher": home_pitcher["fullName"],
                "away_pitcher": away_pitcher["fullName"],
                "time": game_time
            })

    if valid_games:

        st.success(f"{len(valid_games)} juegos listos para análisis")

        for g in valid_games:

            st.markdown(f"""
            ### {g['away']} vs {g['home']}
            🧢 Visitante: **{g['away_pitcher']}**  
            🧢 Local: **{g['home_pitcher']}**  
            ⏰ {g['time']}
            """)

    else:
        st.warning("Aún no hay pitchers confirmados hoy.")

else:
    st.write("No hay juegos hoy.")
