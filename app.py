import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="MLB PROP AI", layout="wide")

st.title("⚾ MLB PLAYER PROP AI ENGINE")

TODAY=date.today().strftime("%Y-%m-%d")

# ======================
# GET GAMES
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
            "avg":float(s.get("avg",.250)),
            "hand":s.get("pitchHand",{}).get("code","R")
        }

    except:
        return None


# ======================
# MODELS
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
# PROP ENGINE
# ======================

def prop_recommendation(stats,score):

    props=[]

    if score>90:
        props.append("HR Props")
        props.append("Total Bases Over")

    if stats["hr9"]>1.4:
        props.append("Power Hitters")

    if stats["whip"]>1.35:
        props.append("Hits Props")

    if stats["hand"]=="R":
        props.append("Target LEFT handed batters")

    else:
        props.append("Target RIGHT handed batters")

    return props


# ======================
# SHARP MODEL
# ======================

def sharp_model(tickets,money):

    edge=money-tickets

    if edge>15:
        return "💰 Sharp Money"

    if edge>5:
        return "📈 Slight Sharp Edge"

    return "Public Game"


# ======================
# MAIN
# ======================

games=get_games()

if not games:
    st.warning("No games today")
    st.stop()

top=[]

for g in games:

    st.markdown("---")
    st.header(g["game"])

    col1,col2=st.columns(2)

    tickets=col1.slider("% Tickets",0,100,50,key=g["game"]+"t")
    money=col2.slider("% Money",0,100,50,key=g["game"]+"m")

    sharp_signal=sharp_model(tickets,money)

    st.write("Market Signal:",sharp_signal)

    cols=st.columns(2)

    pitchers=[
        ("Away",g["away_pitcher"],g["away_id"]),
        ("Home",g["home_pitcher"],g["home_id"])
    ]

    for col,p in zip(cols,pitchers):

        side,name,pid=p

        with col:

            if not name:
                st.write("TBD")
                continue

            st.subheader(name)

            stats=pitcher_stats(pid)

            if not stats:
                st.warning("No stats")
                continue

            score=vulnerability(stats)
            status=classify(score)

            st.metric("Vulnerability",score)
            st.markdown(status)

            props=prop_recommendation(stats,score)

            st.write("🎯 PROP TARGETS")
            for pr in props:
                st.write("•",pr)

            if score>85:
                top.append((g["game"],name,props))


st.markdown("---")
st.header("⭐ TOP PLAYER PROP SPOTS")

if not top:
    st.write("No elite prop spots")

for t in top:
    st.write(f"{t[0]} — Attack {t[1]} → {', '.join(t[2])}")
