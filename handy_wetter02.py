import streamlit as st
import requests
from datetime import datetime

# Seiteneinstellungen
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT = 47.5584
LON = 7.5733

# -----------------------
# Hilfsfunktionen
# -----------------------

def pollen_farbe(wert):
    if wert < 10:
        return "🟢 Niedrig"
    elif wert < 50:
        return "🟡 Achtung"
    else:
        return "🔴 Hoch"


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


# -----------------------
# Wetter + Rhein
# -----------------------

def hole_wetter_und_rhein():

    try:

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LAT}&longitude={LON}"
            "&current=temperature_2m,weather_code"
            "&timezone=Europe%2FBerlin"
        )

        res = requests.get(url, timeout=10)
        data = res.json()

        curr = data["current"]

        temp = curr["temperature_2m"]
        code = curr["weather_code"]

        emoji, desc = wetter_beschreibung(code)

        # Rhein Temperatur (Fallback)
        rhein_temp = 8.4

        return {
            "temp": temp,
            "emoji": emoji,
            "desc": desc,
            "rhein": rhein_temp
        }

    except Exception:
        return None


# -----------------------
# Luft + Pollen
# -----------------------

def hole_luft_und_pollen():

    try:

        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={LAT}&longitude={LON}"
            "&current=pm10,ozone,birch_pollen,grass_pollen"
        )

        res = requests.get(url, timeout=10)
        data = res.json()

        curr = data["current"]

        return {
            "ozon": curr["ozone"],
            "pm10": curr["pm10"],
            "birke": curr["birch_pollen"],
            "gras": curr["grass_pollen"]
        }

    except Exception:
        return None


# -----------------------
# Fussball
# -----------------------

def hole_fcb_ticker(team_id):

    try:

        url = "https://api.openligadb.de/getmatchdata/ch1/2025"

        res = requests.get(url, timeout=10).json()

        jetzt = datetime.now()

        for spiel in res:

            if (
                team_id == spiel["team1"]["teamID"]
                or team_id == spiel["team2"]["teamID"]
            ):

                zeit = datetime.strptime(
                    spiel["matchDateTime"],
                    "%Y-%m-%dT%H:%M:%S"
                )

                if zeit.date() >= jetzt.date():

                    t1 = spiel["team1"]["shortName"]
                    t2 = spiel["team2"]["shortName"]

                    if spiel["matchResults"] and not spiel["matchIsFinished"]:

                        r = spiel["matchResults"][-1]

                        return f"🔴 LIVE: {t1} {r['pointsTeam1']}:{r['pointsTeam2']} {t2}"

                    prefix = "Heute" if zeit.date() == jetzt.date() else zeit.strftime("%d.%m.")

                    return f"{prefix}: {t1} vs {t2} ({zeit.strftime('%H:%M')} Uhr)"

        return "Kein Spiel geplant"

    except Exception:
        return "Daten laden..."


# -----------------------
# UI
# -----------------------

st.markdown(
    "<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>",
    unsafe_allow_html=True
)


if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:

    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()

    st.session_state.fcb = hole_fcb_ticker(128)
    st.session_state.yb = hole_fcb_ticker(122)


# -----------------------
# Wetter
# -----------------------

w = st.session_state.w

if w:

    c1, c2 = st.columns(2)

    c1.metric(
        "Luft",
        f"{w['emoji']} {w['temp']}°C",
        f"Aktuell: {w['desc']}"
    )

    c2.metric(
        "Rhein",
        f"🌊 {w['rhein']}°C"
    )


# -----------------------
# Luftqualität + Pollen
# -----------------------

l = st.session_state.l

if l:

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.write("🌳 **Pollen**")

        st.write(f"Birke: {pollen_farbe(l['birke'])}")
        st.write(f"Gräser: {pollen_farbe(l['gras'])}")

    with col2:

        st.write("💨 **Luftqualität**")

        if l["ozon"] < 80:
            st.write(f"Ozon: 🟢 {l['ozon']} (Gut)")
        elif l["ozon"] < 120:
            st.write(f"Ozon: 🟡 {l['ozon']} (Mittel)")
        else:
            st.write(f"Ozon: 🔴 {l['ozon']} (Hoch)")


# -----------------------
# Fussball
# -----------------------

st.divider()

st.subheader("⚽ Fussball-Ticker")

st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **Young Boys:** {st.session_state.yb}")


st.caption(
    f"Stand: {datetime.now().strftime('%H:%M')} | Basel App 2026"
)
