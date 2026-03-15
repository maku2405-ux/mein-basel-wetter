import streamlit as st
import requests
from datetime import datetime
import pytz

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

# DEIN API-TOKEN
API_TOKEN = "b63726db10d14e4baf5287dbb338bfb3"
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
# Fussball (Mit deinem API-Token)
# -------------------------

def hole_fussball_ticker(team_name):
    try:
        # ID 2073 = Schweizer Super League
        url = "https://api.football-data.org/v4/competitions/2073/matches"
        headers = {"X-Auth-Token": API_TOKEN}
        
        # Aktuelles Datum für den Filter (HEUTE)
        heute = datetime.now().strftime('%Y-%m-%d')
        # Wir holen alle Spiele der Saison und filtern lokal nach dem Team
        res = requests.get(url, headers=headers, timeout=10).json()
        
        for m in res.get('matches', []):
            t1 = m['homeTeam']['shortName'] or m['homeTeam']['name']
            t2 = m['awayTeam']['shortName'] or m['awayTeam']['name']
            
            # Prüfen, ob unser Team heute spielt
            if team_name.lower() in t1.lower() or team_name.lower() in t2.lower():
                # Zeit umrechnen (UTC zu Schweiz)
                utc_time = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
                local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Zurich'))
                zeit_str = local_time.strftime("%H:%M")
                
                status = m['status']
                if status in ["IN_PLAY", "FINISHED", "PAUSED"]:
                    s1 = m['score']['fullTime']['home']
                    s2 = m['score']['fullTime']['away']
                    tag = " (LIVE)" if status != "FINISHED" else " (Endstand)"
                    return f"{t1} {s1}:{s2} {t2}{tag}"
                else:
                    return f"{t1} vs. {t2} (Anpfiff {zeit_str} Uhr)"
        
        return "Kein Spiel heute"
    except Exception as e: 
        return "Daten aktuell nicht verfügbar"

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
w = st.session_state.w
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"Aktuell: **{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_e} {w['rhein']}°C")

# Pollen & Luftqualität
l = st.session_state.l
if l:
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
    st.caption("**PM 10:** Grössere Staubpartikel (Abrieb, Baustellen, Pollen), belasten die Atemwege.")

# Fussball
st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

# --- FUSSZEILE ---
st.divider()
tz_ch = pytz.timezone('Europe/Zurich')
jetzt_ch = datetime.now(tz_ch).strftime('%H:%M')

st.caption(f"Stand: {jetzt_ch} | Quellen: Open-Meteo, Football-Data.org")
st.caption("(C)2026 by M. Kunz")
