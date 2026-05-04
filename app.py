import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="MLB Pitcher AI", layout="wide")

st.title("⚾ MLB Pitcher AI — WORKING VERSION")

TODAY=date.today().strftime("%Y-%m-%d")

# ======================
# GET GAMES
# ======================

def get_games():

    url=f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={TODAY}"
    data=requests.get(url).json()

    if not data["dates"]:
        return []

    games=[]

    for g in data["dates"][0]["games"]:

        gamePk=g["gamePk"]

        away=g["teams"]["away"]["team"]["name"]
        home=g["teams"]["home"]["team"]["name"]

        games.append({
            "game":f"{away} @ {home}",
            "gamePk":gamePk
        })

    return games


# ======================
# GET STARTING PITCHERS
# ======================

def get_starting_pitchers(gamePk):

    url=f"https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live"
    data=requests.get(url).json()

    try:
        box=data["liveData"]["boxscore"]["teams"]

        away_pitcher=None
        home_pitcher=None

        # AWAY
        for pid in box["away"]["pitchers"]:
            player=box["away"]["players"][f"ID{pid}"]
            if player["stats"]["pitching"]["gamesStarted"]==1:
                away_pitcher=player["person"]["fullName"]
                away_id=player["person"]["id"]
                break

        # HOME
        for pid in box["home"]["pitchers"]:
            player=box["home"]["players"][f"ID{pid}"]
            if player["stats"]["pitching"]["gamesStarted"]==1:
                home_pitcher=player["person"]["fullName"]
                home_id=player["person"]["id"]
                break

        return away_pitcher,away_id,home_pitcher,home_id

    except:
        return None,None,None,None


# ======================
# PITCHER STATS
# ======================

def pitcher_stats(pid):

    if not pid:
        return None

    url=f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=season&group=pitching"
    r=requests.get(url).json()

    try:
        s=r["stats"][0]["splits"][0]["stat"]

        return{
            "hr9":float(s.get("homeRunsPer9",1.2)),
            "whip":float(s.get("whip",1.30)),
            "era":float(s.get("era",4.00)),
            "avg":float(s.get("avg",.250))
        }

    except:
        return None


# ======================
# MODEL
# ======================

def vulnerability(stats):

    score=(
        stats["hr9"]*20+
        stats["whip"]*15+
        stats["era"]*5+
        stats["avg"]*400
    )

    return round(score,1)


def classify(score):

    if score>=90:
        return "🔥 TARGET"

    if score>=70:
        return "🔴 Vulnerable"

    return "🟢 Stable"


# ======================
# MAIN
# ======================

games=get_games()

if not games:
    st.warning("No games today")
    st.stop()

for g in games:

    st.markdown("---")
    st.header(g["game"])

    away_p,away_id,home_p,home_id=get_starting_pitchers(g["gamePk"])

    cols=st.columns(2)

    pitchers=[
        ("Away",away_p,away_id),
        ("Home",home_p,home_id)
    ]

    for col,p in zip(cols,pitchers):

        side,name,pid=p

        with col:

            if not name:
                st.write("Esperando abridor...")
                continue

            st.subheader(name)

            stats=pitcher_stats(pid)

            if not stats:
                st.warning("No stats")
                continue

            score=vulnerability(stats)
            status=classify(score)

            st.metric("Vulnerability",score)
            st.markdown(status)
            st.write(stats)
