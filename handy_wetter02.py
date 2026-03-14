import streamlit as st
import requests

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

def hole_daten():
    stadt = "Basel"
    url_wetter = f"https://wttr.in/{stadt}?format=j1&lang=de"
    url_luft = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
    try:
        res_w = requests.get(url_wetter, timeout=5).json()
        res_l = requests.get(url_luft, timeout=5).json()
        temp = res_w['current_condition'][0]['temp_C']
        desc = res_w['current_condition'][0]['lang_de'][0]['value']
        ozon = res_l['current']['ozone']
        pm10 = res_l['current']['pm10']
        return temp, desc, ozon, pm10
    except: return None

def hole_fussball_info(team_id):
    try:
        # Prüfe das nächste Spiel
        next_m = requests.get(f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if next_m and not next_m.get('matchIsFinished'):
            t1 = next_m['team1']['shortName']
            t2 = next_m['team2']['shortName']
            termin = next_m['matchDateTime'].split('T')[1][:5]
            return f"{t1} vs. {t2} (Morgen {termin} Uhr)"
        
        # Prüfe das letzte Spiel (für Resultat/Live)
        last_m = requests.get(f"https://api.openligadb.de/getlastmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if last_m:
            t1 = last_m['team1']['shortName']
            t2 = last_m['team2']['shortName']
            res_list = last_m.get('matchResults', [])
            if res_list:
                e1 = res_list[-1]['pointsTeam1']
                e2 = res_list[-1]['pointsTeam2']
                status = "LIVE" if not last_m['matchIsFinished'] else "Endstand"
                return f"{t1} {e1}:{e2} {t2} ({status})"
        return "Keine Daten"
    except: return "Nicht erreichbar"

# Titel in KÖNIGSBLAU
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten_geladen' not in st.session_state:
    st.session_state.daten_geladen = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten_geladen = hole_daten()

daten = st.session_state.daten_geladen

if daten:
    temp, desc, ozon, pm10 = daten
    
    # Verbesserte Emoji-Logik
    emoji = "🌡️"
    d_low = desc.lower()
    if any(x in d_low for x in ["sonne", "heiter", "klar"]): emoji = "☀️"
    elif any(x in d_low for x in ["wolke", "bewölkt", "wolkig", "bedeckt"]): emoji = "☁️"
    elif any(x in d_low for x in ["regen", "schauer", "nass"]): emoji = "🌧️"
    elif "gewitter" in d_low: emoji = "⛈️"

    st.metric("Temperatur", f"{emoji} {temp} °C")
    st.write(f"Wetter: **{desc}**")
    
    st.divider()

    # Ozon & Feinstaub
    if ozon > 120: st.error(f"Ozon: {ozon} µg/m³ (KRITISCH)")
    elif ozon > 80: st.warning(f"Ozon: {ozon} µg/m³ (Erhöht)")
    else: st.success(f"Ozon: {ozon} µg/m³ (Gut)")

    if pm10 > 50: st.error(f"Feinstaub: {pm10} µg/m³ (KRITISCH)")
    elif pm10 > 35: st.warning(f"Feinstaub: {pm10} µg/m³ (Erhöht)")
    else: st.success(f"Feinstaub: {pm10} µg/m³ (Gut)")

    # FUSSBALL UPDATE
    st.divider()
    st.subheader("⚽ Fussball-Update")
    
    fcb = hole_fussball_info(128)
    yb = hole_fussball_info(122)
    
    st.markdown(f"🔴🔵 **FC Basel:** {fcb}")
    st.markdown(f"🟡⚫ **Young Boys:** {yb}")

else:
    st.error("Fehler beim Laden")

st.caption("Daten: wttr.in, Open-Meteo & OpenLigaDB")
