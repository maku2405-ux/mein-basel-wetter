import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

def hole_wetter():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        curr = res['current']
        temp, code = curr['temperature_2m'], curr['weather_code']
        
        emoji, desc = "🌡️", "Unbekannt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [45, 48]: emoji, desc = "🌫️", "Nebel"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        else: emoji, desc = "☁️", "Bedeckt"
        
        return {"temp": temp, "emoji": emoji, "desc": desc}
    except: return None

def hole_luft():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
        res = requests.get(url, timeout=5).json()
        return {"ozon": res['current']['ozone'], "pm10": res['current']['pm10']}
    except: return None

def hole_fussball(team_id):
    try:
        # Wir holen direkt das nächste Spiel für die spezifische Team-ID
        # Basel = 128, YB = 122
        url = f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}"
        s = requests.get(url, timeout=5).json()
        
        if s:
            t1, t2 = s['team1']['shortName'], s['team2']['shortName']
            termin = s['matchDateTime'].split('T')
            datum_raw = termin[0].split('-')
            datum = f"{datum_raw[2]}.{datum_raw[1]}."
            uhrzeit = termin[1][:5]
            
            # Check ob es heute ist
            heute = datetime.now().strftime('%d.%m.')
            prefix = "Heute" if datum == heute else datum
            
            # Falls das Spiel schon läuft oder fertig ist, Resultat zeigen
            if s['matchResults']:
                res_akt = s['matchResults'][-1]
                tore = f"{res_akt['pointsTeam1']}:{res_akt['pointsTeam2']}"
                status = "LIVE" if not s['matchIsFinished'] else "Endstand"
                return f"{t1} {tore} {t2} ({status})"
            
            return f"{prefix}: {t1} vs. {t2} ({uhrzeit} Uhr)"
        return "Kein Spiel gefunden"
    except: return "⚠️ Verbindung klemmt"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if st.button('AKTUALISIEREN') or 'w' not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball(128) # Basel
    st.session_state.yb = hole_fussball(122)  # YB

# Wetter & Luft Anzeige
w, l = st.session_state.w, st.session_state.l
if w:
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{w['emoji']} {w['temp']} °C")
    col2.write(f"Wetter: **{w['desc']}**")

if l:
    st.divider()
    if l['ozon'] > 120: st.error(f"Ozon: {l['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {l['ozon']} µg/m³ (Gut)")
    
    if l['pm10'] > 50: st.error(f"Feinstaub: {l['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {l['pm10']} µg/m³ (Gut)")

# Fussball
st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔵🔴 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

st.caption(f"Letztes Update: {datetime.now().strftime('%H:%M')} | Daten: Open-Meteo & OpenLigaDB")
