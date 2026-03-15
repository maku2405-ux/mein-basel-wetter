import streamlit as st
import requests
from datetime import datetime
import pytz

# ---------------------------------------------------------
# Seiteneinstellungen
# ---------------------------------------------------------
st.set_page_config(page_title="Basler Luft & Rhein", page_icon="🌊")

LAT = 47.5584
LON = 7.5733

# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------

def pollen_status(v):
    if v < 10:
        return "🟢 Niedrig"
    elif v < 50:
        return "🟡 Achtung"
    else:
        return "🔴 Hoch"

def luft_status(v):
    if v < 20:
        return f"🟢 {v}"
    elif v < 50:
        return f"🟡 {v}"
    else:
        return f"🔴 {v}"

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

# ---------------------------------------------------------
# Wetter & Luftdaten
# ---------------------------------------------------------

def hole_wetter():
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            "&current=temperature_2m,weather_code"
            "&timezone=Europe%2FBerlin"
        )
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
            f"?latitude={LAT}&longitude={LON}"
            "&current=pm2_5,pm10,ozone,birch_pollen,grass_pollen"
        )
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
# UI Dashboard
# ---------------------------------------------------------

st.markdown(
    "<h1 style='text-align:center;color:#00529F;'>🏙️ Basel Dashboard</h1>",
    unsafe_allow_html=True
)

if st.button("🔄 DATEN AKTUALISIEREN") or "w" not in st.session_state:
    st.session_state.w = hole_wetter()
    st.session_state.l = hole_luft()

# Wetter
w = st.session_state.get("w")
if w:
    rhein_e = rhein_emoji(w["rhein"])
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°
