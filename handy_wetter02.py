import streamlit as st
import requests

# Seiteneinstellungen für das Natel
st.set_page_config(page_title="Basel Air Monitor", page_icon="🇨🇭")

def hole_daten():
    stadt = "Basel"
    url_wetter = f"https://wttr.in/{stadt}?format=j1"
    url_luft = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
    
    try:
        # Wetter & Luft laden
        res_w = requests.get(url_wetter).json()
        res_l = requests.get(url_luft).json()
        
        temp = res_w['current_condition'][0]['temp_C']
        beschreibung = res_w['current_condition'][0]['weatherDesc'][0]['value']
        ozon = res_l['current']['ozone']
        feinstaub = res_l['current']['pm10']
        
        return temp, beschreibung, ozon, feinstaub
    except:
        return None

st.title("🇨🇭 Basel Air Monitor")

# Diese Zeile sorgt dafür, dass die Daten sofort beim Start geladen werden
if 'daten_geladen' not in st.session_state:
    st.session_state.daten_geladen = hole_daten()

# Der Button kann die Daten jederzeit neu erzwingen
if st.button('AKTUALISIEREN'):
    st.session_state.daten_geladen = hole_daten()

# Hier werden die Werte angezeigt (egal ob vom Start oder vom Button)
daten = st.session_state.daten_geladen

if daten:
    temp, desc, ozon, pm10 = daten
    # ... (hier kommt dein restlicher Code für st.metric, st.success usw.)
    if daten:
        temp, desc, ozon, pm10 = daten
        
        # Temperatur Anzeige
        st.metric("Temperatur", f"{temp} °C")
        st.write(f"Wetter: **{desc}**")
        
        st.divider()
        
        # Ozon Ampel
        if ozon > 120:
            st.error(f"Ozon: {ozon} µg/m³ (KRITISCH)")
        elif ozon > 80:
            st.warning(f"Ozon: {ozon} µg/m³ (Erhöht)")
        else:
            st.success(f"Ozon: {ozon} µg/m³ (Gut)")

        # Feinstaub Ampel
        if pm10 > 50:
            st.error(f"Feinstaub: {pm10} µg/m³ (KRITISCH)")
        elif pm10 > 35:
            st.warning(f"Feinstaub: {pm10} µg/m³ (Erhöht)")
        else:
            st.success(f"Feinstaub: {pm10} µg/m³ (Gut)")
    else:
        st.error("Verbindungsfehler!")

st.caption("Daten: wttr.in & Open-Meteo")
