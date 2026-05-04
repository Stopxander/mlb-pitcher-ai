import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="MLB AUTO SHARP SCANNER", layout="wide")

st.title("⚾ MLB AUTO SHARP SCANNER")

TODAY = date.today().strftime("%Y-%m-%d")

# ======================
# GET MLB GAMES
# ======================

def get_games():

    url=f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={TODAY}"
    data=requests.get(url).json()

    if not data["dates"]:
        return []

    games=[]

    for g in data["dates"][0]["games"]:

        away=g["teams"]["away"]["team"]["name"]
        home=g["teams"]["home"]["team"]["name"]

        away_p=g["teams"]["away"].get("probablePitcher",{})
        home_p=g["teams"]["home"].get("probablePitcher",{})

        games.append({
            "game":f"{away} @ {home}",
            "away_pitcher":away_p.get("fullName"),
            "away_id":away_p.get("id"),
            "home_pitcher":home_p.get("fullName"),
            "home_id":home_p.get("id")
        })

    return games


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
# VULNERABILITY MODEL
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

    if score>=95:
        return "🔥 ELITE TARGET"

    elif score>=75:
        return "🔴 Vulnerable"

    elif score>=60:
        return "🟡 Neutral"

    return "🟢 Stable"


# ======================
# SHARP ANALYSIS
# ======================

def sharp_model(tickets,money,open_line,current_line):

    sharp_edge=money-tickets
    line_move=current_line-open_line

    signals=[]

    if sharp_edge>15:
        signals.append("Sharp Money")

    if sharp_edge>0 and line_move<0:
        signals.append("Reverse Line Movement")

    if tickets<40 and money>60:
        signals.append("Contrarian Play")

    return sharp_edge,line_move,signals


# ======================
# BET ENGINE
# ======================

def bet_signal(vuln,signals):

    if vuln>90 and "Sharp Money" in signals:
        return "💰 SYNDICATE PLAY"

    if vuln>80:
        return "🎯 HR / HITS PROPS"

    if "Reverse Line Movement" in signals:
        return "📈 Follow Sharp Side"

    return "No Edge"


# ======================
# MAIN APP
# ======================

games=get_games()

if not games:
    st.warning("No games today")
    st.stop()

top=[]

for g in games:

    st.markdown("---")
    st.header(g["game"])

    st.subheader("📊 Market Data (Action Network / ZCode)")

    col1,col2,col3,col4=st.columns(4)

    tickets=col1.slider("% Tickets",0,100,50,key=g["game"]+"t")
    money=col2.slider("% Money",0,100,50,key=g["game"]+"m")
    open_line=col3.number_input("Opening Line",value=-110,key=g["game"]+"o")
    current_line=col4.number_input("Current Line",value=-110,key=g["game"]+"c")

    sharp_edge,line_move,signals=sharp_model(
        tickets,money,open_line,current_line
    )

    st.write("Signals:",signals if signals else "None")

    cols=st.columns(2)

    pitchers=[
        ("Away",g["away_pitcher"],g["away_id"]),
        ("Home",g["home_pitcher"],g["home_id"])
    ]

    for col,p in zip(cols,pitchers):

        side,name,pid=p

        with col:

            if not name:
                st.write(f"{side}: TBD")
                continue

            st.subheader(name)

            stats=pitcher_stats(pid)

            if not stats:
                st.warning("No stats")
                continue

            vuln=vulnerability(stats)
            status=classify(vuln)

            signal=bet_signal(vuln,signals)

            st.metric("Vulnerability",vuln)
            st.markdown(status)
            st.success(signal)

            if signal!="No Edge":
                top.append((g["game"],name,signal))


st.markdown("---")
st.header("⭐ AUTO SYNDICATE PLAYS")

if not top:
    st.write("No strong edges today")

for t in top:
    st.write(f"{t[0]} — {t[1]} → {t[2]}")
