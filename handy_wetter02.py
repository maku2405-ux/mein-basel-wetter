import streamlit as st
import requests
import pandas as pd
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
# Fussball (Korrigiert auf bsl / 2025)
# -------------------------

def hole_letztes_spiel(team_name):
    try:
        # Abfrage der Swiss Super League (bsl) für die aktuelle Saison 2025
        url = "https://api.openligadb.de/getmatchdata/bsl/2025"
        res = requests.get(url, timeout=10).json()
        
        # Wir suchen das aktuellste Spiel des Teams (das letzte, das ein Ergebnis hat)
        gespielte_spiele = [s for s in res if (team_name in s['team1']['teamName'] or team_name in s['team2']['teamName']) and s['matchIsFinished']]
        
        if gespielte_spiele:
            letztes = gespielte_spiele[-1]
            t1 = letztes['team1']['shortName']
            t2 = letztes['team2']['shortName']
            ergebnis = letztes['matchResults'][0]
            datum = datetime.strptime(letztes['matchDateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%d.%m.")
            return f"{datum}: {t1} {ergebnis['pointsTeam1']}:{ergebnis['pointsTeam2']} {t2}"
        
        return "Keine aktuellen Ergebnisse gefunden"
    except:
        return "Daten aktuell nicht verfügbar"

# -------------------------
# UI
# -------------------------

st.markdown("<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb_info = hole_letztes_spiel("Basel")
    st.session_state.yb_info = hole_letztes_spiel("Young Boys")

# Wetter Anzeige
w = st.session_state.w
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"**{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_e} {w['rhein']}°C")

# Luft & Pollen
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
        st.write(f"PM10: {luft_status(l['pm10'])}")

# Fussball Sektion
st.divider()
st.subheader("⚽ Fussball-Ticker (Super League)")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb_info}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb_info}")

# --- FUSSZEILE ---
st.divider()
st.caption(f"Stand: {datetime.now().strftime('%H:%M')} | Quellen: Open-Meteo, OpenLigaDB")
st.caption("(C)2026 by M. Kunz")
