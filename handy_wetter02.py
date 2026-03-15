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
        # Rhein-Temperatur hier statisch gelassen, da kein Sensor-Link vorliegt
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
# Fussball (Gezielte Abfrage für HEUTE)
# -------------------------

def hole_fussball_ticker(team_name):
    try:
        headers = {"X-Auth-Token": API_TOKEN}
        # Wir filtern direkt in der API-Anfrage nach dem heutigen Datum
        heute = datetime.now().strftime('%Y-%m-%d')
        
        # Schweizer Super League (ID 2073)
        url = f"https://api.football-data.org/v4/competitions/2073/matches"
        params = {"dateFrom": heute, "dateTo": heute}
        
        res = requests.get(url, headers=headers, params=params, timeout=10).json()
        matches = res.get('matches', [])
        
        if not matches:
            return "Heute kein Super League Spiel angesetzt."

        for m in matches:
            # Wir prüfen alle Namensvarianten (Vollname und Kurzname)
            h_name = m['homeTeam']['name'] or ""
            h_short = m['homeTeam']['shortName'] or ""
            a_name = m['awayTeam']['name'] or ""
            a_short = m['awayTeam']['shortName'] or ""
            
            if (team_name.lower() in h_name.lower() or team_name.lower() in h_short.lower() or 
                team_name.lower() in a_name.lower() or team_name.lower() in a_short.lower()):
                
                # Zeit UTC -> Schweiz
                utc_time = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
                local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Zurich'))
                zeit_str = local_time.strftime("%H:%M")
                
                status = m['status']
                s1 = m['score']['fullTime']['home']
                s2 = m['score']['fullTime']['away']
                
                t1_display = h_short or h_name
                t2_display = a_short or a_name

                if status in ["TIMED", "SCHEDULED"]:
                    return f"{t1_display} vs. {t2_display} (Anpfiff {zeit_str} Uhr)"
                elif status in ["IN_PLAY", "LIVE", "PAUSED"]:
                    return f"{t1_display} {s1}:{s2} {t2_display} 🟢 LIVE"
                elif status == "FINISHED":
                    return f"{t1_display} {s1}:{s2} {t2_display} (Endstand)"
        
        return "Kein Spiel für dieses Team heute."
    except:
        return "Daten aktuell nicht erreichbar."

# -------------------------
# UI Dashboard
# -------------------------

st.markdown("<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

# Button zum manuellen Aktualisieren
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

# Fussball-Ticker
st.divider()
st.subheader("⚽ Fussball-Ticker (Live)")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

# --- FUSSZEILE ---
st.divider()
tz_ch = pytz.timezone('Europe/Zurich')
jetzt_ch = datetime.now(tz_ch).strftime('%H:%M')

st.caption(f"Stand: {jetzt_ch} | Quellen: Open-Meteo, Football-Data.org")
st.caption("(C)2026 by M. Kunz")
