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

def hole_live_ticker(team_name):
    try:
        # Abfrage der aktuellen Saison
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        heute = datetime.now().date()
        
        naechstes = None
        letztes = None

        # Wir sortieren die Spiele nach Zeit
        spiele = sorted(res, key=lambda x: x['matchDateTime'])

        for spiel in spiele:
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                spiel_zeit = datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S").date()
                
                if spiel_zeit >= heute:
                    if not naechstes:
                        naechstes = spiel
                else:
                    letztes = spiel

        # Entscheidung: Was zeigen wir an?
        anzeige_spiel = naechstes if naechstes else letztes

        if anzeige_spiel:
            s = anzeige_spiel
            t1 = s['team1']['shortName']
            t2 = s['team2']['shortName']
            spiel_zeit_obj = datetime.strptime(s['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            uhrzeit = spiel_zeit_obj.strftime("%H:%M")
            datum = spiel_zeit_obj.strftime("%d.%m.")

            # Falls das Spiel läuft oder fertig ist
            if s['matchIsFinished'] or s['matchResults']:
                # Wir suchen das Endergebnis (meistens das erste in der Liste 'matchResults')
                res_list = s.get('matchResults', [])
                if res_list:
                    # Wir nehmen das Resultat mit der höchsten ID (meistens das Endergebnis)
                    final = res_list[-1]
                    punkte1 = final['pointsTeam1']
                    punkte2 = final['pointsTeam2']
                    status = "(Endstand)" if s['matchIsFinished'] else "🔴 LIVE"
                    return f"{t1} {punkte1}:{punkte2} {t2} {status}"
            
            # Falls es in der Zukunft liegt
            return f"{t1} vs. {t2} ({datum} um {uhrzeit} Uhr)"
        
        return "Keine Spieldaten"
    except Exception as e:
        return "Daten aktuell nicht verfügbar"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if 'daten' not in st.session_state:
    st.session_state.daten = hole_daten()

if st.button('AKTUALISIEREN'):
    st.session_state.daten = hole_daten()

d = st.session_state.daten

if d:
    # Wetter-Emoji Logik
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
    
    if d['ozon'] > 120: st.error(f"Ozon: {d['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {d['ozon']} µg/m³ (Gut)")
    
    if d['pm10'] > 50: st.error(f"Feinstaub: {d['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {d['pm10']} µg/m³ (Gut)")

    st.divider()
    st.subheader("⚽ Fussball-Update")
    st.write(f"🔵🔴 **FC Basel:** {hole_live_ticker('Basel')}")
    st.write(f"🟡⚫ **Young Boys:** {hole_live_ticker('Young Boys')}")

else:
    st.error("Fehler beim Laden.")

st.caption(f"Stand: {(datetime.now() + timedelta(hours=0)).strftime('%d.%m.%Y %H:%M')} | Basel App")
