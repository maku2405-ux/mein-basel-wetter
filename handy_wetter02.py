import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

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
    except: return None

def hole_live_ticker(team_name):
    try:
        # Wir holen ALLE Spiele der Saison
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        
        # Wir suchen das Spiel, das heute stattfindet oder als letztes war
        aktuelles_spiel = None
        for spiel in res:
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                aktuelles_spiel = spiel
                # Wenn das Spiel noch nicht vorbei ist, ist es das, was wir suchen!
                if not spiel['matchIsFinished']:
                    break
        
        if aktuelles_spiel:
            s = aktuelles_spiel
            t1 = s['team1']['shortName']
            t2 = s['team2']['shortName']
            
            if s['matchIsFinished']:
                res_fin = s['matchResults'][0]
                return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
            elif s['matchResults']: 
                # Das ist der Live-Ticker Modus
                res_live = s['matchResults'][-1]
                return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
            else:
                # Vorschau für heute
                termin = s['matchDateTime'].split('T')
                uhrzeit = termin[1][:5]
                return f"Heute: {t1} vs. {t2} (Anpfiff {uhrzeit} Uhr)"
        
        return "Kein Spiel in Sicht"
    except: return "Daten laden..."

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten' not in st.session_state:
    st.session_state.daten = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

d = st.session_state.daten
if d:
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{d['temp']} °C")
    col2.write(f"Wetter: **{d['desc']}**")
    
    st.divider()
    
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    st.divider()
    st.subheader("⚽ Fussball-Ticker")
    
    st.write(f"🔵🔴 **FC Basel:** {hole_live_ticker('Basel')}")
    st.write(f"🟡⚫ **Young Boys:** {hole_live_ticker('Young Boys')}")
else:
    st.error("Daten konnten nicht geladen werden.")

st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Basel App")
