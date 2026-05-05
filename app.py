import streamlit as st
import requests

st.set_page_config(page_title="MLB Pitcher AI", layout="wide")

st.title("⚾ MLB Pitcher Vulnerability AI")

# ======================
# SAFE ESPN FETCH
# ======================

def get_games():

    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"

    try:
        data = requests.get(url).json()
    except:
        st.error("Error conectando con ESPN API")
        return []

    games = []

    for event in data.get("events", []):

        comp = event["competitions"][0]
        teams = comp["competitors"]

        home = next(t for t in teams if t["homeAway"]=="home")
        away = next(t for t in teams if t["homeAway"]=="away")

        def get_pitcher(team):
            try:
                return team["probables"][0]["athlete"]["displayName"]
            except:
                return "TBD"

        games.append({
            "game": f'{away["team"]["displayName"]} vs {home["team"]["displayName"]}',
            "home_pitcher": get_pitcher(home),
            "away_pitcher": get_pitcher(away)
        })

    return games


games = get_games()

if len(games) == 0:
    st.stop()

# ======================
# GAME SELECTOR
# ======================

game_names = [g["game"] for g in games]

selected_game = st.selectbox("Selecciona Juego", game_names)

game = next(g for g in games if g["game"] == selected_game)

st.subheader(selected_game)

# ======================
# INPUT PANEL
# ======================

def pitcher_panel(name):

    st.markdown(f"### {name}")

    col1,col2,col3 = st.columns(3)

    hr9 = col1.number_input("HR/9",0.0,3.0,1.2,key=name+"hr9")
    barrel = col1.number_input("Barrel %",0.0,20.0,9.0,key=name+"barrel")

    fb = col2.number_input("Fly Ball %",0.0,70.0,38.0,key=name+"fb")
    woba = col2.number_input("Split wOBA",0.200,0.500,0.330,key=name+"woba")

    iso = col3.number_input("Lineup ISO",0.050,0.400,0.170,key=name+"iso")
    park = col3.number_input("Ballpark HR Factor",0.5,2.0,1.05,key=name+"park")

    sharp = st.slider("Sharp Money Index",0,100,50,key=name+"sharp")

    return {
        "hr9":hr9,
        "barrel":barrel,
        "fb":fb,
        "woba":woba,
        "iso":iso,
        "park":park,
        "sharp":sharp
    }


home_data = pitcher_panel(game["home_pitcher"])
away_data = pitcher_panel(game["away_pitcher"])

# ======================
# MODEL ENGINE
# ======================

def risk_score(d):

    score = (
        d["hr9"]*25 +
        d["barrel"]*2 +
        d["fb"]*0.6 +
        (d["woba"]-0.300)*200 +
        d["iso"]*120 +
        d["park"]*15 +
        d["sharp"]*0.3
    )

    return round(score,1)


def classify(score):

    if score >= 95:
        return "🔥 Elite Target"
    elif score >= 75:
        return "🔴 Vulnerable"
    elif score >= 60:
        return "🟡 Neutral"
    else:
        return "🟢 Stable"


home_score = risk_score(home_data)
away_score = risk_score(away_data)

home_class = classify(home_score)
away_class = classify(away_score)

# ======================
# RESULTS
# ======================

st.divider()

c1,c2 = st.columns(2)

c1.metric(game["home_pitcher"], home_score)
c1.write(home_class)

c2.metric(game["away_pitcher"], away_score)
c2.write(away_class)

# ======================
# GAME ENVIRONMENT
# ======================

elite_count = sum([
    "Elite" in home_class,
    "Elite" in away_class
])

if elite_count == 2:
    env = "🔥 OFFENSIVE GAME"
elif elite_count == 1:
    env = "⚠️ TARGETABLE MATCHUP"
else:
    env = "🧊 LOW SCORING"

st.subheader("Game Environment")
st.write(env)

# ======================
# AUTO BET ENGINE
# ======================

st.subheader("⭐ Recommended Plays")

plays = []

if elite_count == 2:
    plays += [
        "✅ OVER LEAN",
        "✅ YRFI SIGNAL",
        "✅ Both Team Totals"
    ]

if "Elite" in home_class or "Elite" in away_class:
    plays += [
        "🎯 Fade Vulnerable Pitcher",
        "💥 HR Prop Spot",
        "⚾ Hits / Total Bases Props"
    ]

if home_data["sharp"] > 60 or away_data["sharp"] > 60:
    plays.append("💰 Sharp Money Confirmation")

if not plays:
    plays.append("No Edge Detected")

for p in plays:
    st.write(p)
