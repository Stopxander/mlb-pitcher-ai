import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

st.title("⚾ MLB EDGE FINDER AI — Daily Picks")

# ------------------------------------------------
# MODELOS
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

    return hr_risk, hit_risk, edge_score, label


def sharp_money_index(tickets, money):

    diff = money - tickets

    if diff >= 25:
        return 90, "🔥 SHARP MONEY FUERTE"
    elif diff >= 15:
        return 75, "💰 SHARP MONEY"
    elif diff >= 5:
        return 60, "⚠️ LEAN SHARP"
    else:
        return 40, "📊 PUBLIC MONEY"


# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

if "pitcher_data" not in st.session_state:
    st.session_state.pitcher_data = {}

if "daily_picks" not in st.session_state:
    st.session_state.daily_picks = []

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

    selected_pitcher = st.selectbox("Pitcher", pitchers)

    key = selected_game + selected_pitcher

    if key not in st.session_state.pitcher_data:
        st.session_state.pitcher_data[key] = {
            "hand":"R",
            "hr9":1.2,
            "barrel":8.0,
            "woba":0.320,
            "iso":0.170,
            "park":1.05
        }

    pdata = st.session_state.pitcher_data[key]

    st.subheader(f"📊 Analizando: {selected_pitcher}")

    col1,col2,col3 = st.columns(3)

    pdata["hand"] = col1.selectbox("Mano",["R","L"],key=key+"hand")
    pdata["hr9"] = col1.number_input("HR/9",value=pdata["hr9"],key=key+"hr9")

    pdata["barrel"] = col2.number_input("Barrel %",value=pdata["barrel"],key=key+"barrel")
    pdata["woba"] = col3.number_input("Split wOBA",value=pdata["woba"],key=key+"woba")

    pdata["iso"] = col1.number_input(
        f"ISO vs {'RHP' if pdata['hand']=='R' else 'LHP'}",
        value=pdata["iso"],
        key=key+"iso"
    )

    pdata["park"] = col2.number_input("Ballpark HR Factor",value=pdata["park"],key=key+"park")

    st.divider()
    st.subheader("💰 Sharp Money")

    tickets = st.slider("% Tickets",0,100,50,key=key+"tickets")
    money = st.slider("% Money",0,100,50,key=key+"money")

    sharp_index, sharp_signal = sharp_money_index(tickets,money)

    st.info(sharp_signal)

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
    c1.metric("HR Risk",round(hr_score,2))
    c2.metric("Hit Risk",round(hit_score,2))
    c3.metric("EDGE SCORE",round(edge_score,2))

    if st.button("✅ Agregar a Daily Picks"):

        st.session_state.daily_picks.append({
            "Juego":selected_game,
            "Pitcher":selected_pitcher,
            "Edge":round(edge_score,2),
            "Señal":label
        })

        st.success("Pick agregado")

# ------------------------------------------------
# DAILY PICKS AI
# ------------------------------------------------

st.divider()
st.header("🤖 Daily Picks AI")

if st.session_state.daily_picks:

    df = pd.DataFrame(st.session_state.daily_picks)

    df = df.sort_values("Edge",ascending=False)

    st.dataframe(df,use_container_width=True)

    st.subheader("🔥 TOP PICKS DEL DÍA")

    top = df.head(3)

    for _,row in top.iterrows():
        st.success(f"{row['Juego']} | {row['Pitcher']} | EDGE {row['Edge']}")

else:
    st.write("Aún no agregas picks.")
