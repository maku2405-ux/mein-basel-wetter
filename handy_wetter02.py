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
# Titel mit 🇨🇭 + Baslerstab
# ---------------------------------------------------------
st.markdown(
    f"""
    <h1 style='text-align:center;color:#00529F;'>
        🇨🇭
        <img src="data:image/jpeg;base64,{baselstab_b64}" width="40"
             style="vertical-align:middle; margin-left:10px; margin-right:10px;">
        Basel Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------
