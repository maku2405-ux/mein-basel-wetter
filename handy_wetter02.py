import streamlit as st
import requests
from datetime import datetime

# 1. Seiteneinstellungen
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

# 2. Daten-Funktionen
def hole_wetter():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=47.5584&longitude=7.5733&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()
        curr = res["current"]
        temp, code = curr["temperature_2m"], curr["weather_code"]
        emoji, desc = "🌡️", "Bedeckt"
        if code == 0: emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]: emoji, desc = "🌤️", "Klar"
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
        url = "https://api.openligadb.de/getmatchdata/ch1/2025"
        spiele = requests.get(url, timeout=5).json()
        for m in spiele:
            if team_suche in m["team1"]["teamName"] or team_suche in m["team2"]["teamName"]:
                if not m["matchIsFinished"]:
                    t1, t2 = m["team1"]["shortName"], m["team2"]["shortName"]
                    dt = m["matchDateTime"].split('T')
                    datum = dt[0].split('-')[2] + "." + dt[0].split('-')[1] + "."
                    uhrzeit = dt[1][:5]
                    if m["matchResults"]:
                        r = m["matchResults"][-1]
                        return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} (LIVE)"
                    prefix = "Heute" if datum == datetime.now().strftime("%d.%m.") else datum
                    return f"{prefix}: {t1} vs. {t2} ({uhrzeit} Uhr)"
        return "Kein Spiel gefunden"
    except: return "⚠️ Verbindung klemmt"

# 3. Anzeige
st.markdown("<h1 style='text-align:center;color:#00529F;'>Basler Luftqualität</h1>", unsafe_allow_html=True)

if st.button("AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball("Basel")
    st.session_state.yb = hole_fussball("Young Boys")

w, l = st.session_state.w, st.session_state.l
if w:
    c1, c2 = st.columns(2)
    c1.metric("Temp", f"{w['emoji']} {w['temp']} °C")
    c2.write(f"Wetter: **{w['desc']}**")

if l:
    st.divider()
    if l["ozon"] > 120: st.error(f"Ozon: {l['ozon']} µg/m³")
    else: st.success(f"Ozon: {l['ozon']} µg/m³ (Gut)")
    if l["pm10"] > 50: st.error(f"Feinstaub: {l['pm10']} µg/m³")
    else: st.success(f"Feinstaub: {l['pm10']} µg/m³ (Gut)")

st.divider()
st.subheader("⚽ Fussball-Ticker")
st.write(f"🔵🔴 **FCB:** {st.session_state.fcb}")
st.write(f"🟡⚫ **YB:** {st.session_state.yb}")

st.caption(f"Update: {datetime.now().strftime('%H:%M')} | Open-Meteo & OpenLigaDB")
