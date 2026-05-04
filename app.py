import streamlit as st
import requests

st.title("⚾ MLB Pitcher AI")

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

data = requests.get(url).json()

# Toggle para mostrar TBD
show_tbd = st.checkbox("Mostrar juegos sin pitcher confirmado (TBD)", value=True)

if data["dates"]:

    games = data["dates"][0]["games"]

    for game in games:

        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        home_pitcher = game["teams"]["home"].get("probablePitcher")
        away_pitcher = game["teams"]["away"].get("probablePitcher")

        game_time = game["gameDate"]

        home_name = home_pitcher["fullName"] if home_pitcher else "TBD"
        away_name = away_pitcher["fullName"] if away_pitcher else "TBD"

        # Si no queremos ver TBD
        if not show_tbd:
            if home_name == "TBD" or away_name == "TBD":
                continue

        # Status visual
        if home_name != "TBD" and away_name != "TBD":
            status = "✅ Listo para analizar"
        else:
            status = "⏳ Esperando pitchers"

        st.markdown(f"""
        ### {away} vs {home}
        🧢 Visitante: **{away_name}**  
        🧢 Local: **{home_name}**  
        ⏰ {game_time}  
        {status}
        """)

else:
    st.write("No hay juegos hoy.")
