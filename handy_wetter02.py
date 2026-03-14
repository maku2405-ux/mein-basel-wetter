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

def hole_yb_resultat():
    try:
        # 1. Wir schauen zuerst nach dem NÄCHSTEN Spiel
        next_m = requests.get("https://api.openligadb.de/getnextmatchbyleagueteam/ch1/3", timeout=5).json()
        
        # 2. Wir schauen nach dem LETZTEN Spiel
        last_m = requests.get("https://api.openligadb.de/getlastmatchbyleagueteam/ch1/3", timeout=5).json()
        
        # Logik: Wenn ein Spiel ansteht
        if next_m and not next_m.get('matchIsFinished'):
            gegner = next_m['team2']['teamName'] if next_m['team1']['teamName'] == "BSC Young Boys" else next_m['team1']['teamName']
            termin = next_m['matchDateTime']
            tag_zeit = termin.split('T')[0].split('-')[2] + "." + termin.split('T')[0].split('-')[1] + ". um " + termin.split('T')[1][:5]
            return f"Nächstes YB Spiel: **Gegen {gegner}** ({tag_zeit} Uhr)"
        
        # Falls kein direktes Vorschauspiel da ist, nimm das letzte Resultat
        elif last_m:
            t1 = last_m['team1']['shortName']
            t2 = last_m['team2']['shortName']
            res_list = last_m.get('matchResults', [])
            if res_list:
                e1 = res_list[0]['pointsTeam1']
                e2 = res_list[0]['pointsTeam2']
                return f"Letztes YB Resultat: **{t1} {e1}:{e2} {t2}**"
        
        return "Aktuell keine YB Spieldaten verfügbar"
    except:
        return "YB-Infos aktuell nicht erreichbar"

# 2. Titel in KÖNIGSBLAU (#00529F)
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

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
    elif "wolke" in d_lower or "bewölkt" in d_lower or "wolkig" in d_lower: emoji = "☁️"
    elif "regen" in d_lower: emoji = "🌧️"

    st.metric("Temperatur", f"{emoji} {temp} °C")
    st.write(f"Wetter: **{desc}**")
    
    st.divider()

    # Ozon & Feinstaub (Mitte der App)
    if ozon > 120: st.error(f"Ozon: {ozon} µg/m³ (KRITISCH)")
    elif ozon > 80: st.warning(f"Ozon: {ozon} µg/m³ (Erhöht)")
    else: st.success(f"Ozon: {ozon} µg/m³ (Gut)")

    if pm10 > 50: st.error(f"Feinstaub: {pm10} µg/m³ (KRITISCH)")
    elif pm10 > 35: st.warning(f"Feinstaub: {pm10} µg/m³ (Erhöht)")
    else: st.success(f"Feinstaub: {pm10} µg/m³ (Gut)")

    # 3. FCB GANZ AM ENDE
    st.divider()
    fcb = hole_fcb_resultat()
    st.markdown(f"⚽ **FCB Live-Update:** {fcb}")

else:
    st.error("Fehler beim Laden")

st.caption("Daten: wttr.in, Open-Meteo & OpenLigaDB")
