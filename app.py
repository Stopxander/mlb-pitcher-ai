import streamlit as st
import requests

st.set_page_config(page_title="MLB Pitcher AI PRO", layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI PRO")

TODAY = "2024-06-01"

SCHEDULE_URL = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={TODAY}"

# ======================
# GET GAMES
# ======================

def get_games():

    data = requests.get(SCHEDULE_URL).json()

    games = []

    if not data["dates"]:
        return []

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

# ======================
# GET PITCHER STATS
# ======================

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

# ======================
# SCORING ENGINE
# ======================

def vulnerability_score(stats):

    score = (
        stats["hr9"] * 20 +
        stats["whip"] * 15 +
        stats["era"] * 5 +
        stats["avg"] * 400
    )

    return round(score,1)

def classify(score):

    if score >= 95:
        return "🔥 ELITE TARGET"

    elif score >= 75:
        return "🔴 Pitcher Vulnerable"

    elif score >= 60:
        return "🟡 Neutral"

    else:
        return "🟢 Stable"

# ======================
# MAIN
# ======================

games = get_games()

if not games:
    st.warning("No games today")
    st.stop()

for g in games:

    st.markdown("---")
    st.header(g["game"])

    cols = st.columns(2)

    pitchers = [
        ("Visitante", g["away_pitcher"], g["away_id"]),
        ("Local", g["home_pitcher"], g["home_id"])
    ]

    for col, p in zip(cols, pitchers):

        side, name, pid = p

        with col:

            if not name:
                st.write(f"{side}: TBD")
                continue

            st.subheader(f"{side}: {name}")

            stats = get_pitcher_stats(pid)

            if not stats:
                st.warning("Stats no disponibles")
                continue

            score = vulnerability_score(stats)
            status = classify(score)

            st.metric("Vulnerability Score", score)
            st.markdown(f"### {status}")

            st.write(stats)

            if score >= 95:
                st.success("💰 BET TARGET DETECTED")
