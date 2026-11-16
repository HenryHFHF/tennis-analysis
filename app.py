
import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# =====================================
# 1. GRUNDEINSTELLUNGEN
# =====================================

st.set_page_config(
    page_title="Tennis Analysis",
    page_icon="🎾",
    layout="wide"
)

DATEI = "tennis_daten.json"


# =====================================
# 2. DATEN LADEN UND SPEICHERN
# =====================================

def daten_laden():
    standard = {
        "matches": [],
        "turniere": [],
        "termine": [],
        "trainingsziel": ""
    }

    if os.path.exists(DATEI):
        try:
            with open(DATEI, "r", encoding="utf-8") as f:
                daten = json.load(f)

            for key, value in standard.items():
                if key not in daten:
                    daten[key] = value

            return daten

        except (json.JSONDecodeError, OSError):
            pass

    return standard


def daten_speichern():
    with open(DATEI, "w", encoding="utf-8") as f:
        json.dump(
            st.session_state.daten,
            f,
            ensure_ascii=False,
            indent=4
        )


if "daten" not in st.session_state:
    st.session_state.daten = daten_laden()

daten = st.session_state.daten


# =====================================
# 3. TITEL UND NAVIGATION
# =====================================

st.title("🎾 Tennis Analysis")

st.write("Dein persönliches Tennis-Portal.")

bereich = st.sidebar.radio(
    "Navigation",
    [
        "🏆 Turniere & Statistiken",
        "📈 Verbesserung & Training",
        "📅 Kalender & Planung"
    ]
)


# =====================================
# 4. TURNIERE UND STATISTIKEN
# =====================================

