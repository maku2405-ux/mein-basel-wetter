import streamlit as st
import requests
from datetime import datetime
import pytz

# ---------------------------------------------------------
# Seiteneinstellungen
# ---------------------------------------------------------
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

# API KEY für API-Football (RapidAPI)
API_FOOTBALL_KEY = "DEIN_RAPIDAPI_KEY_HIER_EINFÜGEN"
LAT = 47.5584
LON = 7.5733

# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------

def pollen_status(v):
    if v < 10:
        return "🟢 Niedrig"
    elif v < 50:
        return "🟡 Achtung"
    else:
        return "🔴 Hoch"

def luft_status(v):
    if v < 20:
        return f"🟢 {v}"
    elif v < 50:
        return f"🟡 {v}"
    else:
        return f"🔴 {v}"

def rhein_emoji(temp):
    if temp < 18:
        return "🥶"
    elif 20 <= temp <= 22:
        return "😊"
    else:
        return "🙂"

def wetter_beschreibung(code):
    mapping = {
        0: ("☀️", "Sonnig"),
        1: ("🌤️", "Heiter"),
        2: ("🌤️", "Leicht bewölkt"),
        3: ("☁️", "Wolkig"),
        45: ("🌫️", "Nebel"),
        48: ("🌫️", "Reifnebel"),
        51: ("🌧️", "Leichter Regen"),
        61: ("🌧️", "Regen"),
        95: ("⛈️", "Gewitter")
    }
    return mapping.get(code, ("☁️", "Bedeckt"))

# ---------------------------------------------------------
# Wetter & Luftdaten
# ---------------------------------------------------------

def hole_wetter():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            "&current=temperature_2m,weather_code"
            "&timezone=Europe%2FBerlin"
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        c = data["current"]
        emoji, desc = wetter_beschreibung(c["weather_code"])
        return {
            "temp": c["temperature_2m"],
            "emoji": emoji,
            "desc": desc,
            "rhein": 8.4
        }
    except Exception:
        return None

def hole_luft():
    try:
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={LAT}&longitude={LON}"
            "&current=pm2_5,pm10,ozone,birch_pollen,grass_pollen"
        )
        r = requests.get(url, timeout=10)
        data = r.json()
        c = data["current"]
        return {
            "ozon": c.get("ozone", 0),
            "pm25": c.get("pm2_5", 0),
            "pm10": c.get("pm10", 0),
            "birke": c.get("birch_pollen", 0),
            "gras": c.get("grass_pollen", 0)
        }
    except Exception:
        return None

# ---------------------------------------------------------
# Fussball (API-Football)
# ---------------------------------------------------------

TEAM_BASEL = 256
TEAM_YB = 257

def hole_fussball_ticker(team_id):
    try:
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            "x-rapidapi-key": API_FOOTBALL_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

        heute = datetime.now().strftime("%Y-%m-%d")

        # 1) Heutiges Spiel
        params_today = {
            "team": team_id,
            "date": heute,
            "timezone": "Europe/Zurich"
        }

        r_today = requests.get(url, headers=headers, params=params_today, timeout=10)
        data_today = r_today.json()
        games_today = data_today.get("response", [])

        if games_today:
            m = games_today[0]
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            status = m["fixture"]["status"]["short"]
            goals_home = m["goals"]["home"]
            goals_away = m["goals"]["away"]

            if status == "NS":
                zeit = m["fixture"]["date"][11:16]
                return f"{home} vs. {away} (Anpfiff {zeit})"

            if status in ["1H", "2H", "HT"]:
                return f"{home} {goals_home}:{goals_away} {away} 🟢 LIVE"

            if status == "FT":
                return f"{home} {goals_home}:{goals_away} {away} (Endstand)"

            return "Spielstatus unbekannt."

        # 2) Letztes Spiel
        params_last = {
            "team": team_id,
            "last": 1,
            "timezone": "Europe/Zurich"
        }

        r_last = requests.get(url, headers=headers, params=params_last, timeout=10)
        data_last = r_last.json()
        last_games = data_last.get("response", [])

        if last_games:
            m = last_games[0]
            home = m["teams"]["home"]["name"]
            away = m["teams"]["away"]["name"]
            goals_home = m["goals"]["home"]
            goals_away = m["goals"]["away"]
            datum = m["fixture"]["date"][:10]
            return f"Letztes Spiel ({datum}): {home} {goals_home}:{goals_away} {away}"

        return "Keine Daten verfügbar."

    except Exception:
        return "Daten nicht erreichbar."

# ---------------------------------------------------------
# UI Dashboard
# ---------------------------------------------------------

st.markdown(
    "<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>",
    unsafe_allow_html=True
)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball_ticker(TEAM_BASEL)
    st.session_state.yb = hole_fussball_ticker(TEAM_YB)

# Wetter
w = st.session_state.get("w")
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"Aktuell: **{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_e} {w['rhein']}°C")

# Umwelt
st.divider()
st.subheader("🌳 Umwelt & Luft")

l = st.session_state.get("l")
if l:
    st.write("**Aktuelle Werte:**")
    cp1, cp2 = st.columns(2)
    cp1.write(f"Birke: {pollen_status(l['birke'])}")
    cp2.write(f"Gräser: {pollen_status(l['gras'])}")

    st.write("")
    cl1, cl2, cl3 = st.columns(3)
    cl1.write(f"Ozon: {luft_status(l['ozon'])}")
    cl2.write(f"PM 2.5: {luft_status(l['pm25'])}")
    cl3.write(f"PM 10: {luft_status(l['pm10'])}")
else:
    st.warning("Umweltdaten konnten nicht geladen werden.")

st.write("")
st.markdown(
    "<small><b>PM 2.5:</b> Sehr feine Partikel (Autoabgase, Industrie), dringen tief in die Lunge ein.</small>",
    unsafe_allow_html=True
)
st.markdown(
    "<small><b>PM 10:</b> Grössere Staubpartikel (Abrieb, Baustellen, Pollen), belasten die Atemwege.</small>",
    unsafe_allow_html=True
)

# Fussball
st.divider()
st.subheader("⚽ Fussball-Ticker")

fcb_text = st.session_state.get("fcb", "Keine Daten")
yb_text = st.session_state.get("yb", "Keine Daten")

st.write("🔴🔵 FC Basel: " + fcb_text)
st.write("🟡⚫ Young Boys: " + yb_text)

# Fusszeile
st.divider()
tz_ch = pytz.timezone("Europe/Zurich")
jetzt_ch = datetime.now(tz_ch).strftime("%H:%M")

st.caption(f"Stand: {jetzt_ch} | Quellen: Open-Meteo, API-Football")
st.caption("(C)2026 by M. Kunz")
