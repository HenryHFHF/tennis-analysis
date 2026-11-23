
import streamlit as st
from supabase import create_client
import pandas as pd
import json
import os
import uuid
from datetime import date

# =================================
# 1. GRUNDEINSTELLUNGEN
# =================================

st.set_page_config(
    page_title="Tennis Analysis",
    page_icon="🎾",
    layout="wide"
)

DATEI = "tennis_daten.json"
def supabase_verbindung(access_token=None):
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]

    client = create_client(url, key)

    if access_token:
        client.postgrest.auth(access_token)

    return client

# =================================
# 2. DATEN LADEN UND SPEICHERN
# =================================


def daten_laden():

    standard = {
        "matches": [],
        "turniere": [],
        "termine": [],
        "video_url": "",
        "tagebuch": []
    }

    user = st.session_state.get("supabase_user")

    if user is None:
        return standard

    try:
        client = supabase_verbindung(
            st.session_state.get("supabase_token")
        )

        antwort = (
            client.table("tennis_data")
            .select("*")
            .eq("user_id", str(user.id))
            .execute()
        )

        if antwort.data:
            daten = antwort.data[0]["data"]

            for key, value in standard.items():
                if key not in daten:
                    daten[key] = value

            return daten

        return standard

    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        return standard


# =================================
# 3. PASSWORTSCHUTZ
# =================================

def loeschschutz(key):

    freigabe = f"freigabe_{key}"

    if st.session_state.get(freigabe, False):
        return True

    with st.expander("🔒 Löschen – Passwort erforderlich"):

        passwort = st.text_input(
            "Passwort eingeben",
            type="password",
            key=f"passwort_{key}"
        )

        if st.button(
            "Freischalten",
            key=f"freischalten_{key}"
        ):

            try:
                richtiges_passwort = st.secrets["loesch_passwort"]

            except Exception:
                st.error("Das Passwort wurde noch nicht eingerichtet.")
                return False

            if passwort == richtiges_passwort:

                st.session_state[freigabe] = True
                st.rerun()

            else:
                st.error("Falsches Passwort!")

    return False


# =================================
# 4. TITEL UND NAVIGATION
# =================================
col_titel, col_login = st.columns([4, 1])

with col_login:
    if "supabase_user" not in st.session_state:
        st.session_state.supabase_user = None

    if st.session_state.supabase_user is None:

        with st.popover("🔐 Login"):
            email = st.text_input("E-Mail", key="login_email")
            passwort = st.text_input(
                "Passwort",
                type="password",
                key="login_passwort"
            )

            if st.button("Anmelden"):
                try:
                    client = supabase_verbindung()
                    antwort = client.auth.sign_in_with_password({
                        "email": email,
                        "password": passwort
                    })

                    st.session_state.supabase_user = antwort.user
                    st.session_state.supabase_token = antwort.session.access_token
                    st.session_state.pop("daten", None)
                    st.success("Erfolgreich angemeldet!")
                    st.rerun()

                except Exception:
                    st.error("Anmeldung fehlgeschlagen. Bitte Daten prüfen.")

    else:
        st.write("Angemeldet")
        if st.button("Abmelden"):
            st.session_state.supabase_user = None
            st.session_state.supabase_token = None
            st.rerun()

col_logo, col_titel = st.columns([1, 4])

with col_logo:
    st.image("logo.png", width=130)

with col_titel:
    st.title("H.F. Tennis Analysis")
    st.write("Dein persönliches Tennis-Portal.")
if "daten" not in st.session_state:
    st.session_state.daten = daten_laden()

daten = st.session_state.daten

bereich = st.sidebar.radio(
    "Navigation",
    [
        "🏆 Turniere & Statistiken",
        "📈 Verbesserung & Training",
        "📅 Kalender & Planung"
    ]
)


