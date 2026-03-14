import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

def hole_wetter():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        curr = res['current']
        temp, code = curr['temperature_2m'], curr['weather_code']
        emoji, desc = "🌡️", "Unbekannt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [45, 48]: emoji, desc = "🌫️", "Nebel"
        elif code in [51, 53, 55, 61, 63, 65]: emoji, desc = "🌧️", "Regen"
        else: emoji, desc = "☁️", "Bedeckt"
        return {"temp": temp, "emoji": emoji, "desc": desc}
    except: return None

def hole_luft():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone"
        res = requests.get(url, timeout=5).json()
        return {"ozon": res['current']['ozone'], "pm10": res['current']['pm10']}
    except: return None

def hole_fussball(team_id, team_name):
    try:
        # Versuch 1: Über das nächste Spiel
        res = requests.get(f"https://api.openligadb.de/getnextmatchbyleagueteam/ch1/{team_id}", timeout=3).json()
        if not res or 'team1' not in res:
            # Versuch 2: Über die gesamte Spieltagsliste (Fallback)
            res_all = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=3).json()
            for m in res_all:
                if team_name in m['team1']['teamName'] or team_name in m['team2']['teamName']:
                    if not m['matchIsFinished']:
                        res = m
                        break
        
        if res:
            t1, t2 = res['team1']['shortName'], res['team2']['shortName']
            dt = res['matchDateTime'].split('T')
            zeit = dt[1][:5]
            datum = dt[0].split('-')[2] + "." + dt[0].split('-')[1] + "."
            
            # Resultat-Check (falls es schon läuft)
            if res.get('matchResults'):
                r = res['matchResults'][-1]
                return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} (LIVE/Endstand)"
            
            prefix = "Heute" if datum == datetime.now().strftime('%d.%m.') else datum
            return f"{prefix}: {t1} vs. {t2} ({zeit} Uhr)"
        
        return "Kein Spiel gefunden"
    except:
        return "Daten aktuell nicht abrufbar"

# --- ANZEIGE ---
st.markdown("<h1 style='text-align: center; color: #00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if st.button('AKTUALISIEREN') or 'w' not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball(128, "Basel")
    st.session_state.yb = hole_fussball(122, "Young Boys")

w, l = st.session_state.w, st.session_state.l
if w:
    col1, col2 = st.columns(2)
    col1.metric("Temperatur", f"{w['emoji']} {w['temp']} °C")
    col2.write(f"Wetter: **{w['desc']}**")

if l:
    st.divider()
    if l['ozon'] > 120: st.error(f"Ozon: {l['ozon']} µg/m³ (Hoch)")
    else: st.success(f"Ozon: {l['ozon']} µg/m³ (Gut)")
    if l['pm10'] > 50: st.error(f"Feinstaub: {l['pm10']} µg/m³ (Hoch)")
    else: st.success(f"Feinstaub: {l['pm10']} µg/m³ (Gut)")

st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔵🔴 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")

st.caption(f"Update: {datetime.now().strftime('%H:%M')} | Daten: Open-Meteo & OpenLigaDB")
