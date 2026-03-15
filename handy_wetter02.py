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
# Fussball (Ticker & Tabelle)
# -------------------------

def hole_fussball_daten(team_id):
    try:
        # Holt das letzte Spiel dieses Teams
        r = requests.get(f"https://api.openligadb.de/getlastmatchbyleagueteam/ch1/{team_id}").json()
        t1, t2 = r['team1']['shortName'], r['team2']['shortName']
        res = r['matchResults'][0]
        return f"Letztes Spiel: {t1} {res['pointsTeam1']}:{res['pointsTeam2']} {t2}"
    except: return "Keine aktuellen Spieldaten"

def hole_tabelle():
    try:
        r = requests.get("https://api.openligadb.de/getbltable/ch1/2025").json()
        data = []
        for i, team in enumerate(r, 1):
            data.append({"Rang": i, "Team": team['shortName'], "Pkt": team['points'], "Sp": team['matches']})
        return pd.DataFrame(data)
    except: return None

# -------------------------
# UI
# -------------------------

st.markdown("<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb_info = hole_fussball_daten(128) # FCB
    st.session_state.yb_info = hole_fussball_daten(122)  # YB
    st.session_state.tabelle = hole_tabelle()

# Wetter Anzeige
if st.session_state.w:
    w = st.session_state.w
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"**{w['desc']}**")
    with c2:
        st.metric("Rhein", f"{rhein_emoji(w['rhein'])} {w['rhein']}°C")

# Luft & Pollen
if st.session_state.l:
    l = st.session_state.l
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
st.subheader("⚽ Fussball-Update")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb_info}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb_info}")

if st.session_state.tabelle is not None:
    with st.expander("📊 Super League Tabelle anzeigen"):
        st.dataframe(st.session_state.tabelle, hide_index=True, use_container_width=True)

st.caption(f"Stand: {datetime.now().strftime('%H:%M')} | Basel App 2026")