if bereich == "🏆 Turniere & Statistiken":

    st.header("🏆 Turniere & Statistiken")

    matches = daten["matches"]

    siege = sum(
        1 for m in matches
        if m["ausgang"] == "Gewonnen"
    )

    niederlagen = sum(
        1 for m in matches
        if m["ausgang"] == "Verloren"
    )

    gesamt = len(matches)

    quote = (
        siege / gesamt * 100
        if gesamt > 0 else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches", gesamt)
    col2.metric("Siege", siege)
    col3.metric("Siegquote", f"{quote:.1f} %")

    st.divider()

    # ---------------------------------
    # NEUES TURNIER
    # ---------------------------------

    st.subheader("🏆 Neues Turnier eintragen")

    with st.form("turnier_form"):

        turniername = st.text_input("Name des Turniers")
        turnierdatum = st.date_input(
            "Turnierdatum",
            value=date.today()
        )
        turnierort = st.text_input("Turnierort")

        turnier_speichern = st.form_submit_button(
            "Turnier speichern"
        )

        if turnier_speichern:

            if turniername.strip():

                daten["turniere"].append({
                    "name": turniername.strip(),
                    "datum": turnierdatum.isoformat(),
                    "ort": turnierort
                })

                daten["termine"].append({
                    "titel": turniername.strip(),
                    "datum": turnierdatum.isoformat(),
                    "typ": "Turnier"
                })

                daten_speichern()
                st.success("Turnier gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte einen Turniernamen eingeben.")

    st.divider()

    # ---------------------------------
    # NEUES MATCH
    # ---------------------------------

    st.subheader("🎾 Neues Match eintragen")

    turniernamen = ["Kein Turnier"] + [
        t["name"] for t in daten["turniere"]
    ]

    with st.form("match_form"):

        gegner = st.text_input("Name des Gegners")

        matchdatum = st.date_input(
            "Datum des Matches",
            value=date.today()
        )

        ergebnis = st.text_input(
            "Ergebnis (z. B. 6:4, 6:3)"
        )

        turnier = st.selectbox(
            "Turnier",
            turniernamen
        )

        ausgang = st.selectbox(
            "Matchausgang",
            ["Gewonnen", "Verloren"]
        )

        match_speichern = st.form_submit_button(
            "Match speichern"
        )

        if match_speichern:

            if gegner.strip() and ergebnis.strip():

                daten["matches"].append({
                    "gegner": gegner.strip(),
                    "datum": matchdatum.isoformat(),
                    "ergebnis": ergebnis.strip(),
                    "ausgang": ausgang,
                    "turnier": turnier
                })

                daten["termine"].append({
                    "titel": f"Match gegen {gegner.strip()}",
                    "datum": matchdatum.isoformat(),
                    "typ": "Match"
                })

                daten_speichern()
                st.success("Match gespeichert!")
                st.rerun()

            else:
                st.warning(
                    "Bitte Gegner und Ergebnis eingeben."
                )

    st.divider()

    # ---------------------------------
    # FORTSCHRITTSDIAGRAMM
    # ---------------------------------

    st.subheader("📊 Meine Entwicklung")

    if matches:

        monatliche_daten = {}

        for match in matches:

            monat = match["datum"][:7]

            if monat not in monatliche_daten:
                monatliche_daten[monat] = {
                    "Siege": 0,
                    "Niederlagen": 0
                }

            if match["ausgang"] == "Gewonnen":
                monatliche_daten[monat]["Siege"] += 1
            else:
                monatliche_daten[monat]["Niederlagen"] += 1

        df = pd.DataFrame.from_dict(
            monatliche_daten,
            orient="index"
        )

        df.index.name = "Monat"
        df = df.sort_index()

        df["Siegquote (%)"] = (
            df["Siege"] /
            (df["Siege"] + df["Niederlagen"]) * 100
        )

        st.write("**Siege und Niederlagen pro Monat**")

        st.bar_chart(
            df[["Siege", "Niederlagen"]]
        )

        st.write("**Entwicklung meiner Siegquote**")

        st.line_chart(
            df[["Siegquote (%)"]]
        )

        st.write("**Monatliche Übersicht**")

        st.dataframe(
            df,
            use_container_width=True
        )

    else:

        st.info(
            "Trage zuerst Matches ein, "
            "damit dein Fortschritt angezeigt wird."
        )

    st.divider()

    # ---------------------------------
    # MATCHÜBERSICHT
    # ---------------------------------

    st.subheader("🎾 Meine Spielergebnisse")

    if matches:

        for i in range(len(matches) - 1, -1, -1):

            match = matches[i]

            with st.expander(
                f"{match['datum']} – gegen "
                f"{match['gegner']} ({match['ausgang']})"
            ):

                st.write("Ergebnis:", match["ergebnis"])
                st.write("Turnier:", match["turnier"])

                if st.button(
                    "Match löschen",
                    key=f"delete_match_{i}"
                ):

                    daten["matches"].pop(i)
                    daten_speichern()
                    st.rerun()

    else:

        st.info("Noch keine Matches eingetragen.")

    st.divider()

    # ---------------------------------
    # TURNIERÜBERSICHT
    # ---------------------------------

    st.subheader("🏆 Meine Turniere")

    if daten["turniere"]:

        for turnier in daten["turniere"]:

            st.write(
                f"**{turnier['name']}** – "
                f"{turnier['datum']} – {turnier['ort']}"
            )

    else:

        st.info("Noch keine Turniere eingetragen.")


# =====================================
# 5. VERBESSERUNG UND TRAINING
# =====================================

elif bereich == "📈 Verbesserung & Training":

    st.header("📈 Verbesserung & Training")

    st.write(
        "Arbeite gezielt an deiner Tennistechnik."
    )

    trainingsbereiche = {
        "🎾 Aufschlag":
            "Verbessere Technik, Konstanz und Platzierung.",

        "🏸 Vorhand":
            "Trainiere Kontrolle, Länge und Präzision.",

        "🎾 Rückhand":
            "Arbeite an Sicherheit und Genauigkeit.",

        "🏃 Beinarbeit":
            "Verbessere Schnelligkeit und Positionierung.",

        "🧠 Taktik":
            "Lerne, deine Gegner besser zu lesen.",

        "💪 Mentales Training":
            "Trainiere Konzentration und Ruhe."
    }

    st.subheader("Trainingsbereiche")

    for name, beschreibung in trainingsbereiche.items():

        with st.expander(name):
            st.write(beschreibung)

    st.divider()

    # ---------------------------------
    # TRAININGSZIELE
    # ---------------------------------

    st.subheader("🎯 Meine Trainingsziele")

    ziel = st.text_area(
        "Woran möchtest du arbeiten?",
        value=daten["trainingsziel"]
    )

    if st.button("Trainingsziel speichern"):

        daten["trainingsziel"] = ziel
        daten_speichern()

        st.success("Trainingsziel gespeichert!")

    st.divider()

    # ---------------------------------
    # VIDEOANALYSE
    # ---------------------------------

    st.subheader("🎥 Videoanalyse")

    video_url = st.text_input(
        "Link zu einem Trainingsvideo"
    )

    if st.button("Video öffnen"):

        if video_url.startswith(("https://", "http://")):

            st.link_button(
                "Trainingsvideo ansehen",
                video_url
            )

        else:

            st.warning("Bitte einen gültigen Link eingeben.")

    st.caption(
        "Später können wir hier eigene Videos hochladen "
        "und deine Technik analysieren."
    )


# =====================================
# 6. KALENDER UND PLANUNG
# =====================================

elif bereich == "📅 Kalender & Planung":

    st.header("📅 Mein Tennis-Kalender")

    st.write(
        "Turniere und Matches werden automatisch "
        "in deinen Kalender übernommen."
    )

    st.divider()

    # ---------------------------------
    # NEUEN TERMIN ERSTELLEN
    # ---------------------------------

    st.subheader("📅 Neuen Termin hinzufügen")

    with st.form("termin_form"):

        titel = st.text_input("Name des Termins")

        termin_datum = st.date_input(
            "Datum",
            value=date.today(),
            key="termin_datum"
        )

        typ = st.selectbox(
            "Art des Termins",
            ["Training", "Event", "Sonstiges"]
        )

        termin_speichern = st.form_submit_button(
            "Termin speichern"
        )

        if termin_speichern:

            if titel.strip():

                daten["termine"].append({
                    "titel": titel.strip(),
                    "datum": termin_datum.isoformat(),
                    "typ": typ
                })

                daten_speichern()
                st.success("Termin gespeichert!")
                st.rerun()

            else:

                st.warning("Bitte einen Namen eingeben.")

    st.divider()

    # ---------------------------------
    # KALENDERÜBERSICHT
    # ---------------------------------

    st.subheader("📆 Meine nächsten Termine")

    alle_termine = sorted(
        daten["termine"],
        key=lambda x: x["datum"]
    )

    heute = date.today().isoformat()

    kommende_termine = [
        t for t in alle_termine
        if t["datum"] >= heute
    ]

    if kommende_termine:

        for i, termin in enumerate(kommende_termine):

            with st.expander(
                f"{termin['datum']} – {termin['titel']}"
            ):

                st.write("Kategorie:", termin["typ"])

                if st.button(
                    "Termin löschen",
                    key=f"delete_termin_{i}"
                ):

                    daten["termine"].remove(termin)
                    daten_speichern()
                    st.rerun()

    else:

        st.info("Keine kommenden Termine vorhanden.")

    st.divider()

    st.subheader("Alle Termine")

    if alle_termine:

        kalender_df = pd.DataFrame([
            {
                "Datum": t["datum"],
                "Termin": t["titel"],
                "Kategorie": t["typ"]
            }
            for t in alle_termine
        ])

        st.dataframe(
            kalender_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Dein Kalender ist noch leer.")


# =====================================
# 7. SEITENENDE
# =====================================

st.sidebar.divider()
st.sidebar.caption("🎾 Tennis Analysis")
st.sidebar.caption("Dein persönliches Tennis-Portal")
