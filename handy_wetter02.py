import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT, LON = 47.5584, 7.5733

# -------------------------
# Hilfsfunktionen
# -------------------------

def pollen_status(v):
    if v < 10: return "🟢 Niedrig"
    elif v < 50: return "🟡 Achtung"
    else: return "🔴 Hoch"

def luft_status(v):
    if v < 20: return f"🟢 {v}"
    elif v < 50: return f"🟡 {v}"
    else: return f"🔴 {v}"

def rhein_emoji(temp):
    if temp < 18: return "🥶"
    elif 20 <= temp <= 22: return "😊"
    else: return "🙂"

def wetter_beschreibung(code):
    mapping = {0: ("☀️", "Sonnig"), 1: ("🌤️", "Heiter"), 2: ("🌤️", "Leicht bewölkt"), 3: ("☁️", "Wolkig"), 
               45: ("🌫️", "Nebel"), 48: ("🌫️", "Reifnebel"), 51: ("🌧️", "Leichter Regen"), 
               61: ("🌧️", "Regen"), 95: ("⛈️", "Gewitter")}
    return mapping.get(code, ("☁️", "Bedeckt"))

# -------------------------
# Datenabfrage (Wetter & Luft)
# -------------------------

def hole_wetter():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        r = requests.get(url, timeout=10).json()
        c = r["current"]
        emoji, desc = wetter_beschreibung(c["weather_code"])
        return {"temp": c["temperature_2m"], "emoji": emoji, "desc": desc, "rhein": 8.4}
    except: return None

def hole_luft():
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=pm2_5,pm10,ozone,birch_pollen,grass_pollen"
        r = requests.get(url, timeout=10).json()
        c = r["current"]
        return {"ozon": c.get("ozone", 0), "pm25": c.get("pm2_5", 0), "pm10": c.get("pm10", 0),
                "birke": c.get("birch_pollen", 0), "gras": c.get("grass_pollen", 0)}
    except: return None

# -------------------------
# Fussball (Präzise Suche im aktuellen Spieltag)
# -------------------------

def hole_fussball_ticker(team_name):
    try:
        # 1. Wir holen zuerst die Info, welcher Spieltag aktuell ist
        group_res = requests.get("https://api.openligadb.de/getcurrentgroup/bsl").json()
        spieltag = group_res['groupOrderID']
        
        # 2. Wir laden alle Spiele dieses Spieltags (Saison 2025)
        url = f"https://api.openligadb.de/getmatchdata/bsl/2025/{spieltag}"
        res = requests.get(url, timeout=10).json()
        
        for m in res:
            if team_name in m['team1']['teamName'] or team_name in m['team2']['teamName']:
                t1, t2 = m['team1']['shortName'], m['team2']['shortName']
                
                # Wenn Tore vorhanden sind (Spiel läuft oder ist fertig)
                if m['matchResults']:
                    # Wir nehmen das Endergebnis (meist Typ ID 2) oder das aktuellste
                    r = m['matchResults'][0]
                    status = " (Endstand)" if m['matchIsFinished'] else " (LIVE)"
                    return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2}{status}"
                else:
                    # Wenn das Spiel noch nicht angepfiffen wurde
                    zeit = datetime.strptime(m['matchDateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
                    return f"{t1} vs. {t2} (Anpfiff {zeit} Uhr)"
                    
        return "Kein Spiel an diesem Spieltag"
    except: return "Daten aktuell nicht verfügbar"

# -------------------------
# UI Dashboard
# -------------------------

st.markdown("<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball_ticker("Basel")
    st.session_state.yb = hole_fussball_ticker("Young Boys")

# Wetter & Rhein
if st.session_state.w:
    w = st.session_state.w
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"Aktuell: **{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_e} {w['rhein']}°C")

# Pollen & Luftqualität
if st.session_state.l:
    l = st.session_state.l
    st.divider()
    st.write("🌳 **Pollen**")
    cp1, cp2 = st.columns(2)
    cp1.write(f"Birke: {pollen_status(l['birke'])}")
    cp2.write(f"Gräser: {pollen_status(l['gras'])}")

    st.divider()
    st.write("💨 **Luftqualität**")
    cl1, cl2, cl3 = st.columns(3)
    cl1.write(f"Ozon: {luft_status(l['ozon'])}")
    cl2.write(f"PM 2.5: {luft_status(l['pm25'])}")
    cl3.write(f"PM 10: {luft_status(l['pm10'])}")
    
    st.write("") 
    st.caption("**PM 2.5:** Sehr feine Partikel (Autoabgase, Industrie), dringen tief in die Lunge ein.")
    st.caption("**PM 10:** Grössere Staubpartikel (Abrieb, Baustellen, Pollen),
