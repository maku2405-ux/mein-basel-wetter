import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT = 47.5584
LON = 7.5733

# -------------------------
# Hilfsfunktionen
# -------------------------

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
    elif temp > 22:
        return "🥵"
    else:
        return "🙂"

def wetter_beschreibung(code):
    if code == 0:
        return "☀️", "Sonnig"
    if code in [1, 2, 3]:
        return "🌤️", "Leicht bewölkt"
    if code in [45, 48]:
        return "🌫️", "Neblig"
    if code in [51, 53, 55, 61, 63, 65]:
        return "🌧️", "Regen"
    if code in [71, 73, 75]:
        return "❄️", "Schnee"
    return "☁️", "Bedeckt"

# -------------------------
# Wetter + Rhein
# -------------------------

def hole_wetter():
    try:
        # KORREKTUR: &current statt Sonderzeichen
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        r = requests.get(url, timeout=10).json()
        c = r["current"]
        temp = c["temperature_2m"]
        code = c["weather_code"]
        emoji, desc = wetter_beschreibung(code)
        rhein = 8.4 # Platzhalter Rheinwert
        return {"temp": temp, "emoji": emoji, "desc": desc, "rhein": rhein}
    except:
        return None

# -------------------------
# Luftqualität + Pollen
# -------------------------

def hole_luft():
    try:
        # KORREKTUR: &current statt Sonderzeichen
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=pm2_5,pm10,ozone,birch_pollen,grass_pollen"
        r = requests.get(url, timeout=10).json()
        c = r["current"]
        return {
            "ozon": c.get("ozone", 0),
            "pm25": c.get("pm2_5", 0),
            "pm10": c.get("pm10", 0),
            "birke": c.get("birch_pollen", 0),
            "gras": c.get("grass_pollen", 0)
        }
    except:
        return None

# -------------------------
# Fussball Ticker (Echte Daten)
# -------------------------

def hole_fussball_daten(team_name):
    try:
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        for spiel in reversed(res):
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                t1, t2 = spiel['team1']['shortName'], spiel['team2']['shortName']
                if spiel['matchIsFinished']:
                    r = spiel['matchResults'][0]
                    return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} (Endstand)"
                elif spiel['matchResults']:
                    r = spiel['matchResults'][-1]
                    return f"🔴 LIVE: {t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2}"
                else:
                    zeit = spiel['matchDateTime'].split('T')[1][:5]
                    return f"{t1} vs. {t2} (Anpfiff {zeit} Uhr)"
        return "Keine aktuellen Daten"
    except:
        return "Daten nicht verfügbar"

# -------------------------
# UI
# -------------------------

st.markdown("<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball_daten("Basel")
    st.session_state.yb = hole_fussball_daten("Young Boys")

# --- WETTER ANZEIGE ---
w = st.session_state.w
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"**{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_e} {w['rhein']}°C")

# --- LUFT ANZEIGE ---
l = st.session_state.l
if l:
    st.divider()
    cl1, cl2 = st.columns(2)
    with cl1:
        st.write("🌳 **Pollen**")
        st.write(f"Birke: {pollen_status(l['birke'])}")
        st.write(f"Gräser: {pollen_status(l['gras'])}")
    with cl2:
        st.write("💨 **Luftqualität**")
        st.write(f"Ozon: {luft_status(l['ozon'])}")
        st.write(f"PM2.5: {luft_status(l['pm25'])}")
        st.write(f"PM10: {luft_status(l['pm10'])}")

# --- FUSSBALL ANZEIGE ---
st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

st.caption(f"Stand: {datetime.now().strftime('%H:%M')} | Basel App 2026")
