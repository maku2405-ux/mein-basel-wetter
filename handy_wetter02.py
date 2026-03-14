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
        
        desc = res_w['current_condition'][0]['lang_de'][0]['value']
        
        # --- WETTER EMOJI LOGIK (WIEDER DA) ---
        emoji = "🌡️"
        d_lower = desc.lower()
        if "sonne" in d_lower or "heiter" in d_lower or "klar" in d_lower: emoji = "☀️"
        elif "wolke" in d_lower or "bedeckt" in d_lower or "bewölkt" in d_lower: emoji = "☁️"
        elif "regen" in d_lower or "schauer" in d_lower: emoji = "🌧️"
        elif "gewitter" in d_lower: emoji = "⛈️"
        
        return {
            "temp": res_w['current_condition'][0]['temp_C'],
            "desc": desc,
            "emoji": emoji,
            "ozon": res_l['current']['ozone'],
            "pm10": res_l['current']['pm10']
        }
    except: return None

def hole_fussball(team_id):
    try:
        # Stabilere Abfrage für das nächste Spiel
        url = f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}"
        res = requests.get(url, timeout=5).json()
        if res:
            t1 = res['team1']['shortName']
            t2 = res['team2']['shortName']
            # Zeit-Formatierung
            termin = res['matchDateTime'].split('T')
            datum_roh = termin[0].split('-')
            datum = f"{datum_roh[2]}.{datum_roh[1]}."
            zeit = termin[1][:5]
            
            # Check ob heute
            if datum == datetime.now().strftime('%d.%m.'):
                return f"**Heute:** {t1} vs. {t2} ({zeit} Uhr)"
            return f"{datum} {t1} vs. {t2} ({zeit} Uhr)"
        return "Kein Spiel gefunden"
    except: 
        return "⚠️ Verbindung zur Liga fehlt"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

# Daten laden
if 'daten' not in st.session_state or st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

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
