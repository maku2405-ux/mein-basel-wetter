import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

def hole_wetter_und_rhein():
    try:
        # Wetter & Rhein-Temperatur via Open-Meteo
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        
        # Rhein-Temperatur (Simulation basierend auf kantonalen Werten)
        rhein_temp = 8.4  
        
        curr = res['current']
        temp, code = curr['temperature_2m'], curr['weather_code']
        
        emoji, desc = "☁️", "Bedeckt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        
        return {"temp": temp, "emoji": emoji, "desc": desc, "rhein": rhein_temp}
    except:
        return None

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
    except:
        return None

def hole_fcb_ticker(team_id):
    try:
        # OpenLigaDB für Schweizer Super League (ch1)
        res = requests.get(f"https://api.openligadb.de/getmatchdata/ch1/2026", timeout=5).json()
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
    except:
        return "Daten konnten nicht geladen werden"

# --- UI DESIGN ---
# Einbinden des echten Baslerstabs via HTML/IMG
baslerstab_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Basel-Stadt-Anw.svg/40px-Basel-Stadt-Anw.svg.png"

st.markdown(
    f"""
    <div style='display: flex; align-items: center; justify-content: center;'>
        <img src='{baslerstab_url}' style='height: 40px; margin-right: 15px;'>
        <h1 style='color: #000000; margin: 0;'>Basel Dashboard</h1>
        <img src='{baslerstab_url}' style='height: 40px; margin-left: 15px;'>
    </div>
    """, 
    unsafe_allow_html=True
)

# Initialisierung der Session State Daten
if 'w' not in st.session_state:
    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()
    st.session_state.fcb = hole_fcb_ticker(128) # Basel
    st.session_state.yb = hole_fcb_ticker(122)  # YB

if st.button('🔄 DATEN AKTUALISIEREN'):
    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()
    st.session_state.fcb = hole_fcb_ticker(128)
    st.session_state.yb = hole_fcb_ticker(122)
    st.rerun()

# 1. Wetter & Rhein
w = st.session_state.w
if w:
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"Aktuell: **{w['desc']}**")
    
    with c2:
        st.metric("Rhein", f"🌊 {w['rhein']}°C")

# 2. Luftqualität & Pollen
l = st.session_state.l
if l:
    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("🌳 **Pollen:**")
        st.caption(f"Birke: {'Niedrig' if l['birke'] < 10 else 'Hoch'}")
        st.caption(f"Gräser: {'Niedrig' if l['gras'] < 10 else 'Hoch'}")
    with col_p2:
        st.write("💨 **Luftqualität:**")
        st.caption(f"Ozon: {l['ozon']} µg/m³")
        st.caption(f"Feinstaub (PM10): {l['pm10']} µg/m³")

# 3. Fussball-Ticker
st.divider()
st.write("⚽ **Fussball Ticker:**")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **BSC Young Boys:** {st.session_state.yb}")
