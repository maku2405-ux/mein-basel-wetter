import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

def hole_wetter_und_rhein():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        
        # Rhein-Temperatur Simulation (Basel Rheinhalle)
        rhein_temp = 8.4  
        
        curr = res['current']
        temp, code = curr['temperature_2m'], curr['weather_code']
        
        emoji, desc = "☁️", "Bedeckt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        
        return {"temp": temp, "emoji": emoji, "desc": desc, "rhein": rhein_temp}
    except: return None

def hole_luft_und_pollen():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone,birch_pollen,grass_pollen"
        res = requests.get(url, timeout=5).json()
        curr = res['current']
        return {
            "ozon": curr['ozone'], 
            "pm10": curr['pm10'],
            "birke": curr['birch_pollen'],
            "gras": curr['grass_pollen']
        }
    except: return None

def hole_fcb_ticker(team_id):
    try:
        res = requests.get(f"https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        jetzt = datetime.now()
        for spiel in res:
            if team_id == spiel['team1']['teamID'] or team_id == spiel['team2']['teamID']:
                zeit = datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
                if zeit.date() >= jetzt.date():
                    t1, t2 = spiel['team1']['shortName'], spiel['team2']['shortName']
                    if spiel['matchResults'] and not spiel['matchIsFinished']:
                        r = spiel['matchResults'][-1]
                        return f"🔴 LIVE: {t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2}"
                    prefix = "Heute" if zeit.date() == jetzt.date() else zeit.strftime("%d.%m.")
                    return f"{prefix}: {t1} vs. {t2} ({zeit.strftime('%H:%M')} Uhr)"
        return "Kein Spiel geplant"
    except: return "Daten laden..."

# --- UI DESIGN ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

if st.button('🔄 DATEN AKTUALISIEREN') or 'w' not in st.session_state:
    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()
    st.session_state.fcb = hole_fcb_ticker(128)
    st.session_state.yb = hole_fcb_ticker(122)

# 1. Wetter & Rhein
w = st.session_state.w
if w:
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"**{w['desc']}**")
    with c2:
        st.metric("Rhein", f"🌊 {w['rhein']}°C")

# 2. Luftqualität & Pollen (MIT FARB-WARNUNG)
l = st.session_state.l
if l:
    st.divider()
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        st.write("🌳 **Pollen:**")
        # Birke Warnung
        if l['birke'] > 50: st.error(f"Birke: Hoch")
        elif l['birke'] > 10: st.warning(f"Birke: Mittel")
        else: st.success(f"Birke: Niedrig")
        
        # Gräser Warnung
        if l['gras'] > 50: st.error(f"Gräser: Hoch")
        elif l['gras'] > 10: st.warning(f"Gräser: Mittel")