# =================================
# 5. TURNIERE UND STATISTIKEN
# =================================

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

    quote = siege / gesamt * 100 if gesamt > 0 else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches", gesamt)
    col2.metric("Siege", siege)
    col3.metric("Siegquote", f"{quote:.1f} %")

    st.divider()

    # ---------------------------------
    # TURNIER HINZUFÜGEN
    # ---------------------------------

    st.subheader("➕ Neues Turnier eintragen")

    with st.form("turnier_formular"):

        turniername = st.text_input("Name des Turniers")

        turnierdatum = st.date_input("Datum des Turniers")

        turnierort = st.text_input("Ort")

        turnier_absenden = st.form_submit_button(
            "Turnier speichern"
        )

        if turnier_absenden:

            if turniername.strip():

                neues_turnier = {
                    "_id": str(uuid.uuid4()),
                    "name": turniername,
                    "datum": turnierdatum.isoformat(),
                    "ort": turnierort
                }

                daten["turniere"].append(neues_turnier)

                daten["termine"].append({
                    "_id": str(uuid.uuid4()),
                    "titel": turniername,
                    "datum": turnierdatum.isoformat(),
                    "typ": "Turnier"
                })

                daten_speichern()

                st.success("Turnier wurde gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte gib einen Turniernamen ein.")

    st.divider()

    # ---------------------------------
    # MATCH HINZUFÜGEN
    # ---------------------------------

    st.subheader("➕ Neues Match eintragen")

    turniernamen = [
        t["name"] for t in daten["turniere"]
    ]

    turnier_auswahl = ["Kein Turnier"] + turniernamen

    with st.form("match_formular"):

        gegner = st.text_input("Name des Gegners")

        matchdatum = st.date_input("Datum des Matches")

        ergebnis = st.text_input(
            "Ergebnis (z. B. 6:4, 6:3)"
        )

        match_turnier = st.selectbox(
            "Turnier",
            turnier_auswahl
        )

        ausgang = st.selectbox(
            "Wie ist das Match ausgegangen?",
            ["Gewonnen", "Verloren"]
        )

        match_absenden = st.form_submit_button(
            "Match speichern"
        )

        if match_absenden:

            if gegner.strip() and ergebnis.strip():

                neues_match = {
                    "_id": str(uuid.uuid4()),
                    "gegner": gegner,
                    "datum": matchdatum.isoformat(),
                    "ergebnis": ergebnis,
                    "ausgang": ausgang,
                    "turnier": match_turnier
                }

                daten["matches"].append(neues_match)

                daten["termine"].append({
                    "_id": str(uuid.uuid4()),
                    "titel": f"Match gegen {gegner}",
                    "datum": matchdatum.isoformat(),
                    "typ": "Match"
                })

                daten_speichern()

                st.success("Match wurde gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte Gegner und Ergebnis eintragen.")

    st.divider()

    # ---------------------------------
    # FORTSCHRITTSDIAGRAMM
    # ---------------------------------

    st.subheader("📊 Meine Entwicklung")

    if daten["matches"]:

        monatsdaten = {}

        for m in daten["matches"]:

            monat = m["datum"][:7]

            if monat not in monatsdaten:

                monatsdaten[monat] = {
                    "Siege": 0,
                    "Niederlagen": 0
                }

            if m["ausgang"] == "Gewonnen":
                monatsdaten[monat]["Siege"] += 1

            else:
                monatsdaten[monat]["Niederlagen"] += 1

        df = pd.DataFrame.from_dict(
            monatsdaten,
            orient="index"
        )

        df.index.name = "Monat"
        df = df.sort_index()

        df["Siegquote"] = (
            df["Siege"] /
            (df["Siege"] + df["Niederlagen"]) * 100
        )

        st.write("Siege und Niederlagen pro Monat")
        st.bar_chart(df[["Siege", "Niederlagen"]])

        st.write("Entwicklung deiner Siegquote")
        st.line_chart(df["Siegquote"])

        st.dataframe(df)

    else:
        st.info("Trage Matches ein, um deinen Fortschritt zu sehen.")

    st.divider()

    # ---------------------------------
    # MATCHÜBERSICHT
    # ---------------------------------

    st.subheader("🎾 Matchübersicht")

    if daten["matches"]:

        for match in reversed(daten["matches"]):

            match_id = match["_id"]

            with st.expander(
                f"{match['gegner']} – {match['datum']}"
            ):

                st.write("Ergebnis:", match["ergebnis"])
                st.write("Ausgang:", match["ausgang"])
                st.write("Turnier:", match["turnier"])

                if loeschschutz(f"match_{match_id}"):

                    if st.button(
                        "🗑️ Match löschen",
                        key=f"delete_match_{match_id}"
                    ):

                        daten["matches"] = [
                            m for m in daten["matches"]
                            if m["_id"] != match_id
                        ]

                        st.session_state.pop(
                            f"freigabe_match_{match_id}",
                            None
                        )

                        daten_speichern()
                        st.success("Match gelöscht!")
                        st.rerun()

    else:
        st.info("Noch keine Matches eingetragen.")

    st.divider()

    # ---------------------------------
    # TURNIERÜBERSICHT
    # ---------------------------------

    st.subheader("🏆 Meine Turniere")

    if daten["turniere"]:

        for turnier in reversed(daten["turniere"]):

            turnier_id = turnier["_id"]

            with st.expander(
                f"{turnier['name']} – {turnier['datum']}"
            ):

                st.write("Ort:", turnier["ort"])

                if loeschschutz(f"turnier_{turnier_id}"):

                    if st.button(
                        "🗑️ Turnier löschen",
                        key=f"delete_turnier_{turnier_id}"
                    ):

                        turniername = turnier["name"]
                        turnierdatum = turnier["datum"]

                        daten["turniere"] = [
                            t for t in daten["turniere"]
                            if t["_id"] != turnier_id
                        ]

                        daten["termine"] = [
                            t for t in daten["termine"]
                            if not (
                                t["typ"] == "Turnier"
                                and t["titel"] == turniername
                                and t["datum"] == turnierdatum
                            )
                        ]

                        st.session_state.pop(
                            f"freigabe_turnier_{turnier_id}",
                            None
                        )

                        daten_speichern()
                        st.success("Turnier gelöscht!")
                        st.rerun()

    else:
        st.info("Noch keine Turniere eingetragen.")


