import streamlit as st
import requests
from datetime import datetime
import pytz
from PIL import Image
import base64
from io import BytesIO

# ---------------------------------------------------------
# Bild laden und in Base64 umwandeln
# ---------------------------------------------------------
def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

baselstab = Image.open("baselstab.jpg")
baselstab_b64 = image_to_base64(baselstab)

# ---------------------------------------------------------
# Streamlit Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT = 47.5584
LON = 7.5733

def pollen_status(v):
    if v < 10:
        return "🟢 Niedrig"
    elif v < 50:
        return "🟡 Achtung"
    else:
        return "🔴 Hoch"

def luft_status(v):
    if v < 20:
        return "🟢 {}".format(v)
    elif v < 50:
        return "🟡 {}".format(v)
    else:
        return "🔴 {}".format(v)

def rhein_emoji(temp):
    if temp < 18:
        return "🥶"
    elif 20 <= temp <= 22:
        return "😊"
    else:
        return "🙂"

def wetter_beschreibung(code):
    mapping = {
        0: ("☀️", "Sonnig"),
        1: ("🌤️", "Heiter"),
        2: ("🌤️", "Leicht bewölkt"),
        3: ("☁️", "Wolkig"),
        45: ("🌫️", "Nebel"),
        48: ("🌫️", "Reifnebel"),
        51: ("🌧️", "Leichter Regen"),
        61: ("🌧️", "Regen"),
        95: ("⛈️", "Gewitter")
    }
    return mapping.get(code, ("☁️", "Bedeckt"))

def hole_wetter():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude={}&longitude={}"
            "&current=temperature_2m,weather_code"
            "&timezone=Europe%2FBerlin"
        ).format(LAT, LON)

        r = requests.get(url, timeout=10)
        data = r.json()
        c = data["current"]
        emoji, desc = wetter_beschreibung(c["weather_code"])
        return {
            "temp": c["temperature_2m"],
            "emoji": emoji,
            "desc": desc,
            "rhein": 8.4
        }
    except Exception:
        return None

def hole_luft():
    try:
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            "?latitude={}&longitude={}"
            "&current=pm2_5,pm10,ozone,birch_pollen,grass_pollen"
        ).format(LAT, LON)

        r = requests.get(url, timeout=10)
        data = r.json()
        c = data["current"]
        return {
            "ozon": c.get("ozone", 0),
            "pm25": c.get("pm2_5", 0),
            "pm10": c.get("pm10", 0),
            "birke": c.get("birch_pollen", 0),
            "gras": c.get("grass_pollen", 0)
        }
    except Exception:
        return None

# ---------------------------------------------------------
# Titel mit Baslerstab
# ---------------------------------------------------------
st.markdown(
    f"""
    <h1 style='text-align:center;color:#00529F;'>
        <img src="data:image/jpeg;base64,{baselstab_b64}" width="40"
             style="vertical-align:middle; margin-right:10px;">
        Basel Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Daten laden
# ---------------------------------------------------------
if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()

w = st.session_state.get("w")
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", "{} {}°C".format(w["emoji"], w["temp"]))
        st.write("Aktuell: <b>{}</b>".format(w["desc"]), unsafe_allow_html=True)
    with c2:
        st.metric("Rhein", "{} {}°C".format(rhein_e, w["rhein"]))

st.divider()
st.subheader("🌳 Umwelt & Luft")

l = st.session_state.get("l")
if l:
    st.write("**Aktuelle Werte:**")
    cp1, cp2 = st.columns(2)
    cp1.write("Birke: {}".format(pollen_status(l["birke"])))
    cp2.write("Gräser: {}".format(pollen_status(l["gras"])))

    st.write("")
    cl1, cl2, cl3 = st.columns(3)
    cl1.write("Ozon: {}".format(luft_status(l["ozon"])))
    cl2.write("PM 2.5: {}".format(luft_status(l["pm25"])))
    cl3.write("PM 10: {}".format(luft_status(l["pm10"])))
else:
    st.warning("Umweltdaten konnten nicht geladen werden.")

st.write("")
st.markdown(
    "<small><b>PM 2.5:</b> Sehr feine Partikel (Autoabgase, Industrie), dringen tief in die Lunge ein.</small>",
    unsafe_allow_html=True
)
st.markdown(
    "<small><b>PM 10:</b> Grössere Staubpartikel (Abrieb, Baustellen, Pollen), belasten die Atemwege.</small>",
    unsafe_allow_html=True
)

st.divider()
tz_ch = pytz.timezone("Europe/Zurich")
jetzt_ch = datetime.now(tz_ch).strftime("%H:%M")

st.caption(
    "Stand: {} | Quellen: Open‑Meteo (Wetter & Luftqualität), "
    "Rheintemperatur: Messstation Basel (manuell eingetragen)".format(jetzt_ch)
)
st.caption("(C)2026 by M. Kunz")
