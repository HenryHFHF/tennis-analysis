import streamlit as st
import json
import os
from datetime import date

# -----------------------------
# GRUNDEINSTELLUNGEN
# -----------------------------

st.set_page_config(
    page_title="Tennis Analysis",
    page_icon="🎾",
    layout="wide"
)

DATEI = "tennis_daten.json"


# -----------------------------
# DATEN SPEICHERN UND LADEN
# -----------------------------

def daten_laden():
    if os.path.exists(DATEI):
        try:
            with open(DATEI, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "matches": [],
        "turniere": [],
        "termine": []
    }


def daten_speichern():
    with open(DATEI, "w", encoding="utf-8") as f:
        json.dump(st.session_state.daten, f, ensure_ascii=False, indent=4)


if "daten" not in st.session_state:
    st.session_state.daten = daten_laden()


daten = st.session_state.daten


# -----------------------------
# STARTSEITE UND NAVIGATION
# -----------------------------

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


# ==================================================
# 1. TURNIERE UND STATISTIKEN
# ==================================================

if bereich == "🏆 Turniere & Statistiken":

    st.header("🏆 Turniere & Statistiken")

    matches = daten["matches"]

    siege = sum(1 for m in matches if m["ausgang"] == "Gewonnen")
    niederlagen = sum(1 for m in matches if m["ausgang"] == "Verloren")
    gesamt = len(matches)

    quote = siege / gesamt * 100 if gesamt > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches", gesamt)
    col2.metric("Siege", siege)
    col3.metric("Siegquote", f"{quote:.1f} %")

    st.divider()

    # Neues Turnier

    st.subheader("Neues Turnier eintragen")

    with st.form("turnier_form"):
        turniername = st.text_input("Name des Turniers")
        turnierdatum = st.date_input("Turnierdatum", value=date.today())
        turnierort = st.text_input("Turnierort")

        turnier_speichern = st.form_submit_button("Turnier speichern")

        if turnier_speichern:
            if turniername.strip():
                daten["turniere"].append({
                    "name": turniername,
                    "datum": turnierdatum.isoformat(),
                    "ort": turnierort
                })

                daten["termine"].append({
                    "titel": turniername,
                    "datum": turnierdatum.isoformat(),
                    "typ": "Turnier"
                })

                daten_speichern()
                st.success("Turnier gespeichert!")
                st.rerun()
            else:
                st.warning("Bitte gib einen Turniernamen ein.")

    # Neues Match

    st.divider()
    st.subheader("Neues Match eintragen")

    turniernamen = ["Kein Turnier"] + [
        t["name"] for t in daten["turniere"]
    ]

    with st.form("match_form"):

        gegner = st.text_input("Name des Gegners")
        datum = st.date_input("Datum des Matches", value=date.today())

        ergebnis = st.text_input(
            "Ergebnis (z. B. 6:4, 6:3)"
        )

        turnier = st.selectbox(
            "Gehört das Match zu einem Turnier?",
            turniernamen
        )

        ausgang = st.selectbox(
            "Wie ist das Match ausgegangen?",
            ["Gewonnen", "Verloren"]
        )

        match_speichern = st.form_submit_button("Match speichern")

        if match_speichern:
            if gegner.strip() and ergebnis.strip():

                daten["matches"].append({
                    "gegner": gegner,
                    "datum": datum.isoformat(),
                    "ergebnis": ergebnis,
                    "ausgang": ausgang,
                    "turnier": turnier
                })

                # Match automatisch im Kalender anzeigen
                daten["termine"].append({
                    "titel": f"Match gegen {gegner}",
                    "datum": datum.isoformat(),
                    "typ": "Match"
                })

                daten_speichern()
                st.success("Match gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte Gegner und Ergebnis eintragen.")
