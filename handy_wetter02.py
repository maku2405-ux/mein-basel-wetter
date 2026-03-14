import streamlit as st
import requests

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

def hole_fcb_resultat():
    try:
        # Holt Daten der Schweizer Super League
        res = requests.get("https://api.openligadb.de/getlastmatchbyleagueteam/ch1/128", timeout=5).json()
        t1 = res['team1']['shortName']
        t2 = res['team2']['shortName']
        # Suche nach dem Endergebnis (Resultat-Typ 2 oder 1)
        ergebnis = res['matchResults'][0]
        return f"{t1} {ergebnis['pointsTeam1']}:{ergebnis['pointsTeam2']} {t2}"
    except: return "FCB-Infos aktuell nicht erreichbar"

st.markdown("<h1 style='text-align: center; color: #FF0000;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten_geladen' not in st.session_state:
    st.session_state.daten_geladen = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten_geladen = hole_daten()

daten = st.session_state.daten_geladen

if daten:
    temp, desc, ozon, pm10 = daten
    emoji = "🌡️"
    d_lower = desc.lower()
    if "sonne" in d_lower or "heiter" in d_lower: emoji = "☀️"
    elif "wolke" in d_lower or "bewölkt" in d_lower: emoji = "☁️"
    elif "regen" in d_lower: emoji = "🌧️"

    st.metric("Temperatur", f"{emoji} {temp} °C")
    st.write(f"Wetter: **{desc}**")
    
    # FCB Sektion
    st.divider()
    fcb = hole_fcb_resultat()
    st.markdown(f"⚽ **FCB Live-Update:** {fcb}")
    st.divider()

    if ozon > 120: st.error(f"Ozon: {ozon} µg/m³ (KRITISCH)")
    elif ozon > 80: st.warning(f"Ozon: {ozon} µg/m³ (Erhöht)")
    else: st.success(f"Ozon: {ozon} µg/m³ (Gut)")

    if pm10 > 50: st.error(f"Feinstaub: {pm10} µg/m³ (KRITISCH)")
    elif pm10 > 35: st.warning(f"Feinstaub: {pm10} µg/m³ (Erhöht)")
    else: st.success(f"Feinstaub: {pm10} µg/m³ (Gut)")
else:
    st.error("Fehler beim Laden")

st.caption("Daten: wttr.in, Open-Meteo & OpenLigaDB")
