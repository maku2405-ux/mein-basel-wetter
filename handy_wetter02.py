import streamlit as st
import requests
from datetime import datetime, timedelta

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
        url = "[api.openligadb.de](https://api.openligadb.de/getmatchdata/ch1/2025)"
        spiele = requests.get(url, timeout=5).json()
        jetzt_datum = datetime.now().strftime("%Y-%m-%d")
        
        naechstes = None
        for m in spiele:  # Vorwärts statt rückwärts
            if team_suche in m["team1"]["teamName"] or team_suche in m["team2"]["teamName"]:
                m_date = m["matchDateTime"].split('T')[0]
                
                # Spiel ist heute oder in der Zukunft
                if m_date >= jetzt_datum:
                    naechstes = m
                    break  # Erstes zukünftiges Spiel gefunden
                
                # Oder: Spiel läuft noch (nicht beendet)
                if not m.get("matchIsFinished", True):
                    naechstes = m
                    break
        
        if not naechstes:
            return "Kein Spiel gefunden"
        
        m = naechstes
        t1, t2 = m["team1"]["shortName"], m["team2"]["shortName"]
        m_date = m["matchDateTime"].split('T')[0]
        uhrzeit = m["matchDateTime"].split('T')[1][:5]
        tag = m_date.split('-')[2] + "." + m_date.split('-')[1] + "."
        
        if m["matchResults"]:
            r = m["matchResults"][-1]
            status = "LIVE" if not m["matchIsFinished"] else "Endstand"
            return f"{t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2} ({status})"
        
        prefix = "Heute" if m_date == jetzt_datum else tag
        return f"{prefix}: {t1} vs. {t2} ({uhrzeit} Uhr)"
        
    except Exception as e:
        return f"⚠️ Fehler: {str(e)}"


# 3. Anzeige
st.markdown("<h1 style='text-align:center;color:#00529F;'>🇨🇭 Basler Luftqualität</h1>", unsafe_allow_html=True)

if st.button("AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()
    st.session_state.fcb = hole_fussball("Basel")
    st.session_state.yb = hole_fussball("Young Boys")

w, l = st.session_state.w, st.session_state.l
if w:
    c1, c2 = st.columns(2)
    c1.metric("Temperatur", f"{w['emoji']} {w['temp']} °C")
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
