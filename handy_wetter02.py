import streamlit as st
import requests
import datetime

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
        # Schweizer Super League Daten für die aktuelle Saison
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        jetzt = datetime.datetime.now()
        
        # Alle Spiele dieses Teams filtern
        team_spiele = [s for s in res if team_name in s['team1']['teamName'] or team_name in s['team2']['teamName']]
        
        # Sortieren nach Datum, um das aktuellste zu finden
        team_spiele.sort(key=lambda x: x['matchDateTime'])
        
        aktuelles_spiel = None
        for spiel in team_spiele:
            spiel_zeit = datetime.datetime.strptime(spiel['matchDateTime'], "%Y-%m-%dT%H:%M:%S")
            # Wir suchen das Spiel, das noch nicht fertig ist ODER heute stattfindet
            if not spiel['matchIsFinished'] or spiel_zeit.date() >= jetzt.date():
                aktuelles_spiel = spiel
                break
        
        if not aktuelles_spiel:
            aktuelles_spiel = team_spiele[-1] # Letztes verfügbares Spiel als Backup

        t1 = aktuelles_spiel['team1']['shortName']
        t2 = aktuelles_spiel['team2']['shortName']
        
        if aktuelles_spiel['matchIsFinished']:
            res_fin = aktuelles_spiel['matchResults'][0]
            return f"{t1} {res_fin['pointsTeam1']}:{res_fin['pointsTeam2']} {t2} (Endstand)"
        elif aktuelles_spiel['matchResults']:
            res_live = aktuelles_spiel['matchResults'][-1]
            return f"🔴 LIVE: {t1} {res_live['pointsTeam1']}:{res_live['pointsTeam2']} {t2}"
        else:
            termin = aktuelles_spiel['matchDateTime']
            datum = termin.split('T')[0].split('-')[2] + "." + termin.split('T')[0].split('-')[1] + "."
            zeit = termin.split('T')[1][:5]
            return f"{t1} vs. {t2} ({datum} um {zeit} Uhr)"
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
    desc_l = d['desc'].lower()
    if "sonne" in desc_l or "heiter" in desc_l: emoji = "☀️"
    elif "wolke" in desc_l or "bewölkt" in desc_l: emoji = "☁️"
    elif "regen" in desc_l: emoji = "🌧️"

    # Layout mit Spalten
    col1, col2 = st.columns(2)
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
