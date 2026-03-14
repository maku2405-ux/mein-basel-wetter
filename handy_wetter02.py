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
        # Wir versuchen zuerst das laufende oder letzte Spiel zu finden
        url = f"https://api.openligadb.de/getlastmatchbyleagueteam/ch1/{team_id}"
        res = requests.get(url, timeout=5).json()
        
        if res:
            t1 = res['team1']['shortName']
            t2 = res['team2']['shortName']
            
            # Wenn das Spiel noch läuft oder gerade fertig ist
            if res['matchResults']:
                res_akt = res['matchResults'][-1]
                stand = f"{res_akt['pointsTeam1']}:{res_akt['pointsTeam2']}"
                status = "LIVE" if not res['matchIsFinished'] else "Endstand"
                return f"{t1} {stand} {t2} ({status})"
            
            # Falls kein Live-Spiel, hole das nächste geplante
            url_next = f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}"
            res_n = requests.get(url_next, timeout=5).json()
            if res_n:
                tag = res_n['matchDateTime'].split('T')[0].split('-')[2]
                monat = res_n['matchDateTime'].split('T')[0].split('-')[1]
                zeit = res_n['matchDateTime'].split('T')[1][:5]
                return f"{res_n['team1']['shortName']} vs {res_n['team2']['shortName']} ({tag}.{monat}. um {zeit})"
                
        return "Keine Spiele gefunden"
    except:
        return "⚠️ Verbindung zur Liga fehlt"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

# Daten laden
if 'daten' not in st.session_state or st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()
    # Wir erzwingen auch ein Update der Fussball-Daten beim Klick
    st.session_state.fcb = hole_fussball(128)
    st.session_state.yb = hole_fussball(122)

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
    
    # Anzeige der gespeicherten Fussball-Daten
    st.write(f"🔵🔴 **FC Basel:** {st.session_state.get('fcb', 'Lade...')}")
    st.write(f"🟡⚫ **Young Boys:** {st.session_state.get('yb', 'Lade...')}")
else:
    st.error("Daten konnten nicht geladen werden.")

st.caption(f"Update: {datetime.now().strftime('%H:%M')} | Open-Meteo & OpenLigaDB")
d = st.session_state.daten

if d:
    # Wetter & Luft mit Emoji
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{d['emoji']} {d['temp']} °C")
    col2.write(f"Wetter: **{d['desc']}**")
    
    st.divider()
    
    # Luftqualität
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    # Fussball Ticker
    st.divider()
    st.subheader("⚽ Fussball-Ticker")
    
    # Direktes Laden in der Anzeige für mehr Stabilität
    fcb = hole_fussball(128)
    yb = hole_fussball(122)
    
    st.write(f"🔵🔴 **FC Basel:** {fcb}")
    st.write(f"🟡⚫ **Young Boys:** {yb}")
else:
    st.error("Wetter-Daten konnten nicht geladen werden.")

st.caption(f"Update: {datetime.now().strftime('%H:%M')} | Open-Meteo & OpenLigaDB")