# =================================
# 6. VERBESSERUNG UND TRAINING
# =================================

elif bereich == "📈 Verbesserung & Training":

    st.header("📈 Verbesserung & Training")

    # ---------------------------------
    # TRAININGSTIPPS
    # ---------------------------------

    st.subheader("🎾 Trainingstipps")

    trainingsbereiche = {
        "Aufschlag": "Achte auf einen gleichmäßigen Ballwurf und einen kontrollierten Bewegungsablauf.",
        "Vorhand": "Arbeite an deinem Treffpunkt vor dem Körper und einer guten Vorbereitung.",
        "Rückhand": "Achte auf eine stabile Körperposition und einen sauberen Treffpunkt.",
        "Beinarbeit": "Versuche, dich rechtzeitig zum Ball zu bewegen und nach dem Schlag wieder bereit zu sein.",
        "Taktik": "Beobachte die Stärken und Schwächen deines Gegners und spiele bewusst.",
        "Mentales Training": "Setze dir kleine Ziele und konzentriere dich auf den nächsten Punkt."
    }

    for thema, tipp in trainingsbereiche.items():

        with st.expander(thema):
            st.write(tipp)

    st.divider()

    # ---------------------------------
    # TENNIS-TAGEBUCH
    # ---------------------------------

    st.header("📒 Mein Tennis-Tagebuch")

    st.write(
        "Halte deine Trainingseinheiten fest und "
        "beobachte, wie du dich weiterentwickelst."
    )

    with st.form("tagebuch_formular", clear_on_submit=True):

        tagebuch_datum = st.date_input(
            "Datum des Trainings",
            value=date.today()
        )

        tagebuch_themen = st.multiselect(
            "Was hast du trainiert?",
            [
                "Aufschlag",
                "Vorhand",
                "Rückhand",
                "Volley",
                "Beinarbeit",
                "Taktik",
                "Matchtraining",
                "Fitness",
                "Mentales Training"
            ]
        )

        tagebuch_gut = st.text_area(
            "Was lief heute gut?"
        )

        tagebuch_verbessern = st.text_area(
            "Was möchtest du verbessern?"
        )

        tagebuch_erkenntnis = st.text_area(
            "Was nimmst du aus dem Training mit?"
        )

        tagebuch_speichern = st.form_submit_button(
            "📓 Trainingseintrag speichern"
        )

        if tagebuch_speichern:

            if (
                tagebuch_themen
                or tagebuch_gut.strip()
                or tagebuch_verbessern.strip()
                or tagebuch_erkenntnis.strip()
            ):

                neuer_eintrag = {
                    "_id": str(uuid.uuid4()),
                    "datum": tagebuch_datum.isoformat(),
                    "themen": tagebuch_themen,
                    "gut": tagebuch_gut,
                    "verbessern": tagebuch_verbessern,
                    "erkenntnis": tagebuch_erkenntnis
                }

                daten["tagebuch"].append(neuer_eintrag)

                daten_speichern()

                st.success(
                    "Dein Trainingseintrag wurde gespeichert!"
                )

                st.rerun()

            else:
                st.warning(
                    "Bitte fülle mindestens ein Feld aus."
                )

    st.divider()

    # ---------------------------------
    # ALTE TAGEBUCHEINTRÄGE
    # ---------------------------------

    st.subheader("📖 Meine bisherigen Einträge")

    if daten["tagebuch"]:

        eintraege = sorted(
            daten["tagebuch"],
            key=lambda e: e["datum"],
            reverse=True
        )

        for eintrag in eintraege:

            with st.expander(
                f"🎾 {eintrag['datum']}"
            ):

                st.write("**Trainierte Bereiche:**")

                if eintrag["themen"]:
                    st.write(", ".join(eintrag["themen"]))
                else:
                    st.write("Keine Bereiche angegeben.")

                st.write("**Was lief gut?**")
                st.write(eintrag["gut"] or "Keine Angabe")

                st.write("**Was möchte ich verbessern?**")
                st.write(eintrag["verbessern"] or "Keine Angabe")

                st.write("**Meine Erkenntnis:**")
                st.write(eintrag["erkenntnis"] or "Keine Angabe")

    else:
        st.info(
            "Du hast noch keine Tagebucheinträge. "
            "Schreibe deinen ersten Trainingseintrag!"
        )

    st.divider()

    # ---------------------------------
    # VIDEOANALYSE
    # ---------------------------------

    st.subheader("🎥 Videoanalyse")

    video_url = st.text_input(
        "Link zu deinem Trainingsvideo",
        value=daten.get("video_url", "")
    )

    if st.button("Videolink speichern"):

        daten["video_url"] = video_url
        daten_speichern()

        st.success("Videolink gespeichert!")

    if daten.get("video_url"):

        st.link_button(
            "🎬 Video öffnen",
            daten["video_url"]
        )


