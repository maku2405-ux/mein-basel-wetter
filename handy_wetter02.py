import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT = 47.5584
LON = 7.5733


# -------------------------
# Hilfsfunktionen
# -------------------------

def pollen_status(wert):

    if wert < 10:
        return "🟢 Niedrig"
    elif wert < 50:
        return "🟡 Achtung"
    else:
        return "🔴 Hoch"


def luft_status(wert):

    if wert < 40:
        return f"🟢 {wert} (Gut)"
    elif wert < 80:
        return f"🟡 {wert} (Mittel)"
    else:
        return f"🔴 {wert} (Hoch)"


def rhein_emoji(temp):

    if temp < 18:
        return "🥶"
    elif 20 <= temp <= 22:
        return "😊"
    elif temp > 22:
        return "🥵"
    else:
        return "🙂"


def wetter_beschreibung(code):

    if code == 0:
        return "☀️", "Sonnig"
    elif code in [1, 2, 3]:
        return "🌤️", "Leicht bewölkt"
    elif code in [45, 48]:
        return "🌫️", "Neblig"
    elif code in [51, 53, 55, 61, 63, 65]:
        return "🌧️", "Regen"
    elif code in [71, 73, 75]:
        return "❄️", "Schnee"
    else:
        return "☁️", "Bedeckt"


# -------------------------
# Wetter + Rhein
# -------------------------

def hole_wetter_und_rhein():

    try:

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LAT}&longitude={LON}"
            "&current=temperature_2m,weather_code"
            "&timezone=Europe%2FBerlin"
        )

        res = requests.get(url, timeout=10).json()

        curr = res["current"]

        temp = curr["temperature_2m"]
        code = curr["weather_code"]

        emoji, desc = wetter_beschreibung(code)

        # Beispiel Rheinwert (falls keine Hydrodaten API)
        rhein_temp = 8.4

        return {
            "temp": temp,
            "emoji": emoji,
            "desc": desc,
            "rhein": rhein_temp
        }

    except:
        return None


# -------------------------
# Luft + Pollen
# -------------------------

def hole_luft_und_pollen():

    try:

        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={LAT}&longitude={LON}"
            "&current=pm10,ozone,birch_pollen,grass_pollen"
        )

        res = requests.get(url, timeout=10).json()

        curr = res["current"]

        return {
            "ozon": curr["ozone"],
            "pm10": curr["pm10"],
            "birke": curr["birch_pollen"],
            "gras": curr["grass_pollen"]
        }

    except:
        return None


# -------------------------
# Fussball
# -------------------------

def hole_team_ticker(team_id):

    try:

        url = "https://api.openligadb.de/getmatchdata/ch1"

        spiele = requests.get(url, timeout=10).json()

        jetzt = datetime.now()

        for spiel in spiele:

            if (
                spiel["team1"]["teamID"] == team_id
                or spiel["team2"]["teamID"] == team_id
            ):

                zeit = datetime.strptime(
                    spiel["matchDateTime"],
                    "%Y-%m-%dT%H:%M:%S"
                )

                t1 = spiel["team1"]["shortName"]
                t2 = spiel["team2"]["shortName"]

                if spiel["matchIsFinished"] is False and spiel["matchResults"]:

                    r = spiel["matchResults"][-1]

                    return f"🔴 LIVE: {t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2}"

                if zeit.date() >= jetzt.date():

                    prefix = (
                        "Heute"
                        if zeit.date() == jetzt.date()
                        else zeit.strftime("%d.%m.")
                    )

                    return f"{prefix}: {t1} vs {t2} ({zeit.strftime('%H:%M')})"

        return "Kein Spiel geplant"

    except:

        return "Daten laden..."


# -------------------------
# UI
# -------------------------

st.markdown(
    "<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>",
    unsafe_allow_html=True
)


if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:

    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()

    st.session_state.fcb = hole_team_ticker(128)
    st.session_state.yb = hole_team_ticker(122)


# -------------------------
# Wetter Anzeige
# -------------------------

w = st.session_state.w

if w:

    rhein_e = rhein_emoji(w["rhein"])

    c1, c2 = st.columns(2)

    c1.metric(
        "Luft",
        f"{w['emoji']} {w['temp']}°C",
        f"Aktuell: {w['desc']}"
    )

    c2.metric(
        "Rhein",
        f"{rhein_e} {w['rhein']}°C"
    )


# -------------------------
# Luftqualität
# -------------------------

l = st.session_state.l

if l:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.write("🌳 **Pollen**")

        st.write(f"Birke: {pollen_status(l['birke'])}")
        st.write(f"Gräser: {pollen_status(l['gras'])}")

    with col2:

        st.write("💨 **Luftqualität**")

        st.write(f"Ozon: {luft_status(l['ozon'])}")
        st.write(f"Feinstaub PM10: {luft_status(l['pm10'])}")


# -------------------------
# Fussball
# -------------------------

st.divider()

st.subheader("⚽ Fussball-Ticker")

st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")


st.caption(
    f"Stand: {datetime.now().strftime('%H:%M')} | Basel App 2026"
)
