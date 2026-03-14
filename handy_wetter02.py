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
        # Abfrage der Saison 2025/26
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        
        # Heutiges Datum als fixer Filter (15.03.2026)
        heute = datetime(2026, 3, 15).date()
        
        zukuenftige_spiele = []

        # Schritt 1: Alle Spiele finden, die heute oder in der Zukunft liegen
        for spiel in res:
            spiel_zeit = datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                if spiel_zeit.date() >= heute:
                    zukuenftige_spiele.append(spiel)
        
        # Schritt 2: Das Spiel anzeigen, das als Nächstes kommt
        if zukuenftige_spiele:
            s = zukuenftige_spiele[0] # Das erste Spiel ab heute
            t1, t2 = s['team1']['shortName'], s['team2']['shortName']
            spiel_zeit_obj = datetime.strptime(s['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            uhrzeit = spiel_zeit_obj.strftime("%H:%M")
            datum = spiel_zeit_obj.strftime("%d.%m.")

            if s['matchIsFinished']:
                res_fin = s['matchResults'][0]
                return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
            elif s['matchResults']:
                res_live = s['matchResults'][-1]
                return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
            else:
                return f"{t1} vs. {t2} ({datum} um {uhrzeit} Uhr)"
        
        # Fallback: Wenn kein zukünftiges Spiel da ist, nimm das letzte vergangene
        for spiel in reversed(res):
            if team_name in spiel['team1']['teamName'] or team_name in spiel['team2']['teamName']:
                t1, t2 = spiel['team1']['shortName'], spiel['team2']['shortName']
                res_fin = spiel['matchResults'][0] if spiel['matchResults'] else {"pointsTeam1":0, "pointsTeam2":0}
                return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Letztes Spiel)"
        
        return "Keine Spieldaten"
    except:
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
    if any(word in d_lower for word in ["sonne", "heiter", "klar"]): emoji = "☀️"
    elif any(word in d_lower for word in ["wolke", "bedeckt", "bewölkt"]): emoji = "☁️"
    elif any(word in d_lower for word in ["regen", "schauer"]): emoji = "🌧️"
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

# Zeitstempel (+1h Korrektur für die Anzeige)
aktuelle_zeit = datetime.now() + timedelta(hours=1)
st.caption(f"Stand: {aktuelle_zeit.strftime('%d.%m.%Y %H:%M')} | Basel App")
