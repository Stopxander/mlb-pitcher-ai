import streamlit as st
import requests

st.title("⚾ MLB Pitcher AI")

st.write("Obteniendo juegos MLB del día...")

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"

response = requests.get(url)
data = response.json()

# Mostrar juegos
if data["dates"]:
    games = data["dates"][0]["games"]

    for game in games:
        home = game["teams"]["home"]["team"]["name"]
        away = game["teams"]["away"]["team"]["name"]

        home_pitcher = game["teams"]["home"].get("probablePitcher", {}).get("fullName", "TBD")
        away_pitcher = game["teams"]["away"].get("probablePitcher", {}).get("fullName", "TBD")

        st.write(f"""
        ### {away} vs {home}
        🧢 Pitcher visitante: {away_pitcher}  
        🧢 Pitcher local: {home_pitcher}
        """)

else:
    st.write("No hay juegos hoy.")
