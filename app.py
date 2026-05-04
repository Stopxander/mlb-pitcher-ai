import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="MLB Sharp Syndicate AI", layout="wide")

st.title("⚾ MLB SHARP SYNDICATE AI")

TODAY = date.today().strftime("%Y-%m-%d")

SCHEDULE_URL = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={TODAY}"

# =============================
# GET TODAY GAMES
# =============================
def get_games():

    data = requests.get(SCHEDULE_URL).json()

    if not data["dates"]:
        return []

    games = []

    for g in data["dates"][0]["games"]:

        away = g["teams"]["away"]["team"]["name"]
        home = g["teams"]["home"]["team"]["name"]

        away_pitcher = g["teams"]["away"].get("probablePitcher", {})
        home_pitcher = g["teams"]["home"].get("probablePitcher", {})

        games.append({
            "game": f"{away} @ {home}",
            "away_pitcher": away_pitcher.get("fullName"),
            "away_id": away_pitcher.get("id"),
            "home_pitcher": home_pitcher.get("fullName"),
            "home_id": home_pitcher.get("id")
        })

    return games


# =============================
# PITCHER STATS
# =============================
def get_pitcher_stats(pid):

    if not pid:
        return None

    url = f"https://statsapi.mlb.com/api/v1/people/{pid}/stats?stats=season&group=pitching"

    r = requests.get(url).json()

    try:
        s = r["stats"][0]["splits"][0]["stat"]

        return {
            "hr9": float(s.get("homeRunsPer9",1.2)),
            "whip": float(s.get("whip",1.30)),
            "era": float(s.get("era",4.00)),
            "avg": float(s.get("avg",.250))
        }
    except:
        return None


# =============================
# SHARP MONEY INPUT
# =============================
def sharp_index():

    st.sidebar.header("💰 Sharp Money Input")

    tickets = st.sidebar.slider("% Tickets",0,100,50)
    money = st.sidebar.slider("% Money",0,100,50)

    edge = money - tickets

    return edge


# =============================
# VULNERABILITY MODEL
# =============================
def vulnerability(stats):

    score = (
        stats["hr9"]*20 +
        stats["whip"]*15 +
        stats["era"]*5 +
        stats["avg"]*400
    )

    return round(score,1)


def classify(score):

    if score >= 95:
        return "🔥 ELITE TARGET"

    elif score >= 75:
        return "🔴 Vulnerable"

    elif score >= 60:
        return "🟡 Neutral"

    else:
        return "🟢 Stable"


# =============================
# BET SIGNAL ENGINE
# =============================
def bet_signal(score, sharp):

    if score > 90 and sharp > 15:
        return "💰 SYNDICATE PLAY"

    if score > 80 and sharp > 5:
        return "🎯 VALUE BET"

    if sharp > 20:
        return "📈 SHARP MONEY ONLY"

    return "No Edge"


# =============================
# MAIN APP
# =============================

sharp_edge = sharp_index()

games = get_games()

if not games:
    st.warning("No games today")
    st.stop()

top_spots = []

for g in games:

    st.markdown("---")
    st.header(g["game"])

    cols = st.columns(2)

    pitchers = [
        ("Away", g["away_pitcher"], g["away_id"]),
        ("Home", g["home_pitcher"], g["home_id"])
    ]

    for col, p in zip(cols, pitchers):

        side, name, pid = p

        with col:

            if not name:
                st.write(f"{side}: TBD")
                continue

            st.subheader(name)

            stats = get_pitcher_stats(pid)

            if not stats:
                st.warning("Stats unavailable")
                continue

            score = vulnerability(stats)
            status = classify(score)
            signal = bet_signal(score, sharp_edge)

            st.metric("Vulnerability", score)
            st.markdown(f"### {status}")
            st.write(stats)
            st.success(signal)

            if signal != "No Edge":
                top_spots.append((g["game"], name, signal))


# =============================
# TOP BET SPOTS
# =============================
st.markdown("---")
st.header("⭐ TOP BET SPOTS TODAY")

if not top_spots:
    st.write("No strong edges detected")

for t in top_spots:
    st.write(f"{t[0]} — {t[1]} → {t[2]}")
