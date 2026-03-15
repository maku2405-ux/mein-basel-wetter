import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basel Live: Wetter & Fussball", page_icon="🔴🔵")

# Dein API-Token (Sicher aufbewahren!)
API_TOKEN = "b63726db10d14e4baf5287dbb338bfb3"

# 2. Titel
st.title("🏘️ Mein Basel: Wetter & Live-Sport")

# 3. Wetter & Rhein (Statische Werte aus deinem Screenshot)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Temperatur Basel", value="5.0 °C")
    st.write("☁️ **Leicht bewölkt**")
with col2:
    st.metric(label="Rhein Temperatur", value="8.4 °C")
    st.write("🌊 **Status:** Ziemlich frisch!")

st.divider()

# 4. Live Fussball Daten von football-data.org
st.header("⚽ Live-Resultate: Super League")

def get_live_scores():
    # ID 2073 steht für die Schweizer Super League
    url = "https://api.football-data.org/v4/competitions/2073/matches"
    headers = {"X-Auth-Token": API_TOKEN}
    
    # Wir filtern nach den Spielen von heute (2026-03-15)
    today = datetime.now().strftime('%Y-%m-%d')
    params = {"dateFrom": today, "dateTo": today}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data.get("matches", [])
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return []

matches = get_live_scores()

if matches:
    for match in matches:
        home_team = match['homeTeam']['shortName']
        away_team = match['awayTeam']['shortName']
        home_score = match['score']['fullTime']['home']
        away_score = match['score']['fullTime']['away']
        status = match['status']
        
        # Schöne Anzeige der Spiele
        with st.expander(f"🏟️ {home_team} vs. {away_team}", expanded=True):
            if status == "TIMED":
                st.write(f"🕒 Anpfiff: {match['utcDate'][11:16]} UTC")
                st.write("**Spiel hat noch nicht begonnen**")
            else:
                st.subheader(f"{home_score} : {away_score}")
                st.caption(f"Status: {status}")
            
            # Spezieller Hinweis für FCB-Fans
            if "Basel" in home_team or "Basel" in away_team:
                st.write("🔴🔵 **Hopp FCB!**")
else:
    st.info("Für heute sind aktuell keine weiteren Spiele in der Super League gelistet.")

st.divider()

# 5. Pollen & Luft
st.subheader("🌳 Umwelt")
st.write("Birke: **Niedrig** | Gräser: **Niedrig**")
st.write("💨 **Luftqualität:** Gut")

st.caption(f"Letztes Update: {datetime.now().strftime('%H:%M:%S')} | Währungen in CHF")
