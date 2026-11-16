import streamlit as st

# Titel der App
st.title("🎾 Meine Tennis-Analyse")

# Begrüßung
st.write("Willkommen zu meiner Tennis-App!")

# Erster Bereich
st.header("Meine Tennis-Statistiken")

st.write("Hier werden später meine Spielergebnisse angezeigt.")

# Neues Match eintragen
st.header("Neues Match eintragen")

gegner = st.text_input("Name des Gegners")

datum = st.date_input("Datum des Matches")

ergebnis = st.text_input("Ergebnis (z. B. 6:4, 6:3)")

gewonnen = st.selectbox(
    "Wie ist das Match ausgegangen?",
    ["Gewonnen", "Verloren"]
)

if st.button("Match speichern"):
    st.success("Dein Match wurde eingetragen!")

    st.write("Gegner:", gegner)
    st.write("Datum:", datum)
    st.write("Ergebnis:", ergebnis)
    st.write("Ausgang:", gewonnen)
