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

def hole_fussball(team_id):
    try:
        # Wir holen direkt das nächste Spiel für das Team (Basel=128, YB=122)
        res = requests.get(f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if res:
            t1 = res['team1']['shortName']
            t2 = res['team2']['shortName']
            termin = res['matchDateTime'].split('T')
            datum = termin[0].split('-')[2] + "." + termin[0].split('-')[1] + "."
            zeit = termin[1][:5]
            
            # Prüfen ob es heute ist
            heute = datetime.now().strftime('%d.%m.')
            prefix = "Heute" if datum == heute else datum
            
            return f"{prefix}: {t1} vs. {t2} ({zeit} Uhr)"
        return "Keine aktuellen Spiele gefunden"
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
    
    # 128 = FC Basel, 122 = Young Boys
    st.write(f"🔵🔴 **FC Basel:** {hole_fussball(128)}")
    st.write(f"🟡⚫ **Young Boys:** {hole_fussball(122)}")
else:
    st.error("Daten konnten nicht geladen werden.")

# Hier habe ich das "Basel App" entfernt und durch die Quelle ersetzt
st.caption(f"Letztes Update: {datetime.now().strftime('%H:%M')} | Quelle: Open-Meteo & OpenLigaDB")
