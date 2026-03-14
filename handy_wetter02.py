import streamlit as st
import requests

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
        # Holt alle Spiele der Schweizer Liga 2025/26
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        for spiel in reversed(res):
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                t1 = spiel['team1']['shortName']
                t2 = spiel['team2']['shortName']
                
                if spiel['matchIsFinished']:
                    res_fin = spiel['matchResults'][0]
                    return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
                elif spiel['matchResults']: 
                    res_live = spiel['matchResults'][-1]
                    return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
                else:
                    termin = spiel['matchDateTime'].split('T')
                    datum = termin[0].split('-')[2] + "." + termin[0].split('-')[1] + "."
                    uhrzeit = termin[1][:5]
                    return f"{t1} vs. {t2} ({datum} {uhrzeit} Uhr)"
        return "Kein Spiel gefunden"
    except: return "Daten laden..."

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten' not in st.session_state:
    st.session_state.daten = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

d = st.session_state.daten
if d:
    # Wetter & Luft
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{d['temp']} °C")
    col2.write(f"Wetter: **{d['desc']}**")
    
    st.divider()
    
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    # --- FUSSBALL UPDATE GANZ UNTEN ---
    st.divider()
    st.subheader("⚽ Fussball-Ticker")
    
    fcb_ticker = hole_live_ticker("Basel")
    yb_ticker = hole_live_ticker("Young Boys")
    
    st.write(f"🔵🔴 **FC Basel:** {fcb_ticker}")
    st.write(f"🟡⚫ **Young Boys:** {yb_ticker}")
else:
    st.error("Daten konnten nicht geladen werden.")

st.caption("Daten: wttr.in, Open-Meteo & OpenLigaDB")
    col1.metric("Temperatur", f"{emoji} {d['temp']} °C")
    col2.write(f"Wetter in Basel: **{d['desc']}**")
    
    st.divider()
    
    # Luftqualität
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    # Fussball Sektion
    st.divider()
    st.subheader("⚽ Fussball-Update")
    
    # Wir rufen die Ticker-Funktion für beide Teams auf
    fcb_info = hole_live_ticker("Basel")
    yb_info = hole_live_ticker("Young Boys")
    
    st.write(f"🔴🔵 **FC Basel:** {fcb_info}")
    st.write(f"🟡⚫ **Young Boys:** {yb_info
