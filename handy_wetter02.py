import streamlit as st
import requests
from datetime import datetime

# -----------------------------
# Seiteneinstellungen
# -----------------------------
st.set_page_config(page_title="Basler Luftqualität", page_icon="🇨🇭")

LAT = 47.5584
LON = 7.5733


# -----------------------------
# Wetter
# -----------------------------
def hole_wetter():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,weather_code&timezone=Europe%2FBerlin"
        res = requests.get(url, timeout=5).json()

        curr = res["current"]
        temp = curr["temperature_2m"]
        code = curr["weather_code"]

        emoji, desc = "🌡️", "Unbekannt"

        if code == 0:
            emoji, desc = "☀️", "Sonnig"
        elif code in [1, 2, 3]:
            emoji, desc = "🌤️", "Leicht bewölkt"
        elif code in [45, 48]:
            emoji, desc = "🌫️", "Nebel"
        elif code in [51, 53, 55, 61, 63, 65]:
            emoji, desc = "🌧️", "Regen"
        else:
            emoji, desc = "☁️", "Bedeckt"

        return {"temp": temp, "emoji": emoji, "desc": desc}

    except:
        return None


# -----------------------------
# Luftqualität
# -----------------------------
def hole_luft():
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={LAT}&longitude={LON}&current=pm10,ozone"
        res = requests.get(url, timeout=5).json()

        return {
            "ozon": res["current"]["ozone"],
            "pm10": res["current"]["pm10"],
        }

    except:
        return None


# -----------------------------
# Fussballspiele
# -----------------------------
def hole_fussball(team_suche):
    try:
        url = "https://api.openligadb.de/getmatchdata/ch1/2025"
        spiele = requests.get(url, timeout=5).json()

        jetzt = datetime.now()
        kommende_spiele = []

        for m in spiele:

            t1 = m["team1"]["teamName"]
            t2 = m["team2"]["teamName"]

            if team_suche in t1 or team_suche in t2:

                match_time = datetime.fromisoformat(m["matchDateTime"])

                # nur zukünftige Spiele berücksichtigen
                if match_time >= jetzt:
                    kommende_spiele.append((match_time, m))

        if not kommende_spiele:
            return "Kein kommendes Spiel"

        # nach Datum sortieren
        kommende_spiele.sort(key=lambda x: x[0])

        match_time, m = kommende_spiele[0]

        t1_short = m["team1"]["shortName"]
        t2_short = m["team2"]["shortName"]

        datum = match_time.strftime("%d.%m.")
        uhrzeit = match_time.strftime("%H:%M")

        prefix = "Heute" if datum == jetzt.strftime("%d.%m.") else datum

        return f"{prefix}: {t1_short} vs. {t2_short} ({uhrzeit} Uhr)"

    except:
        return "⚠️ API Problem"


# -----------------------------
# Titel
# -----------------------------
st.markdown(
    "<h1 style='text-align:center;color:#00529F;'>🇨🇭 Basler Luftqualität</h1>",
    unsafe_allow_html=True,
)


# -----------------------------
# Daten laden
# -----------------------------
if st.button("AKTUALISIEREN") or "w" not in st.session_state:

    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()

    st.session_state.fcb = hole_fussball("Basel")
    st.session_state.yb = hole_fussball("Young Boys")


w = st.session_state.w
l = st.session_state.l


# -----------------------------
# Wetter anzeigen
# -----------------------------
if w:

    col1, col2 = st.columns(2)

    col1.metric("Temperatur", f"{w['emoji']} {w['temp']} °C")
    col2.write(f"Wetter: **{w['desc']}**")


# -----------------------------
# Luftqualität anzeigen
# -----------------------------
if l:

    st.divider()

    if l["ozon"] > 120:
        st.error(f"Ozon: {l['ozon']} µg/m³ (Hoch)")
    else:
        st.success(f"Ozon: {l['ozon']} µg/m³ (Gut)")

    if l["pm10"] > 50:
        st.error(f"Feinstaub: {l['pm10']} µg/m³ (Hoch)")
    else:
        st.success(f"Feinstaub: {l['pm10']} µg/m³ (Gut)")


# -----------------------------
# Fussball-Ticker
# -----------------------------
st.divider()
st.subheader("⚽ Fussball-Ticker")

st.write(f"🔵🔴 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")


# -----------------------------
# Footer
# -----------------------------
st.caption(
    f"Update: {datetime.now().strftime('%H:%M')} | Daten: Open-Meteo & OpenLigaDB"
)
