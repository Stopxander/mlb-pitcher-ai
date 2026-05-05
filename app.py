import streamlit as st
import requests
from datetime import date

st.set_page_config(layout="wide")

# ===============================
# GET MLB GAMES (ESPN API)
# ===============================
@st.cache_data(ttl=600)
def get_games():

    today = date.today().strftime("%Y%m%d")

    url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"

    data = requests.get(url).json()

    games = []

    for event in data["events"]:

        comp = event["competitions"][0]

        home = comp["competitors"][0]["team"]["displayName"]
        away = comp["competitors"][1]["team"]["displayName"]

        home_pitcher = comp["competitors"][0].get(
            "probables", [{}]
        )[0].get("athlete", {}).get("displayName", "TBD")

        away_pitcher = comp["competitors"][1].get(
            "probables", [{}]
        )[0].get("athlete", {}).get("displayName", "TBD")

        games.append({
            "game": f"{away} vs {home}",
            "home_pitcher": home_pitcher,
            "away_pitcher": away_pitcher
        })

    return games


# ===============================
# FAKE SMART STAT GENERATOR
# (temporary until live stat API)
# ===============================
def generate_pitcher_stats(name):

    seed = sum(ord(c) for c in name)

    return {
        "hr9": round(0.8 + (seed % 80)/100,2),
        "barrel": round(5 + (seed % 10),1),
        "flyball": round(30 + (seed % 20),1),
        "woba": round(.280 + (seed % 60)/1000,3),
        "lineup_iso": round(.140 + (seed % 60)/1000,3),
        "park_factor": round(0.9 + (seed % 30)/100,2),
        "sharp_index": 40 + (seed % 60)
    }


# ===============================
# VULNERABILITY MODEL
# ===============================
def vulnerability(stats):

    score = (
        stats["hr9"]*25 +
        stats["barrel"]*2 +
        stats["flyball"]*1.2 +
        stats["woba"]*150 +
        stats["lineup_iso"]*200 +
        stats["park_factor"]*20 +
        stats["sharp_index"]*0.4
    )

    return round(score,1)


def label(score):

    if score > 140:
        return "🔥 ELITE TARGET (Attack Over / Batter Props)"
    elif score > 120:
        return "⚠️ Vulnerable"
    elif score > 100:
        return "Neutral"
    else:
        return "🧊 Stable Pitcher"


# ===============================
# UI
# ===============================
st.title("⚾ MLB Pitcher Vulnerability AI")

games = get_games()

if not games:
    st.warning("No games today")
    st.stop()

selected = st.selectbox(
    "Select Game",
    [g["game"] for g in games]
)

game = next(g for g in games if g["game"] == selected)

col1, col2 = st.columns(2)

for col, pname, side in [
    (col1, game["away_pitcher"], "Away"),
    (col2, game["home_pitcher"], "Home"),
]:

    with col:

        st.subheader(f"{side} Pitcher")
        st.markdown(f"### {pname}")

        if pname == "TBD":
            st.warning("Waiting for confirmed pitcher")
            continue

        stats = generate_pitcher_stats(pname)

        score = vulnerability(stats)

        st.metric("HR/9", stats["hr9"])
        st.metric("Barrel %", stats["barrel"])
        st.metric("Flyball %", stats["flyball"])
        st.metric("Split wOBA", stats["woba"])
        st.metric("Lineup ISO", stats["lineup_iso"])
        st.metric("Ballpark Factor", stats["park_factor"])
        st.metric("Sharp Money Index", stats["sharp_index"])

        st.success(label(score))
        st.metric("Vulnerability Score", score)
