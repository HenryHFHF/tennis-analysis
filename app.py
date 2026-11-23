import streamlit as st
from supabase import create_client
import pandas as pd
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


def daten_speichern():

    user = st.session_state.get("supabase_user")

    if user is None:
        st.error("Bitte zuerst anmelden.")
        return

    try:
        client = supabase_verbindung(
            st.session_state.get("supabase_token")
        )

        client.table("tennis_data").upsert({
            "id": str(user.id),
            "user_id": str(user.id),
            "data": st.session_state.daten
        }).execute()

    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")


# =================================
# 3. PASSWORTSCHUTZ
# =================================

def bearbeitungsschutz(key):

    freigabe = f"freigabe_{key}"

    if st.session_state.get(freigabe, False):
        return True

    with st.expander("🔒 Bearbeiten – Passwort erforderlich"):

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
            st.session_state.pop("daten", None)
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
        if m.get("ausgang") == "Gewonnen"
    )

    niederlagen = sum(
        1 for m in matches
        if m.get("ausgang") == "Verloren"
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

    match_art = st.selectbox(
        "Match-Art auswählen",
        ["Einzel", "Doppel"]
    )

    with st.form("match_formular"):

        if match_art == "Einzel":

            gegner = st.text_input("Name des Gegners")
            partner = ""
            gegner2 = ""

        else:

            partner = st.text_input(
                "Vor- und Nachname des Partners"
            )

            gegner = st.text_input(
                "Vor- und Nachname des 1. Gegners"
            )

            gegner2 = st.text_input(
                "Vor- und Nachname des 2. Gegners"
            )

        matchdatum = st.date_input(
            "Datum des Matches",
            key="match_datum_eingabe"
        )

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

            if match_art == "Einzel":

                eingaben_vollstaendig = (
                    gegner.strip() and ergebnis.strip()
                )

            else:

                eingaben_vollstaendig = (
                    partner.strip()
                    and gegner.strip()
                    and gegner2.strip()
                    and ergebnis.strip()
                )

            if eingaben_vollstaendig:

                neues_match = {
                    "_id": str(uuid.uuid4()),
                    "art": match_art,
                    "gegner": gegner,
                    "partner": partner,
                    "gegner2": gegner2,
                    "datum": matchdatum.isoformat(),
                    "ergebnis": ergebnis,
                    "ausgang": ausgang,
                    "turnier": match_turnier
                }

                daten["matches"].append(neues_match)

                if match_art == "Einzel":
                    titel = f"Match gegen {gegner}"
                else:
                    titel = f"Match gegen {gegner} und {gegner2}"

                daten["termine"].append({
                    "_id": str(uuid.uuid4()),
                    "titel": titel,
                    "datum": matchdatum.isoformat(),
                    "typ": "Match"
                })

                daten_speichern()

                st.success("Match wurde gespeichert!")
                st.rerun()

            else:
                st.warning(
                    "Bitte alle Namen und das Ergebnis eintragen."
                )

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

            art = match.get("art", "Einzel")
            partner = match.get("partner", "")
            gegner = match.get("gegner", "")
            gegner2 = match.get("gegner2", "")
            ausgang = match.get("ausgang", "Gewonnen")

            if ausgang == "Gewonnen":
                symbol = "🏆"
                farbe = "green"
            else:
                symbol = "🥈"
                farbe = "red"

            if art == "Doppel":
                titel = f"Doppel – {partner} / {gegner} und {gegner2}"
            else:
                titel = f"Einzel – {gegner}"

            with st.container(border=True):

                st.markdown(f"### {titel}")
                st.caption(match.get("datum", ""))

                st.markdown(
                    f"**Ausgang:** :{farbe}[{symbol} {ausgang}]"
                )

                if art == "Doppel":
                    st.markdown(f"**Partner:** {partner}")
                    st.markdown(f"**Gegner:** {gegner} und {gegner2}")
                else:
                    st.markdown(f"**Gegner:** {gegner}")

                st.markdown(
                    f"## :{farbe}[{match.get('ergebnis', '')}]"
                )

                st.markdown(
                    f"**Turnier:** {match.get('turnier', '-')}"
                )

                if st.button(
                    "✏️ Bearbeiten",
                    key=f"bearbeiten_match_{match_id}"
                ):
                    st.session_state["aktives_match_bearbeiten"] = match_id
                    st.rerun()

                if st.session_state.get(
                    "aktives_match_bearbeiten"
                ) == match_id:

                    if bearbeitungsschutz(f"match_{match_id}"):

                        st.divider()
                        st.markdown("### ✏️ Match bearbeiten")

                        art_neu = st.selectbox(
                            "Matchart",
                            ["Einzel", "Doppel"],
                            index=0 if art == "Einzel" else 1,
                            key=f"edit_art_{match_id}"
                        )

                        if art_neu == "Doppel":

                            partner_neu = st.text_input(
                                "Partner",
                                value=partner,
                                key=f"edit_partner_{match_id}"
                            )

                            gegner_neu = st.text_input(
                                "1. Gegner",
                                value=gegner,
                                key=f"edit_gegner_{match_id}"
                            )

                            gegner2_neu = st.text_input(
                                "2. Gegner",
                                value=gegner2,
                                key=f"edit_gegner2_{match_id}"
                            )

                        else:

                            partner_neu = ""
                            gegner2_neu = ""

                            gegner_neu = st.text_input(
                                "Name des Gegners",
                                value=gegner,
                                key=f"edit_gegner_{match_id}"
                            )

                        datum_neu = st.date_input(
                            "Datum",
                            value=date.fromisoformat(match["datum"]),
                            key=f"edit_datum_{match_id}"
                        )

                        ergebnis_neu = st.text_input(
                            "Ergebnis",
                            value=match.get("ergebnis", ""),
                            key=f"edit_ergebnis_{match_id}"
                        )

                        turnier_optionen = [
                            t.get("name", "")
                            for t in daten.get("turniere", [])
                            if t.get("name")
                        ]

                        aktuelles_turnier = match.get("turnier", "-")

                        if aktuelles_turnier not in turnier_optionen:
                            turnier_optionen.append(aktuelles_turnier)

                        if not turnier_optionen:
                            turnier_optionen = ["-"]

                        turnier_neu = st.selectbox(
                            "Turnier",
                            turnier_optionen,
                            index=turnier_optionen.index(aktuelles_turnier),
                            key=f"edit_turnier_{match_id}"
                        )

                        ausgang_neu = st.selectbox(
                            "Matchausgang",
                            ["Gewonnen", "Verloren"],
                            index=0 if ausgang == "Gewonnen" else 1,
                            key=f"edit_ausgang_{match_id}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "💾 Änderungen speichern",
                                key=f"save_match_{match_id}"
                            ):

                                if gegner_neu.strip() and ergebnis_neu.strip():

                                    if art_neu == "Doppel" and not (
                                        partner_neu.strip()
                                        and gegner2_neu.strip()
                                    ):
                                        st.warning(
                                            "Bitte Partner und beide Gegner eintragen."
                                        )

                                    else:

                                        altes_datum = match["datum"]

                                        if art == "Doppel":
                                            alter_titel = (
                                                f"Match gegen {gegner} und {gegner2}"
                                            )
                                        else:
                                            alter_titel = f"Match gegen {gegner}"

                                        if art_neu == "Doppel":
                                            neuer_titel = (
                                                f"Match gegen {gegner_neu} "
                                                f"und {gegner2_neu}"
                                            )
                                        else:
                                            neuer_titel = f"Match gegen {gegner_neu}"

                                        match["art"] = art_neu
                                        match["partner"] = partner_neu
                                        match["gegner"] = gegner_neu
                                        match["gegner2"] = gegner2_neu
                                        match["datum"] = datum_neu.isoformat()
                                        match["ergebnis"] = ergebnis_neu
                                        match["turnier"] = turnier_neu
                                        match["ausgang"] = ausgang_neu

                                        for termin in daten["termine"]:

                                            if (
                                                termin.get("typ") == "Match"
                                                and termin.get("titel") == alter_titel
                                                and termin.get("datum") == altes_datum
                                            ):
                                                termin["titel"] = neuer_titel
                                                termin["datum"] = datum_neu.isoformat()
                                                break

                                        daten_speichern()

                                        st.session_state.pop(
                                            f"freigabe_match_{match_id}",
                                            None
                                        )

                                        st.session_state.pop(
                                            "aktives_match_bearbeiten",
                                            None
                                        )

                                        st.success("Match erfolgreich geändert!")
                                        st.rerun()

                                else:
                                    st.warning(
                                        "Bitte Gegner und Ergebnis eintragen."
                                    )

                        with col2:

                            if st.button(
                                "Abbrechen",
                                key=f"cancel_match_{match_id}"
                            ):

                                st.session_state.pop(
                                    f"freigabe_match_{match_id}",
                                    None
                                )

                                st.session_state.pop(
                                    "aktives_match_bearbeiten",
                                    None
                                )

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

            with st.container(border=True):

                st.markdown(f"### {turnier['name']}")
                st.write("**Datum:**", turnier["datum"])
                st.write("**Ort:**", turnier.get("ort", ""))

                if st.button(
                    "✏️ Turnier bearbeiten",
                    key=f"bearbeiten_turnier_{turnier_id}"
                ):
                    st.session_state["aktives_turnier_bearbeiten"] = turnier_id
                    st.rerun()

                if st.session_state.get(
                    "aktives_turnier_bearbeiten"
                ) == turnier_id:

                    if bearbeitungsschutz(f"turnier_{turnier_id}"):

                        st.divider()
                        st.markdown("### ✏️ Turnier bearbeiten")

                        name_neu = st.text_input(
                            "Turniername",
                            value=turnier["name"],
                            key=f"edit_turnier_name_{turnier_id}"
                        )

                        datum_neu = st.date_input(
                            "Turnierdatum",
                            value=date.fromisoformat(turnier["datum"]),
                            key=f"edit_turnier_datum_{turnier_id}"
                        )

                        ort_neu = st.text_input(
                            "Turnierort",
                            value=turnier.get("ort", ""),
                            key=f"edit_turnier_ort_{turnier_id}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "💾 Änderungen speichern",
                                key=f"save_turnier_{turnier_id}"
                            ):

                                if name_neu.strip():

                                    alter_name = turnier["name"]
                                    altes_datum = turnier["datum"]

                                    turnier["name"] = name_neu
                                    turnier["datum"] = datum_neu.isoformat()
                                    turnier["ort"] = ort_neu

                                    for termin in daten["termine"]:

                                        if (
                                            termin.get("typ") == "Turnier"
                                            and termin.get("titel") == alter_name
                                            and termin.get("datum") == altes_datum
                                        ):
                                            termin["titel"] = name_neu
                                            termin["datum"] = datum_neu.isoformat()
                                            break

                                    daten_speichern()

                                    st.session_state.pop(
                                        f"freigabe_turnier_{turnier_id}",
                                        None
                                    )

                                    st.session_state.pop(
                                        "aktives_turnier_bearbeiten",
                                        None
                                    )

                                    st.success("Turnier erfolgreich geändert!")
                                    st.rerun()

                                else:
                                    st.warning("Bitte einen Turniernamen eingeben.")

                        with col2:

                            if st.button(
                                "Abbrechen",
                                key=f"cancel_turnier_{turnier_id}"
                            ):

                                st.session_state.pop(
                                    f"freigabe_turnier_{turnier_id}",
                                    None
                                )

                                st.session_state.pop(
                                    "aktives_turnier_bearbeiten",
                                    None
                                )

                                st.rerun()


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

        tagebuch_gut = st.text_area("Was lief heute gut?")
        tagebuch_verbessern = st.text_area("Was möchtest du verbessern?")
        tagebuch_erkenntnis = st.text_area("Was nimmst du aus dem Training mit?")

        tagebuch_speichern = st.form_submit_button(
            "📒 Trainingseintrag speichern"
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

                st.success("Dein Trainingseintrag wurde gespeichert!")
                st.rerun()

            else:
                st.warning("Bitte fülle mindestens ein Feld aus.")

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

            eintrag_id = eintrag["_id"]

            with st.expander(f"🎾 {eintrag['datum']}"):

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

                st.divider()

                # EINTRAG BEARBEITEN

                if st.button(
                    "✏️ Eintrag bearbeiten",
                    key=f"bearbeiten_tagebuch_{eintrag_id}"
                ):
                    st.session_state["aktiver_tagebuch_eintrag"] = eintrag_id
                    st.rerun()

                if st.session_state.get(
                    "aktiver_tagebuch_eintrag"
                ) == eintrag_id:

                    if bearbeitungsschutz(f"tagebuch_{eintrag_id}"):

                        st.markdown("### ✏️ Eintrag bearbeiten")

                        datum_neu = st.date_input(
                            "Trainingsdatum",
                            value=date.fromisoformat(eintrag["datum"]),
                            key=f"edit_tagebuch_datum_{eintrag_id}"
                        )

                        themen_neu = st.multiselect(
                            "Trainierte Bereiche",
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
                            ],
                            default=eintrag.get("themen", []),
                            key=f"edit_tagebuch_themen_{eintrag_id}"
                        )

                        gut_neu = st.text_area(
                            "Was lief heute gut?",
                            value=eintrag.get("gut", ""),
                            key=f"edit_tagebuch_gut_{eintrag_id}"
                        )

                        verbessern_neu = st.text_area(
                            "Was möchtest du verbessern?",
                            value=eintrag.get("verbessern", ""),
                            key=f"edit_tagebuch_verbessern_{eintrag_id}"
                        )

                        erkenntnis_neu = st.text_area(
                            "Was nimmst du aus dem Training mit?",
                            value=eintrag.get("erkenntnis", ""),
                            key=f"edit_tagebuch_erkenntnis_{eintrag_id}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button(
                                "💾 Änderungen speichern",
                                key=f"save_tagebuch_{eintrag_id}"
                            ):
                                eintrag["datum"] = datum_neu.isoformat()
                                eintrag["themen"] = themen_neu
                                eintrag["gut"] = gut_neu
                                eintrag["verbessern"] = verbessern_neu
                                eintrag["erkenntnis"] = erkenntnis_neu

                                daten_speichern()

                                st.session_state.pop(
                                    f"freigabe_tagebuch_{eintrag_id}",
                                    None
                                )

                                st.session_state.pop(
                                    "aktiver_tagebuch_eintrag",
                                    None
                                )

                                st.success("Eintrag geändert!")
                                st.rerun()

                        with col2:

                            if st.button(
                                "Abbrechen",
                                key=f"cancel_tagebuch_{eintrag_id}"
                            ):

                                st.session_state.pop(
                                    f"freigabe_tagebuch_{eintrag_id}",
                                    None
                                )

                                st.session_state.pop(
                                    "aktiver_tagebuch_eintrag",
                                    None
                                )

                                st.rerun()

                st.divider()

                # EINTRAG OHNE PASSWORT LÖSCHEN

                if st.button(
                    "🗑️ Eintrag löschen",
                    key=f"loeschen_tagebuch_{eintrag_id}"
                ):

                    daten["tagebuch"] = [
                        e for e in daten["tagebuch"]
                        if e["_id"] != eintrag_id
                    ]

                    daten_speichern()

                    st.session_state.pop(
                        "aktiver_tagebuch_eintrag",
                        None
                    )

                    st.session_state.pop(
                        f"freigabe_tagebuch_{eintrag_id}",
                        None
                    )

                    st.success("Eintrag gelöscht!")
                    st.rerun()

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

        termin_absenden = st.form_submit_button("Termin speichern")

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

                st.write("**Art:**", termin["typ"])

                if termin.get("typ") in ["Match", "Turnier"]:

                    st.info(
                        "Dieser Termin gehört zu einem Match oder Turnier. "
                        "Bitte bearbeite ihn im Bereich "
                        "'Turniere & Statistiken'."
                    )

                else:

                    # TERMIN BEARBEITEN

                    if st.button(
                        "✏️ Termin bearbeiten",
                        key=f"bearbeiten_termin_{termin_id}"
                    ):
                        st.session_state["aktiver_termin_bearbeiten"] = termin_id
                        st.rerun()

                    if st.session_state.get(
                        "aktiver_termin_bearbeiten"
                    ) == termin_id:

                        if bearbeitungsschutz(f"termin_{termin_id}"):

                            st.divider()
                            st.markdown("### ✏️ Termin bearbeiten")

                            titel_neu = st.text_input(
                                "Name des Termins",
                                value=termin.get("titel", ""),
                                key=f"edit_termin_titel_{termin_id}"
                            )

                            datum_neu = st.date_input(
                                "Datum des Termins",
                                value=date.fromisoformat(termin["datum"]),
                                key=f"edit_termin_datum_{termin_id}"
                            )

                            typ_neu = st.selectbox(
                                "Art des Termins",
                                ["Training", "Sonstiges"],
                                index=(
                                    0 if termin.get("typ") == "Training"
                                    else 1
                                ),
                                key=f"edit_termin_typ_{termin_id}"
                            )

                            col1, col2 = st.columns(2)

                            with col1:

                                if st.button(
                                    "💾 Änderungen speichern",
                                    key=f"save_termin_{termin_id}"
                                ):

                                    if titel_neu.strip():

                                        termin["titel"] = titel_neu
                                        termin["datum"] = datum_neu.isoformat()
                                        termin["typ"] = typ_neu

                                        daten_speichern()

                                        st.session_state.pop(
                                            f"freigabe_termin_{termin_id}",
                                            None
                                        )

                                        st.session_state.pop(
                                            "aktiver_termin_bearbeiten",
                                            None
                                        )

                                        st.success(
                                            "Termin erfolgreich geändert!"
                                        )
                                        st.rerun()

                                    else:
                                        st.warning(
                                            "Bitte gib einen Namen für den Termin ein."
                                        )

                            with col2:

                                if st.button(
                                    "Abbrechen",
                                    key=f"cancel_termin_{termin_id}"
                                ):

                                    st.session_state.pop(
                                        f"freigabe_termin_{termin_id}",
                                        None
                                    )

                                    st.session_state.pop(
                                        "aktiver_termin_bearbeiten",
                                        None
                                    )

                                    st.rerun()

                    st.divider()

                    # TERMIN OHNE PASSWORT LÖSCHEN

                    if st.button(
                        "🗑️ Termin löschen",
                        key=f"loeschen_termin_{termin_id}"
                    ):

                        daten["termine"] = [
                            t for t in daten["termine"]
                            if t["_id"] != termin_id
                        ]

                        daten_speichern()

                        st.session_state.pop(
                            "aktiver_termin_bearbeiten",
                            None
                        )

                        st.session_state.pop(
                            f"freigabe_termin_{termin_id}",
                            None
                        )

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
