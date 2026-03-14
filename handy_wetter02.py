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
    except:
        return None

def hole_live_ticker(team_name):
    try:
        # Wir fragen die Saison 2025 ab (da sie bis Sommer 2026 läuft)
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        jetzt = datetime.now()
        aktuelles_spiel = None

        # Wir suchen das Spiel, das zeitlich am nächsten bei HEUTE (15.03.2026) liegt
        for spiel in res:
            spiel_zeit = datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                # Wenn das Spiel heute ist oder in der Zukunft liegt, nehmen wir dieses
                if spiel_zeit.date() >= jetzt.date():
                    aktuelles_spiel = spiel
                    break
                else:
                    # Ansonsten merken wir uns das letzte Spiel als Fallback
                    aktuelles_spiel = spiel

        if aktuelles_spiel:
            s = aktuelles_spiel
            t1, t2 = s['team1']['shortName'], s['team2']['shortName']
            
            # Fall 1: Spiel ist fertig
            if s['matchIsFinished']:
                res_fin = s['matchResults'][0]
                return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
            
            # Fall 2: Spiel läuft gerade (Live-Ticker)
            elif s['matchResults'] and not s['matchIsFinished']:
                res_live = s['matchResults'][-1]
                return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
            
            # Fall 3: Spiel ist in der Zukunft/Heute geplant
            else:
                termin = s['matchDateTime'].split('T')
                datum_raw = termin[0].split('-')
                datum_formatiert = f"{datum_raw[2]}.{datum_raw[1]}."
                uhrzeit = termin[1][:5]
                if datum_formatiert == jetzt.strftime("%d.%m."):
                    return f"{t1} vs. {t2} (Heute, {uhrzeit} Uhr)"
                else:
                    return f"{t1} vs. {t2} ({datum_formatiert} {uhrzeit} Uhr)"
        
        return "Keine aktuellen Spieldaten"
    except:
        return "Daten aktuell nicht verfügbar"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

# Daten laden oder aktualisieren
if 'daten' not in st.session_state:
    st.session_state.daten = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

d = st.session_state.daten

if d:
    # Wetter & Temperatur
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{d['temp']} °C")
    col2.write(f"Wetter: **{d['desc']}**")
    
    st.divider()
    
    # Luftqualität (Schweizer Grenzwerte)
    if d['ozon'] > 120:
        st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else:
        st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50:
        st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else:
        st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    # Fussball Ticker
    st.divider()
    st.subheader("⚽ Fussball-Update")
    
    fcb_ticker = hole_live_ticker("Basel")
    yb_ticker = hole_live_ticker("Young Boys")
    
    st.write(f"🔵🔴 **FC Basel:** {fcb_ticker}")
    st.write(f"🟡⚫ **Young Boys:** {yb_ticker}")

else:
    st.error("Verbindungsfehler. Bitte erneut aktualisieren.")

# Footer mit Zeitstempel
st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')} | Daten: Open-Meteo & OpenLigaDB")
