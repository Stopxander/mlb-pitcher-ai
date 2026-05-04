import streamlit as st
import requests

st.set_page_config(page_title="MLB Pitcher Vulnerability AI", layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# ======================
# ESPN GAMES + PITCHERS
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
                p=team["probables"][0]
                return p["athlete"]["displayName"]
            except:
                return None

        games.append({
            "game":f'{away["team"]["displayName"]} @ {home["team"]["displayName"]}',
            "away_pitcher":get_pitcher(away),
            "home_pitcher":get_pitcher(home)
        })

    return games


# ======================
# FIND PLAYER ID (MLB)
# ======================

def get_player_id(name):

    if not name:
        return None

    url=f"https://statsapi.mlb.com/api/v1/people/search?names={name}"
    r=requests.get(url).json()

    try:
        return r["people"][0]["id"]
    except:
        return None


# ======================
# GET PITCHER STATS
# ======================

def pitcher_stats(pid):

    if not pid:
        return None

    url=f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=season&group=pitching"
    r=requests.get(url).json()

    try:
        s=r["stats"][0]["splits"][0]["stat"]

        return {
            "hr9":float(s.get("homeRunsPer9",1.2)),
            "whip":float(s.get("whip",1.30)),
            "era":float(s.get("era",4.00)),
            "avg":float(s.get("avg",.250))
        }
    except:
        return None


# ======================
# VULNERABILITY MODEL
# ======================

def vulnerability(stats):

    score=(
        stats["hr9"]*22 +
        stats["whip"]*18 +
        stats["era"]*6 +
        stats["avg"]*400
    )

    return round(score,1)


def classify(score):

    if score>=95:
        return "🔥 ELITE TARGET"

    if score>=75:
        return "🔴 Pitcher Vulnerable"

    if score>=60:
        return "🟡 Neutral"

    return "🟢 Stable"


# ======================
# DISPLAY
# ======================

games=get_games()

if not games:
    st.warning("No games found")
    st.stop()

for g in games:

    st.markdown("---")
    st.header(g["game"])

    cols=st.columns(2)

    pitchers=[
        ("Away",g["away_pitcher"]),
        ("Home",g["home_pitcher"])
    ]

    for col,p in zip(cols,pitchers):

        side,name=p

        with col:

            if not name:
                st.write("TBD")
                continue

            st.subheader(name)

            pid=get_player_id(name)
            stats=pitcher_stats(pid)

            if not stats:
                st.warning("Stats unavailable")
                continue

            score=vulnerability(stats)
            status=classify(score)

            st.metric("Vulnerability Score",score)
            st.markdown(f"### {status}")

            st.write(stats)
