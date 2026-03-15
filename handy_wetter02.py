import streamlit as st
import requests
from datetime import datetime, timedelta

# -----------------------------
# 1. Seiteneinstellungen
# -----------------------------
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

# -----------------------------
# 2. Daten-Funktionen
# -----------------------------
def hole_wetter():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        curr = res["current"]
        temp, code = curr["temperature_2m"], curr["weather_code"]
        
        # Wetter-Emoji Zuordnung
        emoji, desc = "🌡️", "Bedeckt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        return {"temp": temp, "emoji": emoji, "desc": desc}
    except: return None

def hole_luft():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
        res = requests.get(url, timeout=5).json()
        return {"ozon": res["current"]["ozone"], "pm10": res["current"]["pm10"]}
    except: return None

def hole_fussball(team_suche):
    try:
        # Wir laden die Saisonliste
        url = "https://api.openligadb.de/getmatchdata/ch1/2025"
        spiele = requests.get(url, timeout=5).json()
        
        jetzt = datetime.now()
        
        # Wir suchen rückwärts, um das aktuellste Spiel zu finden
        for m in reversed(spiele):
            t1_name = m["team1"]["teamName"]
            t2_name = m["team2"]["teamName"]
            
            if team_suche in t1_name or team_suche in t2_name:
                # Zeitstempel umwandeln
                m_time = datetime.fromisoformat(m["matchDateTime"].replace('Z', ''))
                
                # Wir nehmen das Spiel, wenn es heute ist oder maximal 1 Tag her ist 
                # (damit wir das Resultat vom Abend noch sehen)
                if m_time.date() >= (jetzt.date() - timedelta(days=1)):
                    t1, t2 = m["team1"]["shortName"], m["team2"]["shortName"]
                    dt = m["matchDateTime"].split('T')
                    datum = dt[0].split('-')[2] + "." + dt[0].split('-')
