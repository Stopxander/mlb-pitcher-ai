import streamlit as st
import requests

st.set_page_config(page_title="MLB Pitcher AI ESPN", layout="wide")

st.title("⚾ MLB Pitcher AI — ESPN Feed")

# ======================
# GET ESPN GAMES
# ======================

def get_games():

    url="https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    data=requests.get(url).json()

    games=[]

    for event in data["events"]:

        comp=event["competitions"][0]
        teams=comp["competitors"]

        away=teams[1]
        home=teams[0]

        def get_pitcher(team):

            try:
                for athlete in team["probables"]:
                    return athlete["athlete"]["displayName"]
            except:
                return "TBD"

        games.append({
            "game":f'{away["team"]["displayName"]} @ {home["team"]["displayName"]}',
            "away_pitcher":get_pitcher(away),
            "home_pitcher":get_pitcher(home)
        })

    return games


# ======================
# SIMPLE DISPLAY
# ======================

games=get_games()

if not games:
    st.warning("No games today")
    st.stop()

for g in games:

    st.markdown("---")
    st.header(g["game"])

    col1,col2=st.columns(2)

    col1.subheader(f"Away Pitcher: {g['away_pitcher']}")
    col2.subheader(f"Home Pitcher: {g['home_pitcher']}")
