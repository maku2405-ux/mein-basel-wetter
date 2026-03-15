import streamlit as st
import requests
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

def hole_wetter_und_rhein():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        rhein_temp = 8.4  
        curr = res['current']
        temp, code = curr['temperature_2m'], curr['weather_code']
        emoji, desc = "☁️", "Bedeckt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        return {"temp": temp, "emoji": emoji, "desc": desc, "rhein": rhein_temp}
    except Exception:
        return None

def hole_luft_und_pollen():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone,birch_pollen,grass_pollen"
        res = requests.get(url, timeout=5).json()
        curr = res['current']
        return {"ozon": curr['ozone'], "pm10": curr['pm10'], "birke": curr['birch_pollen'], "gras": curr['grass_pollen']}
    except Exception:
        return None

def hole_fussball_ticker(suche_name):
    try:
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        jetzt = datetime.now()
        spiele_team = []
        for spiel in res:
            if suche_name.lower() in spiel['team1']['teamName'].lower() or suche_name.lower() in spiel['team2']['teamName'].lower():
                match_date = spiel['matchDateTime'].split(".")[0]
                spiel_zeit = datetime.strptime(match_date, "%Y-%m-%dT%H:%M:%S")
                spiele_team.append((spiel_zeit, spiel))
        
        if not spiele_team:
            return "Kein Spiel gefunden"

        spiele_team.sort(key=lambda x: abs((x[0] - jetzt).total_seconds()))
        naechstes_zeit, spiel = spiele_team[0]
        t1_s, t2_s = spiel['team1']['shortName'], spiel['team2']['shortName']
        res_list = spiel['matchResults']
        
        p1 = res_list[-1]['pointsTeam1'] if res_list else 0
        p2 = res_list[-1]['pointsTeam2'] if res_list else 0

        if not spiel['matchIsFinished']:
            if naechstes_zeit <= jetzt <= naechstes_zeit + timedelta(hours=2):
                return f"🔴 LIVE: {t1_s} {p1}:{p2} {t2_s}"
            tag = "Heute" if naechstes_zeit.date() == jetzt.date() else naechstes_zeit.strftime("%d.%m.")
            return f"⏳ {tag}: {t1_s} vs. {t2_s} ({naechstes_zeit.strftime('%H:%M')} Uhr)"
        else:
            return f"FT: {t1_s} {p1}:{p2} {t2_s}"
    except Exception:
        return "Daten aktuell nicht verfügbar"

def hole_wappen():
    try:
        url = "https
