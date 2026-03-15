import streamlit as st

# 1. Seiteneinstellungen
st.set_page_config(page_title="Mein Basel Wetter & Sport", page_icon="🏘️")

# 2. Titel der App
st.title("🏘️ Mein Basel: Wetter & Sport")

# 3. Wetter Sektion (Werte aus deinen Screenshots übernommen)
st.header("🌡️ Aktuelles Wetter")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Temperatur", value="5.0 °C")
    st.write("Aktuell: **Leicht bewölkt**")

with col2:
    st.metric(label="Rhein Temperatur", value="8.4 °C")
    st.write("🌊 **Status:** Erfrischend!")

st.divider()

# 4. Pollen Sektion
st.subheader("🌳 Pollenflug")
st.write("Birke: **Niedrig**")
st.write("Gräser: **Niedrig**")
st.write("💨 **Luftqualität:** Gut")

st.divider()

# 5. Fussball Sektion (Super League - 15. März 2026)
st.header("⚽ Fussball: Super League")

# Spiel: FC Basel
st.subheader("🔴🔵 FC Basel vs. Servette FC")
st.write("🕒 Anpfiff: **16:30 Uhr** (Joggeli)")
st.info("Mein Tipp: **2:1** – Ein Heimsieg zum Joggeli-Jubiläum!")

# Spiel: YB
st.subheader("🟡⚫ FC Lausanne-Sport vs. BSC Young Boys")
st.write("🕒 Anpfiff: **14:00 Uhr**")
st.write("Mein Tipp: **1:3** – YB nutzt die Lausanner Abwehrschwäche.")

# 6. Platzhalter für zukünftige API-Daten (Hier war vorhin der URL-Fehler)
# url = "https://deine-wetter-oder-sport-api.ch/v1/data"

st.divider()
st.caption("Datenstand: 15.03.2026 | Hopp FCB!")
