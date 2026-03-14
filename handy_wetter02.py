import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

# Hilfsfunktion für sicheres Laden
def hole_daten():
    try:
        url_wetter = "https://wttr.in/Basel?format=j1&lang=de"
        url_luft = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
        res_w = requests.get(url_wetter, timeout=5).json()
        res_l = requests.get(url_luft, timeout=5).json()
        return {
            "temp": res_w['current_condition'][0]['temp_C'],
            "desc": res_w['current_condition'][0]['lang_de'][0]['value'],
            "ozon": res_l['current']['ozone'],
            "pm10": res_l['current']['pm10']
        }
    except:
        return None

def hole_fussball(team_id):
    try:
        # Check auf laufendes Spiel
        res = requests.get(f"https://api.openligadb.de/getlastmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if res:
            t1, t2 = res['team1']['shortName'], res['team2']['shortName']
            if res['matchResults']:
                r = res['matchResults'][-1]
                status = "LIVE" if not res['matchIsFinished'] else "Endstand"
                return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} ({status})"
        
        # Check auf nächstes Spiel
        res_n = requests.get(f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if res_n:
            t = res_n['matchDateTime'].split('T')
            d = t[0].split('-')[2] + "." + t[0].split('-')[1] + "."
            z = t[1][:5]
            return f"{res_n['team1']['shortName']} vs {res_n['team2']['shortName']} ({d} {z})"
        return "Keine Spiele"
    except:
        return "⚠️ Info folgt"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

# Der Button ist jetzt immer oben sichtbar
if st.button('AKTUALISIEREN'):
    st.session_state.wetter = hole_daten()
    st.session_state.fcb = hole_fussball(128)
    st.session_state.yb = hole_fussball(122)

# Erstmaliges Laden
if 'wetter' not in st.session_state:
    st.session_state.wetter = hole_daten()
    st.session_state.fcb = hole_fussball(128)
    st.session_state.yb = hole_fussball(122)

# Wetter-Teil
w = st.session_state.wetter
if w:
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{w['temp']} °C")
    col2.write(f"Wetter: **{w['desc']}**")
    
    st.divider()
    
    if w['ozon'] > 120: st.error(f"Ozon: {w['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {w['ozon']} µg/m³ (Gut)")
    
    if w['pm10'] > 50: st.error(f"Feinstaub: {w['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {w['pm10']} µg/m³ (Gut)")
else:
    st.warning("Wetterdaten werden geladen...")

# Fussball-Teil (Ganz unten)
st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔵🔴 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

st.caption(f"Update: {datetime.now().strftime('%H:%M')} | Open-Meteo & OpenLigaDB")
