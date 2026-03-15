import streamlit as st
import requests
from datetime import datetime
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
    except:
        return None

def hole_luft_und_pollen():
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=47.5584&longitude=7.5733&current=pm10,ozone,birch_pollen,grass_pollen"
        res = requests.get(url, timeout=5).json()
        curr = res['current']
        return {"ozon": curr['ozone'], "pm10": curr['pm10'], "birke": curr['birch_pollen'], "gras": curr['grass_pollen']}
    except:
        return None

def hole_fussball_ticker(suche_name):
    try:
        # Abruf der Saison 2025 (entspricht 2025/2026)
        res = requests.get("https://api.openligadb.de/getmatchdata/ch1/2025", timeout=5).json()
        if not res:
            return "Keine Spieldaten gefunden"
            
        jetzt = datetime.now()
        zukuenftige_spiele = []

        for spiel in res:
            t1_name = spiel['team1']['teamName']
            t2_name = spiel['team2']['teamName']
            
            # Suche nach dem Teamnamen im Spiel
            if suche_name.lower() in t1_name.lower() or suche_name.lower() in t2_name.lower():
                match_date = spiel['matchDateTime'].split(".")[0]
                zeit = datetime.strptime(match_date, "%Y-%m-%dT%H:%M:%S")
                
                # 1. LIVE-Check
                if not spiel['matchIsFinished'] and zeit <= jetzt:
                    t1_short, t2_short = spiel['team1']['shortName'], spiel['team2']['shortName']
                    res_list = spiel['matchResults']
                    p1 = res_list[-1]['pointsTeam1'] if res_list else 0
                    p2 = res_list[-1]['pointsTeam2'] if res_list else 0
                    return f"🔴 LIVE: {t1_short} {p1}:{p2} {t2_short}"
                
                # 2. Zukünftige Spiele sammeln
                if zeit > jetzt:
                    zukuenftige_spiele.append(spiel)

        if zukuenftige_spiele:
            # Das nächste Spiel finden
            naechstes = sorted(zukuenftige_spiele, key=lambda x: x['matchDateTime'])[0]
            m_date = naechstes['matchDateTime'].split(".")[0]
            zeit = datetime.strptime(m_date, "%Y-%m-%dT%H:%M:%S")
            t1_s, t2_s = naechstes['team1']['shortName'], naechstes['team2']['shortName']
            tag = "Heute" if zeit.date() == jetzt.date() else zeit.strftime("%d.%m.")
            return f"{tag}: {t1_s} vs. {t2_s} ({zeit.strftime('%H:%M')} Uhr)"

        return "Keine weiteren Spiele geplant"
    except Exception:
        return "Aktuell keine Daten"

# --- WAPPEN LADEN ---
def hole_wappen():
    try:
        url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Wappen_Basel-Stadt.svg/250px-Wappen_Basel-Stadt.svg.png"
        response = requests.get(url, timeout=3)
        return Image.open(BytesIO(response.content))
    except:
        return None

# --- UI DESIGN ---
wappen = hole_wappen()

if wappen:
    col_t1, col_t2, col_t3 = st.columns([1, 3, 1])
    with col_t1: st.image(wappen, width=80)
    with col_t2: st.markdown("<h1 style='text-align: center; color: #000000; padding-top: 10px;'>Basel Dashboard</h1>", unsafe_allow_html=True)
    with col_t3: st.image(wappen, width=80)
else:
    st.markdown("<h1 style='text-align: center;'>🏙️ Basel Dashboard</h1>", unsafe_allow_html=True)

# Initialisierung
if 'w' not in st.session_state:
    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()
    st.session_state.fcb = hole_fussball_ticker("Basel")
    st.session_state.yb = hole_fussball_ticker("Young Boys")

if st.button('🔄 DATEN AKTUALISIEREN'):
    st.session_state.w = hole_wetter_und_rhein()
    st.session_state.l = hole_luft_und_pollen()
    st.session_state.fcb = hole_fussball_ticker("Basel")
    st.session_state.yb = hole_fussball_ticker("Young Boys")
    st.rerun()

# 1. Wetter & Rhein
w = st.session_state.w
if w:
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Luft", f"{w['emoji']} {w['temp']}°C")
        st.write(f"Aktuell: **{w['desc']}**")
    with c2:
        st.metric("Rhein", f"🌊 {w['rhein']}°C")

# 2. Luftqualität & Pollen
l = st.session_state.l
if l:
    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("🌳 **Pollen:**")
        st.caption(f"Birke: {'Niedrig' if l['birke'] < 10 else 'Hoch'}")
        st.caption(f"Gräser: {'Niedrig' if l['gras'] < 10 else 'Hoch'}")
    with col_p2:
        st.write("💨 **Luftqualität:**")
        st.caption(f"Ozon: {l['ozon']} µg/m³")
        st.caption(f"Feinstaub (PM10): {l['pm10']} µg/m³")

# 3. Fussball-Ticker
st.divider()
st.write("⚽ **Fussball Ticker:**")
st.write(f"🔴🔵 **FC Basel:** {st.session_state.fcb}")
st.write(f"🟡⚫ **BSC Young Boys:** {st.session_state.yb}")
