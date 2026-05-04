import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("⚾ MLB EDGE FINDER AI")

# ------------------------------------------------
# MODELO EDGE
# ------------------------------------------------

def calculate_edge(hr9, barrel, woba, iso, park, sharp):

    hr_risk = (
        hr9 * 20 +
        barrel * 1.5 +
        woba * 100 +
        iso * 120 +
        park * 15
    )

    hit_risk = (
        woba * 150 +
        iso * 100 +
        barrel * 1.2
    )

    edge_score = hr_risk + sharp * 0.5

    if edge_score > 95:
        label = "🔥 TOP EDGE DEL DÍA"
    elif edge_score > 75:
        label = "💰 Edge Positivo"
    elif edge_score > 60:
        label = "⚠️ Lean"
    else:
        label = "❌ Sin Valor"

    return round(hr_risk,2), round(hit_risk,2), round(edge_score,2), label


# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

if "pitcher_data" not in st.session_state:
    st.session_state.pitcher_data = {}

# ------------------------------------------------
# OBTENER JUEGOS MLB
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

    # -------------------------
    # SELECTORES
    # -------------------------

    selected_game = st.selectbox("Juego", list(game_map.keys()))

    pitchers = [
        f"Visitante — {game_map[selected_game]['away_pitcher']}",
        f"Local — {game_map[selected_game]['home_pitcher']}"
    ]

    selected_pitcher = st.selectbox("Pitcher", pitchers)

    key = selected_game + selected_pitcher

    # -------------------------
    # DEFAULT DATA
    # -------------------------

    if key not in st.session_state.pitcher_data:
        st.session_state.pitcher_data[key] = {}

    pdata = st.session_state.pitcher_data[key]

    # FIX errores futuros
    pdata.setdefault("hand","R")
    pdata.setdefault("hr9",1.2)
    pdata.setdefault("barrel",8.0)
    pdata.setdefault("woba",0.320)
    pdata.setdefault("iso",0.170)
    pdata.setdefault("park",1.05)
    pdata.setdefault("sharp",50)

    # ------------------------------------------------
    # INPUTS
    # ------------------------------------------------

    st.subheader(f"📊 Analizando: {selected_pitcher}")

    col1, col2, col3 = st.columns(3)

    pdata["hand"] = col1.selectbox(
        "Mano del Pitcher",
        ["R","L"],
        index=0 if pdata["hand"]=="R" else 1,
        key=key+"hand"
    )

    pdata["hr9"] = col1.number_input(
        "HR/9",
        value=float(pdata["hr9"]),
        key=key+"hr9"
    )

    pdata["barrel"] = col2.number_input(
        "Barrel %",
        value=float(pdata["barrel"]),
        key=key+"barrel"
    )

    pdata["woba"] = col3.number_input(
        "Split wOBA Allowed",
        value=float(pdata["woba"]),
        key=key+"woba"
    )

    pdata["iso"] = col1.number_input(
        f"Lineup ISO vs {'RHP' if pdata['hand']=='R' else 'LHP'}",
        value=float(pdata["iso"]),
        key=key+"iso"
    )

    pdata["park"] = col2.number_input(
        "Ballpark HR Factor",
        value=float(pdata["park"]),
        key=key+"park"
    )

    pdata["sharp"] = col3.slider(
        "Sharp Money Index",
        0,
        100,
        int(pdata["sharp"]),
        key=key+"sharp"
    )

    # ------------------------------------------------
    # CALCULO EDGE
    # ------------------------------------------------

    hr_score, hit_score, edge_score, label = calculate_edge(
        pdata["hr9"],
        pdata["barrel"],
        pdata["woba"],
        pdata["iso"],
        pdata["park"],
        pdata["sharp"]
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("HR Risk", hr_score)
    c2.metric("Hit Risk", hit_score)
    c3.metric("EDGE SCORE", edge_score)

    if "TOP EDGE" in label:
        st.error(label)
    elif "Positivo" in label:
        st.success(label)
    elif "Lean" in label:
        st.warning(label)
    else:
        st.info(label)

else:
    st.write("No hay juegos hoy.")
