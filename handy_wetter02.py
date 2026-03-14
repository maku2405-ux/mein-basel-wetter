import streamlit as st
import requests
from datetime import datetime, timedelta

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
    except:
        return None

def hole_live_ticker(suchname):
    try:
        # Abfrage der aktuellen Saison 2025/26
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        
        # Das heutige Datum (15.03.2026)
        jetzt = datetime.now()
        
        spiele_liste = []

        # Wir filtern die Liste: Nur Spiele, die HEUTE oder in der ZUKUNFT liegen
        for spiel in res:
            spiel_zeit = datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            if suchname in spiel['team1']['teamName'] or suchname in spiel['team2']['teamName']:
                # Filter: Alles vor heute fliegt raus!
                if spiel_zeit.date() >= jetzt.date():
                    spiele_liste.append(spiel)
        
        # Sortieren, damit das zeitlich nächste Spiel oben steht
        spiele_liste.sort(key=lambda x: x['matchDateTime'])

        if spiele_liste:
            s = spiele_liste[0] # Das absolut nächste Spiel
            t1 = s['team1']['shortName']
            t2 = s['team2']['shortName']
            spiel_zeit_obj = datetime.strptime(s['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            uhrzeit = spiel_zeit_obj.strftime("%H:%M")
            datum = spiel_zeit_obj.strftime("%d.%m.")

            # Live-Ticker Logik
            if s['matchResults'] and not s['matchIsFinished']:
                res_live = s['matchResults'][-1]
                return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
            elif s['matchIsFinished']:
                res_fin = s['matchResults'][0]
                return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
            else:
                return f"{t1} vs. {t2} ({datum} um {uhrzeit} Uhr)"
        
        return "Kein Spiel in den nächsten Tagen"
    except:
        return "Daten-Update folgt..."

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten' not in st.session_state:
    st.session_state.daten = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

d = st.session_state.daten

if d:
    # Emoji-Logik
    emoji = "🌡️"
    d_lower = d['desc'].lower()
    if any(x in d_lower for x in ["sonne", "heiter", "klar"]): emoji = "☀️"
    elif any(x in d_lower for x in ["wolke", "bedeckt", "bewölkt"]): emoji = "☁️"
    elif any(x in d_lower for x in ["regen", "schauer"]): emoji = "🌧️"
    elif "gewitter" in d_lower: emoji = "⛈️"

    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{emoji} {d['temp']} °C")
    col2.write(f"Wetter: **{d['desc']}**")
    
    st.divider()
    
    # Luftqualität
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    # Fussball
    st.divider()
    st.subheader("⚽ Fussball-Update")
    st.write(f"🔵🔴 **FC Basel:** {hole_live_ticker('FC Basel 1893')}")
    st.write(f"🟡⚫ **Young Boys:** {hole_live_ticker('BSC Young Boys')}")

else:
    st.error("Ladefehler...")

st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Basel App")
