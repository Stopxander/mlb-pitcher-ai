import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("⚾ MLB EDGE FINDER AI — Sharp Edition")

# ------------------------------------------------
# EDGE MODEL
# ------------------------------------------------

def calculate_edge(hr9, barrel, woba, iso, park, sharp_index):

    hr_risk = hr9*20 + barrel*1.5 + woba*100 + iso*120 + park*15
    hit_risk = woba*150 + iso*100 + barrel*1.2

    edge_score = hr_risk + sharp_index*0.6

    if edge_score > 110:
        label = "🔥 ELITE BET"
    elif edge_score > 90:
        label = "🔥 TOP EDGE"
    elif edge_score > 70:
        label = "💰 EDGE POSITIVO"
    else:
        label = "❌ SIN VALOR"

    return round(hr_risk,2), round(hit_risk,2), round(edge_score,2), label


# ------------------------------------------------
# SHARP MONEY CALCULATOR
# ------------------------------------------------

def sharp_money_index(tickets, money):

    diff = money - tickets

    if diff >= 25:
        signal = "🔥 SHARP MONEY FUERTE"
        index = 90
    elif diff >= 15:
        signal = "💰 SHARP MONEY"
        index = 75
    elif diff >= 5:
        signal = "⚠️ LEAN SHARP"
        index = 60
    else:
        signal = "📊 PUBLIC MONEY"
        index = 40

    return index, signal


# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

if "pitcher_data" not in st.session_state:
    st.session_state.pitcher_data = {}

# ------------------------------------------------
# MLB GAMES
# ------------------------------------------------

url = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"
data = requests.get(url).json()

if data["dates"]:

    games = data["dates"][0]["games"]

    game_map = {}

    for g in games:
        away = g["teams"]["away"]["team"]["name"]
        home = g["teams"]["home"]["team"]["name"]

        away_pitcher = g["teams"]["away"].get("probablePitcher")
        home_pitcher = g["teams"]["home"].get("probablePitcher")

        game_name = f"{away} vs {home}"

        game_map[game_name] = {
            "away_pitcher": away_pitcher["fullName"] if away_pitcher else "TBD",
            "home_pitcher": home_pitcher["fullName"] if home_pitcher else "TBD"
        }

    selected_game = st.selectbox("Juego", list(game_map.keys()))

    pitchers = [
        f"Visitante — {game_map[selected_game]['away_pitcher']}",
        f"Local — {game_map[selected_game]['home_pitcher']}"
    ]

    selected_pitcher = st.selectbox("Pitcher Analizado", pitchers)

    key = selected_game + selected_pitcher

    if key not in st.session_state.pitcher_data:
        st.session_state.pitcher_data[key] = {}

    pdata = st.session_state.pitcher_data[key]

    pdata.setdefault("hand","R")
    pdata.setdefault("hr9",1.2)
    pdata.setdefault("barrel",8.0)
    pdata.setdefault("woba",0.320)
    pdata.setdefault("iso",0.170)
    pdata.setdefault("park",1.05)

    st.subheader(f"📊 Analizando: {selected_pitcher}")

    col1,col2,col3 = st.columns(3)

    pdata["hand"] = col1.selectbox(
        "Mano Pitcher",
        ["R","L"],
        index=0 if pdata["hand"]=="R" else 1,
        key=key+"hand"
    )

    pdata["hr9"] = col1.number_input("HR/9",value=float(pdata["hr9"]),key=key+"hr9")
    pdata["barrel"] = col2.number_input("Barrel %",value=float(pdata["barrel"]),key=key+"barrel")
    pdata["woba"] = col3.number_input("Split wOBA",value=float(pdata["woba"]),key=key+"woba")

    pdata["iso"] = col1.number_input(
        f"Lineup ISO vs {'RHP' if pdata['hand']=='R' else 'LHP'}",
        value=float(pdata["iso"]),
        key=key+"iso"
    )

    pdata["park"] = col2.number_input("Ballpark HR Factor",value=float(pdata["park"]),key=key+"park")

    st.divider()
    st.subheader("💰 Sharp Money (Action Network / ZCode)")

    tickets = st.slider("% Tickets",0,100,50,key=key+"tickets")
    money = st.slider("% Money",0,100,50,key=key+"money")

    sharp_index, sharp_signal = sharp_money_index(tickets,money)

    st.info(sharp_signal)

    # EDGE CALCULATION
    hr_score, hit_score, edge_score, label = calculate_edge(
        pdata["hr9"],
        pdata["barrel"],
        pdata["woba"],
        pdata["iso"],
        pdata["park"],
        sharp_index
    )

    st.divider()

    c1,c2,c3 = st.columns(3)

    c1.metric("HR Risk",hr_score)
    c2.metric("Hit Risk",hit_score)
    c3.metric("EDGE SCORE",edge_score)

    if "ELITE" in label:
        st.error(label)
    elif "TOP" in label:
        st.success(label)
    else:
        st.warning(label)

else:
    st.write("No hay juegos hoy.")
