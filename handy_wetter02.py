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
        return res_w['current_condition'][0]['temp_C'], res_w['current_condition'][0]['lang_de'][0]['value'], res_l['current']['ozone'], res_l['current']['pm10']
    except: return None

def hole_team_info(team_id):
    try:
        # Wir versuchen zuerst das letzte Resultat zu holen
        res = requests.get(f"https://api.openligadb.de/getlastmatchbyleagueteam/ch1/{team_id}", timeout=5).json()
        if res:
            t1 = res['team1']['shortName']
            t2 = res['team2']['shortName']
            r = res.get('matchResults', [])
            if r:
                return f"{t1} {r[0]['pointsTeam1']}:{r[0]['pointsTeam2']} {t2} (Letztes Spiel)"
        return "Keine Daten gefunden"
    except: return "Nicht erreichbar"

st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten_geladen' not in st.session_state:
    st.session_state.daten_geladen = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten_geladen = hole_daten()

daten = st.session_state.daten_geladen

if daten:
    temp, desc, ozon, pm10 = daten
    st.metric("Temperatur", f"🌡️ {temp} °C")
    st.write(f"Wetter: **{desc}**")
    st.divider()

    # Luftqualität
    if ozon > 120: st.error(f"Ozon: {ozon} µg/m³ (KRITISCH)")
    else: st.success(f"Ozon: {ozon} µg/m³ (Gut)")

    if pm10 > 50: st.error(f"Feinstaub: {pm10} µg/m³ (KRITISCH)")
    else: st.success(f"Feinstaub: {pm10} µg/m³ (Gut)")

    # FUSSBALL SEKTION GANZ UNTEN
    st.divider()
    st.subheader("⚽ Fussball-Update")
    
    # FC Basel (ID 128)
    fcb = hole_team_info(128)
    st.write(f"🔴🔵 **FC Basel:** {fcb}")
    
    # Young Boys (ID 131)
    yb = hole_team_info(131)
    st.write(f"🟡⚫ **Young Boys:** {yb}")

else:
    st.error("Fehler beim Laden der Daten")

st.caption("Daten: wttr.in, Open-Meteo & OpenLigaDB")