import pandas as pd

    # Fortschrittsdiagramm

    st.divider()
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

        # Tabelle für das Diagramm erstellen

        df = pd.DataFrame.from_dict(
            monatliche_daten,
            orient="index"
        )

        df = df.sort_index()

        # Siegquote berechnen

        df["Siegquote (%)"] = (
            df["Siege"] /
            (df["Siege"] + df["Niederlagen"]) * 100
        )

        st.write("**Siege und Niederlagen pro Monat**")
        st.bar_chart(df[["Siege", "Niederlagen"]])

        st.write("**Entwicklung meiner Siegquote**")
        st.line_chart(df[["Siegquote (%)"]])

        st.write("**Monatliche Übersicht**")
        st.dataframe(df, use_container_width=True)

    else:
        st.info("Trage zuerst Matches ein, damit dein Fortschritt angezeigt werden kann.")
    # Matchübersicht

    st.divider()
    st.subheader("Meine Spielergebnisse")

    if matches:
        for i, match in enumerate(reversed(matches)):
            with st.expander(
                f"{match['datum']} – gegen {match['gegner']} "
                f"({match['ausgang']})"
            ):
                st.write("Ergebnis:", match["ergebnis"])
                st.write("Turnier:", match["turnier"])

                if st.button("Match löschen", key=f"delete_match_{i}"):
                    daten["matches"].remove(match)
                    daten_speichern()
                    st.rerun()
    else:
        st.info("Du hast noch keine Matches eingetragen.")

    # Turnierübersicht

    st.divider()
    st.subheader("Meine Turniere")

    if daten["turniere"]:
        for turnier in daten["turniere"]:
            st.write(
                f"🏆 **{turnier['name']}** – "
                f"{turnier['datum']} – {turnier['ort']}"
            )
    else:
        st.info("Noch keine Turniere eingetragen.")


# ==================================================
# 2. VERBESSERUNG UND TRAINING
# ==================================================

elif bereich == "📈 Verbesserung & Training":

    st.header("📈 Verbesserung & Training")

    st.write(
        "Hier kannst du an deiner Tennistechnik "
        "und deiner Spielstärke arbeiten."
    )

    st.subheader("🎯 Trainingsbereiche")

    trainingsbereiche = {
        "Aufschlag": "Arbeite an deiner Aufschlagtechnik und Konstanz.",
        "Vorhand": "Trainiere Kontrolle, Länge und Platzierung.",
        "Rückhand": "Verbessere deine Sicherheit und Präzision.",
        "Beinarbeit": "Arbeite an Schnelligkeit und Positionierung.",
        "Taktik": "Lerne, deine Gegner besser zu lesen.",
        "Mentales Training": "Arbeite an Konzentration und Ruhe."
    }

    for name, beschreibung in trainingsbereiche.items():
        with st.expander(name):
            st.write(beschreibung)

    st.divider()

    # Eigene Trainingsnotizen

    st.subheader("📝 Meine Trainingsziele")

    if "trainingsziel" not in st.session_state:
        st.session_state.trainingsziel = ""

    ziel = st.text_area(
        "Woran möchtest du arbeiten?",
        value=st.session_state.trainingsziel
    )

    if st.button("Trainingsziel speichern"):
        st.session_state.trainingsziel = ziel
        st.success("Trainingsziel gespeichert!")

    st.divider()

    # Videos

    st.subheader("🎥 Videoanalyse")

    video_url = st.text_input(
        "Link zu einem Trainingsvideo"
    )

    if st.button("Video öffnen"):
        if video_url.startswith(("https://", "http://")):
            st.link_button("Trainingsvideo ansehen", video_url)
        else:
            st.warning("Bitte gib einen gültigen Video-Link ein.")

    st.caption(
        "Hier können wir später auch eigene Videos "
        "hochladen und analysieren."
    )


# ==================================================
# 3. KALENDER UND PLANUNG
# ==================================================

elif bereich == "📅 Kalender & Planung":

    st.header("📅 Mein Tennis-Kalender")

    st.write(
        "Deine Turniere und Matches werden automatisch "
        "aus dem ersten Bereich übernommen."
    )

    st.divider()

    # Neuen Termin hinzufügen

    st.subheader("Neuen Termin hinzufügen")

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
                    "titel": titel,
                    "datum": termin_datum.isoformat(),
                    "typ": typ
                })

                daten_speichern()
                st.success("Termin gespeichert!")
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")

    st.divider()

    # Termine anzeigen

    st.subheader("Meine nächsten Termine")

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
                f"📅 {termin['datum']} – {termin['titel']}"
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
        st.info("Du hast momentan keine kommenden Termine.")

    st.divider()

    st.subheader("Alle Termine")

    if alle_termine:
        st.dataframe(
            [
                {
                    "Datum": t["datum"],
                    "Termin": t["titel"],
                    "Kategorie": t["typ"]
                }
                for t in alle_termine
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Dein Kalender ist noch leer.")


# ==================================================
# ENDE
# ==================================================

st.sidebar.divider()
st.sidebar.caption("🎾 Tennis Analysis – Version 2.0")
