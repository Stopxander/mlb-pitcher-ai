import streamlit as st
import requests

st.set_page_config(page_title="MLB Sharp Betting AI", layout="wide")

# ===============================
# ESPN API (LINEUPS + PITCHERS)
# ===============================

@st.cache_data(ttl=300)
def get_games():
    url = "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    data = requests.get(url).json()

    games = []

    for event in data["events"]:
        comp = event["competitions"][0]

        home = comp["competitors"][0]
        away = comp["competitors"][1]

        games.append({
            "matchup": f"{away['team']['displayName']} vs {home['team']['displayName']}",
            "home_pitcher": home.get("probables", [{}])[0].get("athlete", {}).get("displayName","TBD"),
            "away_pitcher": away.get("probables", [{}])[0].get("athlete", {}).get("displayName","TBD"),
        })

    return games


games = get_games()

st.title("⚾ MLB Sharp Betting AI")

if not games:
    st.warning("No games detected.")
    st.stop()

matchup = st.selectbox(
    "Select Game",
    [g["matchup"] for g in games]
)

game = next(g for g in games if g["matchup"] == matchup)

# ===============================
# LEAGUE BASELINES
# ===============================

LEAGUE = {
    "hr9": 1.10,
    "barrel": 8.5,
    "flyball": 36,
    "woba": .315,
    "iso": .165,
    "park": 1.00
}

def vulnerability(stats):

    score = 50

    score += (stats["hr9"] - LEAGUE["hr9"]) * 40
    score += (stats["barrel"] - LEAGUE["barrel"]) * 3
    score += (stats["flyball"] - LEAGUE["flyball"]) * 1.5
    score += (stats["woba"] - LEAGUE["woba"]) * 300
    score += (stats["lineup_iso"] - LEAGUE["iso"]) * 400
    score += (stats["park_factor"] - LEAGUE["park"]) * 60
    score += (stats["sharp_index"] - 50) * 0.6

    return round(score,1)

def label(score):

    if score >= 75:
        return "🔥 ELITE TARGET (Bet OVER / Batter Props)"
    elif score >= 60:
        return "⚠️ Attackable Pitcher"
    elif score >= 45:
        return "Neutral"
    else:
        return "🧊 Strong Pitcher (Lean UNDER)"

# ===============================
# PITCHER PANEL
# ===============================

def pitcher_card(name):

    st.subheader(name)

    hr9 = st.number_input("HR/9",0.0,3.0,1.1,0.05,key=name+"hr9")
    barrel = st.number_input("Barrel %",0.0,20.0,8.5,0.5,key=name+"barrel")
    flyball = st.number_input("Flyball %",20.0,60.0,36.0,1.0,key=name+"fb")
    woba = st.number_input("Split wOBA",0.250,0.450,0.315,0.005,key=name+"woba")

    lineup_iso = st.number_input("Lineup ISO",0.100,0.300,0.165,0.005,key=name+"iso")
    park_factor = st.number_input("Ballpark HR Factor",0.80,1.40,1.00,0.01,key=name+"park")

    sharp_index = st.slider(
        "Sharp Money Index",
        0,100,50,
        help="0 = Public | 100 = Sharp side",
        key=name+"sharp"
    )

    stats = {
        "hr9":hr9,
        "barrel":barrel,
        "flyball":flyball,
        "woba":woba,
        "lineup_iso":lineup_iso,
        "park_factor":park_factor,
        "sharp_index":sharp_index
    }

    score = vulnerability(stats)

    st.metric("Vulnerability Score",score)
    st.success(label(score))

    return score


# ===============================
# DISPLAY BOTH PITCHERS
# ===============================

col1,col2 = st.columns(2)

with col1:
    away_score = pitcher_card(game["away_pitcher"])

with col2:
    home_score = pitcher_card(game["home_pitcher"])

# ===============================
# AUTO BETTING RECOMMENDATION
# ===============================

st.divider()
st.header("🤖 AI Betting Recommendation")

if away_score >=75 and home_score >=75:
    st.error("🔥🔥 DOUBLE ELITE → OVER GAME / HR PROPS / NRFI NO")

elif away_score >=75:
    st.warning(f"🔥 Attack {game['away_pitcher']} → Team Total / Batter Props")

elif home_score >=75:
    st.warning(f"🔥 Attack {game['home_pitcher']} → Team Total / Batter Props")

elif away_score <45 and home_score <45:
    st.success("🧊 Pitching Duel → UNDER Lean")

else:
    st.info("⚖️ No strong betting edge detected")