# =================================
# 7. KALENDER UND PLANUNG
# =================================

elif bereich == "📅 Kalender & Planung":

    st.header("📅 Kalender & Planung")

    # ---------------------------------
    # NEUEN TERMIN HINZUFÜGEN
    # ---------------------------------

    st.subheader("➕ Neuen Termin eintragen")

    with st.form("termin_formular"):

        terminname = st.text_input("Name des Termins")

        termindatum = st.date_input("Datum des Termins")

        terminart = st.selectbox(
            "Art des Termins",
            ["Training", "Sonstiges"]
        )

        termin_absenden = st.form_submit_button(
            "Termin speichern"
        )

        if termin_absenden:

            if terminname.strip():

                daten["termine"].append({
                    "_id": str(uuid.uuid4()),
                    "titel": terminname,
                    "datum": termindatum.isoformat(),
                    "typ": terminart
                })

                daten_speichern()

                st.success("Termin gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte gib einen Namen ein.")

    st.divider()

    # ---------------------------------
    # KALENDERÜBERSICHT
    # ---------------------------------

    st.subheader("📆 Meine Termine")

    if daten["termine"]:

        termine_sortiert = sorted(
            daten["termine"],
            key=lambda t: t["datum"]
        )

        heute = date.today().isoformat()

        st.write("**Anstehende Termine**")

        kommende = [
            t for t in termine_sortiert
            if t["datum"] >= heute
        ]

        if kommende:

            for termin in kommende:

                st.write(
                    f"📌 **{termin['datum']}** – "
                    f"{termin['titel']} ({termin['typ']})"
                )

        else:
            st.info("Keine anstehenden Termine.")

        st.divider()

        st.write("**Alle Termine verwalten**")

        for termin in reversed(termine_sortiert):

            termin_id = termin["_id"]

            with st.expander(
                f"{termin['titel']} – {termin['datum']}"
            ):

                st.write("Art:", termin["typ"])

                # Kalendertermine ohne Passwort löschen
                if st.button(
                    "🗑️ Termin löschen",
                    key=f"delete_termin_{termin_id}"
                ):

                    daten["termine"] = [
                        t for t in daten["termine"]
                        if t["_id"] != termin_id
                    ]

                    daten_speichern()
                    st.success("Termin gelöscht!")
                    st.rerun()

    else:
        st.info("Noch keine Termine eingetragen.")


# =================================
# 8. SIDEBAR
# =================================

st.sidebar.divider()
st.sidebar.caption("🎾 Tennis Analysis")
st.sidebar.caption("Dein persönliches Tennis-Portal")
