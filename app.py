import streamlit as st
from supabase import create_client
import pandas as pd
import uuid
import base64
from pathlib import Path
from datetime import date


# =================================
# 1. GRUNDEINSTELLUNGEN
# =================================

st.set_page_config(
    page_title="Tennis Analysis",
    page_icon="🎾",
    layout="wide"
)


# =================================
# DESIGN UND FARBEN
# =================================

st.markdown("""
<style>

/* Gesamter App-Hintergrund */
.stApp {
    background-color: #000000 !important;
    color: #f5f5f5 !important;
}

/* Oberer Streamlit-Bereich */
[data-testid="stHeader"] {
    background-color: #000000 !important;
}

/* Seitenleiste ausblenden */
[data-testid="stSidebar"] {
    display: none;
}

/* Überschriften und normale Texte */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

p, label, span, li, .stMarkdown, [data-testid="stMetricLabel"],
[data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
    color: #f0f0f0;
}

/* Eingabefelder */
.stTextInput input,
.stTextArea textarea,
.stDateInput input,
.stNumberInput input,
[data-baseweb="select"] > div {
    background-color: #171717 !important;
    color: #ffffff !important;
    border: 1px solid #555555 !important;
    border-radius: 8px;
}

/* Allgemeine Buttons: schwarz/dunkelgrau */
.stButton button,
.stFormSubmitButton button {
    background-color: #171717 !important;
    color: #ffffff !important;
    border: 1px solid #555555 !important;
    border-radius: 9px;
    font-weight: bold;
}

.stButton button *,
.stFormSubmitButton button * {
    color: #ffffff !important;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #292929 !important;
}

/* Dunkelgrüner Kopfbereich */
.st-key-top_header {
    background: linear-gradient(120deg, #12351f, #07110b) !important;
    padding: 20px 26px 16px 26px;
    border: 1px solid #315d3d;
    border-radius: 18px;
    margin-bottom: 12px;
}

.st-key-top_header .brand-title {
    color: #ffffff !important;
    font-size: 30px;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}

.st-key-top_header .brand-subtitle,
.st-key-top_header .logged-in-label {
    color: #d5e5d8 !important;
    font-size: 15px;
    margin: 5px 0 0 0;
}

/* Fünf große Navigationsfelder */
.st-key-main_navigation [role="radiogroup"] {
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px !important;
    width: 100%;
    background: transparent !important;
    padding: 0 !important;
}

.st-key-main_navigation [role="radiogroup"] label {
    display: flex !important;
    align-items: center;
    justify-content: center;
    min-height: 62px;
    padding: 12px 10px !important;
    background: #173d27 !important;
    border: 1px solid #315d3d !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    text-align: center;
    font-weight: 700;
    transition: background 0.2s ease, transform 0.2s ease;
}

.st-key-main_navigation [role="radiogroup"] label * {
    color: #ffffff !important;
}

.st-key-main_navigation [role="radiogroup"] label:hover {
    background: #245234 !important;
    border-color: #6b9b75 !important;
}

.st-key-main_navigation [role="radiogroup"] label:has(input:checked) {
    background: #347346 !important;
    border: 2px solid #b5d4bb !important;
}

.st-key-main_navigation [role="radiogroup"] input {
    display: none !important;
}

@media (max-width: 800px) {
    .st-key-main_navigation [role="radiogroup"] {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

/* Grüne Karten */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #173d27 !important;
    border: 1px solid #245234 !important;
    border-radius: 12px;
}

/* Weiße Schrift in grünen Karten */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] *,
[data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stVerticalBlockBorderWrapper"] p {
    color: #ffffff !important;
}

/* Login-Button im Kopfbereich: dunkelgrün */
.st-key-top_header [data-testid="stPopover"] > button {
    background-color: #245234 !important;
    color: #ffffff !important;
    border: 1px solid #3b6b49 !important;
    border-radius: 10px;
    font-weight: 700;
}

.st-key-top_header [data-testid="stPopover"] > button * {
    color: #ffffff !important;
}

.st-key-top_header [data-testid="stPopover"] > button:hover {
    background-color: #347346 !important;
}

/* Login-Fenster dunkel gestalten */
[data-testid="stPopoverBody"] {
    background-color: #171717 !important;
    border: 1px solid #555555 !important;
}

[data-testid="stPopoverBody"] p,
[data-testid="stPopoverBody"] label,
[data-testid="stPopoverBody"] span {
    color: #ffffff !important;
}

/* Anmelden-Button im geöffneten Login-Fenster: dunkel */
[data-testid="stPopoverBody"] .stButton button,
[data-testid="stPopoverBody"] .stFormSubmitButton button {
    background-color: #171717 !important;
    color: #ffffff !important;
    border: 1px solid #555555 !important;
}

[data-testid="stPopoverBody"] .stButton button *,
[data-testid="stPopoverBody"] .stFormSubmitButton button * {
    color: #ffffff !important;
}
/* =================================
   HEAD-TO-HEAD-FENSTER SCHWARZ
   ================================= */

/* Hintergrund des Dialogfensters */
[data-testid="stDialog"] {
    background-color: #000000 !important;
}

/* Eigentliche Dialogfläche */
[data-testid="stDialog"] > div,
[data-testid="stDialog"] [role="dialog"] {
    background-color: #000000 !important;
    border: 1px solid #315d3d !important;
    border-radius: 16px !important;
}

/* Alle inneren Bereiche schwarz */
[data-testid="stDialog"] [data-testid="stVerticalBlock"],
[data-testid="stDialog"] [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #000000 !important;
    border-color: #315d3d !important;
}

/* Überschriften und Texte weiß */
[data-testid="stDialog"] h1,
[data-testid="stDialog"] h2,
[data-testid="stDialog"] h3,
[data-testid="stDialog"] p,
[data-testid="stDialog"] label,
[data-testid="stDialog"] span,
[data-testid="stDialog"] [data-testid="stMarkdownContainer"],
[data-testid="stDialog"] [data-testid="stMarkdownContainer"] * {
    color: #ffffff !important;
}

/* Eingabefelder dunkel */
[data-testid="stDialog"] input,
[data-testid="stDialog"] textarea {
    background-color: #171717 !important;
    color: #ffffff !important;
    border: 1px solid #555555 !important;
}

/* Buttons im Head-to-Head-Fenster */
[data-testid="stDialog"] .stButton button {
    background-color: #245234 !important;
    color: #ffffff !important;
    border: 1px solid #315d3d !important;
}

[data-testid="stDialog"] .stButton button:hover {
    background-color: #292929 !important;
}
/* Trennlinien */
hr {
    border-color: #444444 !important;
}


/* Diagramme: schwarzer Hintergrund und helle Beschriftungen */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"] > div,
[data-testid="stArrowVegaLiteChart"] > div {
    background-color: #000000 !important;
}

[data-testid="stVegaLiteChart"] svg,
[data-testid="stArrowVegaLiteChart"] svg,
[data-testid="stVegaLiteChart"] canvas,
[data-testid="stArrowVegaLiteChart"] canvas {
    background-color: #000000 !important;
}

[data-testid="stVegaLiteChart"] .role-axis text,
[data-testid="stArrowVegaLiteChart"] .role-axis text,
[data-testid="stVegaLiteChart"] .role-axis-title,
[data-testid="stArrowVegaLiteChart"] .role-axis-title {
    fill: #ffffff !important;
}

[data-testid="stVegaLiteChart"] .role-axis path,
[data-testid="stVegaLiteChart"] .role-axis line,
[data-testid="stArrowVegaLiteChart"] .role-axis path,
[data-testid="stArrowVegaLiteChart"] .role-axis line {
    stroke: #777777 !important;
}


/* =================================
   WEISSE EINGABEN UND MELDEFELDER SCHWARZ
   ================================= */

/* Datumsfelder: auch den inneren Streamlit-/BaseWeb-Bereich färben */
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] > div,
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stDateInput"] [data-baseweb="input"] > div {
    background-color: #171717 !important;
    color: #ffffff !important;
    border-color: #555555 !important;
}

/* Auswahlfelder (z. B. Training, Match-Art, Turnier, Ergebnis) */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [role="combobox"],
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {
    background-color: #171717 !important;
    color: #ffffff !important;
    border-color: #555555 !important;
}

[data-testid="stSelectbox"] svg,
[data-testid="stDateInput"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Helle Info-/Hinweisboxen (z. B. „Keine anstehenden Termine“) */
[data-testid="stAlert"],
[data-testid="stAlert"] > div,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
    background-color: #171717 !important;
    color: #ffffff !important;
    border: 1px solid #3b6b49 !important;
    border-radius: 10px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* Auch Popover- und Dropdown-Flächen dunkel halten */
[data-baseweb="popover"] > div,
[data-baseweb="menu"] {
    background-color: #171717 !important;
    color: #ffffff !important;
}


</style>
""", unsafe_allow_html=True)



# =================================
# SUPABASE-VERBINDUNG
# =================================

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
        "tagebuch": [],
        "gegner_notizen": {}
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

# Login-Status vorbereiten
if "supabase_user" not in st.session_state:
    st.session_state.supabase_user = None


# OBERER KOPFBEREICH
with st.container(key="top_header"):

    col_brand, col_login = st.columns([6, 1])

    with col_brand:
        col_logo, col_titel = st.columns([1, 6], vertical_alignment="center")

        with col_logo:
            st.image("logo.png", width=85)

        with col_titel:
            st.markdown(
                "<h1 class='brand-title'>H.F. Tennis Analysis</h1>"
                "<p class='brand-subtitle'>Dein persönliches Tennis-Portal.</p>",
                unsafe_allow_html=True
            )

    with col_login:
        if st.session_state.supabase_user is None:

            with st.popover("🔐 Login"):

                email = st.text_input(
                    "E-Mail",
                    key="login_email"
                )

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
                        st.error(
                            "Anmeldung fehlgeschlagen. Bitte Daten prüfen."
                        )

        else:
            st.markdown(
                "<p class='logged-in-label'>Angemeldet</p>",
                unsafe_allow_html=True
            )

            if st.button("Abmelden"):
                st.session_state.supabase_user = None
                st.session_state.supabase_token = None
                st.session_state.pop("daten", None)
                st.rerun()


# DATEN LADEN
if "daten" not in st.session_state:
    st.session_state.daten = daten_laden()

daten = st.session_state.daten
# =================================
# HEAD-TO-HEAD DIALOG-FENSTER
# =================================

@st.dialog("🎾 Head-to-Head", width="large")
def head_to_head_dialog(gegner_name, daten):

    st.subheader(f"Dein Vergleich mit {gegner_name}")

    gegner_matches = [
        m for m in daten["matches"]
        if gegner_name.strip().casefold() in [
            str(m.get("gegner", "")).strip().casefold(),
            str(m.get("gegner2", "")).strip().casefold()
        ]
    ]

    h2h_siege = sum(
        1 for m in gegner_matches
        if m.get("ausgang") == "Gewonnen"
    )

    h2h_niederlagen = sum(
        1 for m in gegner_matches
        if m.get("ausgang") == "Verloren"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Matches", len(gegner_matches))
    col2.metric("🏆 Siege", h2h_siege)
    col3.metric("Niederlagen", h2h_niederlagen)

    st.divider()

    st.subheader("📋 Bisherige Begegnungen")

    if gegner_matches:

        for m in sorted(
            gegner_matches,
            key=lambda x: x.get("datum", ""),
            reverse=True
        ):

            symbol = (
                "🏆"
                if m.get("ausgang") == "Gewonnen"
                else "❌"
            )

            st.markdown(
                f"**{m.get('datum', '')}** – "
                f"{symbol} {m.get('ausgang', '')} – "
                f"{m.get('ergebnis', '')}"
            )

            st.caption(
                f"{m.get('art', 'Einzel')} | "
                f"Turnier: {m.get('turnier', '-')}"
            )

    else:
        st.info("Noch keine Begegnungen gefunden.")

    st.divider()

    st.subheader("📝 Meine Notizen zu diesem Gegner")

    notizen = daten.setdefault("gegner_notizen", {})

    notiz_id = gegner_name.strip().casefold()

    gespeicherte_notizen = notizen.get(notiz_id, {})

    spielweise = st.text_area(
        "Wie spielt der Gegner?",
        value=gespeicherte_notizen.get("spielweise", ""),
        key=f"h2h_spielweise_{notiz_id}"
    )

    staerken = st.text_area(
        "Stärken des Gegners",
        value=gespeicherte_notizen.get("staerken", ""),
        key=f"h2h_staerken_{notiz_id}"
    )

    schwaechen = st.text_area(
        "Schwächen des Gegners",
        value=gespeicherte_notizen.get("schwaechen", ""),
        key=f"h2h_schwaechen_{notiz_id}"
    )

    taktik = st.text_area(
        "Meine Taktik für das nächste Match",
        value=gespeicherte_notizen.get("taktik", ""),
        key=f"h2h_taktik_{notiz_id}"
    )

    if st.button(
        "💾 Gegnernotizen speichern",
        key=f"h2h_speichern_{notiz_id}"
    ):

        daten["gegner_notizen"][notiz_id] = {
            "spielweise": spielweise,
            "staerken": staerken,
            "schwaechen": schwaechen,
            "taktik": taktik
        }

        daten_speichern()

        st.success("Gegnernotizen wurden gespeichert!")

        st.rerun()

    if st.button(
        "✖ Fenster schließen",
        key=f"h2h_schliessen_{notiz_id}"
    ):

        st.session_state.pop("h2h_gegner", None)

        st.rerun()


# NAVIGATION ALS VIER GROSSE FELDER
with st.container(key="main_navigation"):
    bereich = st.radio(
        "Navigation",
        [
            "🏠 Startseite",
            "📊 Leistungsdashboard",
            "🏆 Turniere & Statistiken",
            "📈 Verbesserung & Training",
            "📅 Kalender & Planung"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="bereich_nav"
    )


# =================================
# 5. STARTSEITE
# =================================

if bereich == "🏠 Startseite":

    # Tennisplatz-Bild für den Willkommensbereich laden
    try:
        bild_daten = Path("startseite_tennis.jpg").read_bytes()
        bild_base64 = base64.b64encode(bild_daten).decode("utf-8")
        hero_hintergrund = (
            "linear-gradient(90deg, rgba(5, 20, 11, 0.88), "
            "rgba(5, 20, 11, 0.30)), "
            f"url('data:image/jpeg;base64,{bild_base64}')"
        )
    except FileNotFoundError:
        hero_hintergrund = "linear-gradient(135deg, #163d25, #0b0f0c)"

    st.markdown(f"""
    <div style="
        background-image: {hero_hintergrund};
        background-size: cover;
        background-position: center;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 48px 42px;
        border-radius: 20px;
        border: 1px solid #315d3d;
        margin-top: 18px;
        margin-bottom: 30px;
        box-shadow: 0 10px 28px rgba(0,0,0,0.18);
    ">
        <h1 style="font-size: 42px; color: #ffffff !important; margin-bottom: 10px;">
            Willkommen bei H.F. Tennis Analysis
        </h1>
        <p style="font-size: 20px; color: #ffffff !important; margin-bottom: 8px;">
            Dein persönliches Tennis-Portal.
        </p>
        <p style="font-size: 16px; color: #e1eee3 !important; max-width: 650px;">
            Analysiere deine Matches, verbessere dein Spiel
            und behalte deine Entwicklung im Blick.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🎾 Dein Tennis auf einen Blick")

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

    col1.metric("🎾 Matches", gesamt)
    col2.metric("🏆 Siege", siege)
    col3.metric("📊 Siegquote", f"{quote:.1f} %")

    st.divider()

    st.subheader("🚀 Deine Bereiche")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 🏆 Turniere & Statistiken")
            st.write("Behalte deine Matches, Ergebnisse und Erfolge im Blick.")

        with st.container(border=True):
            st.markdown("### 📈 Verbesserung & Training")
            st.write("Trainingsziele, Tipps und dein persönliches Tennis-Tagebuch.")

    with col2:
        with st.container(border=True):
            st.markdown("### 📅 Kalender & Planung")
            st.write("Alle deine Trainings, Matches und Turniere übersichtlich geplant.")

        with st.container(border=True):
            st.markdown("### 🎥 Videoanalyse")
            st.write("Nutze deine Trainingsvideos, um dein Spiel zu analysieren.")

    st.divider()

    st.subheader("📅 Deine nächsten Termine")

    heute = date.today().isoformat()

    kommende_termine = sorted(
        [
            t for t in daten["termine"]
            if t.get("datum", "") >= heute
        ],
        key=lambda t: t["datum"]
    )

    if kommende_termine:

        for termin in kommende_termine[:5]:

            st.markdown(
                f"**{termin['datum']}** – "
                f"{termin['titel']} "
                f"({termin['typ']})"
            )

    else:
        st.info("Du hast aktuell keine anstehenden Termine.")

    st.divider()

    st.caption("H.F. Tennis Analysis | Dein Tennis. Deine Entwicklung.")



# =================================
# 6. LEISTUNGSDASHBOARD
# =================================

elif bereich == "📊 Leistungsdashboard":

    st.header("📊 Mein Leistungsdashboard")
    st.write(
        "Deine wichtigsten Tennisdaten auf einen Blick – "
        "automatisch aus deinen gespeicherten Matches berechnet."
    )

    matches = daten.get("matches", [])

    siege = sum(
        1 for m in matches
        if m.get("ausgang") == "Gewonnen"
    )

    niederlagen = sum(
        1 for m in matches
        if m.get("ausgang") == "Verloren"
    )

    gesamt = len(matches)
    gewertete_matches = siege + niederlagen
    quote = (
        siege / gewertete_matches * 100
        if gewertete_matches > 0 else 0
    )

    einzel_matches = sum(
        1 for m in matches
        if m.get("art", "Einzel") == "Einzel"
    )

    doppel_matches = sum(
        1 for m in matches
        if m.get("art", "Einzel") == "Doppel"
    )

    # ---------------------------------
    # KENNZAHLEN
    # ---------------------------------

    st.subheader("🎾 Deine Gesamtbilanz")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Matches insgesamt", gesamt)
    col2.metric("🏆 Siege", siege)
    col3.metric("❌ Niederlagen", niederlagen)
    col4.metric("📊 Siegquote", f"{quote:.1f} %")

    st.divider()

    # ---------------------------------
    # EINZEL UND DOPPEL
    # ---------------------------------

    st.subheader("🎾 Einzel und Doppel")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Einzelmatches", einzel_matches)

    with col2:
        st.metric("Doppelmatches", doppel_matches)

    st.divider()

    # ---------------------------------
    # ZEITLICHE ENTWICKLUNG
    # ---------------------------------

    st.subheader("📈 Deine Entwicklung im Zeitverlauf")

    verlaufsdaten = []

    for match in matches:
        datum = pd.to_datetime(
            match.get("datum", ""),
            errors="coerce"
        )

        ausgang = match.get("ausgang")

        if pd.notna(datum) and ausgang in ["Gewonnen", "Verloren"]:
            verlaufsdaten.append({
                "Datum": datum,
                "Monat": datum.strftime("%Y-%m"),
                "Ausgang": ausgang
            })

    if verlaufsdaten:

        df_verlauf = pd.DataFrame(verlaufsdaten)

        monatsbilanz = (
            df_verlauf
            .groupby(["Monat", "Ausgang"])
            .size()
            .unstack(fill_value=0)
        )

        for spalte in ["Gewonnen", "Verloren"]:
            if spalte not in monatsbilanz.columns:
                monatsbilanz[spalte] = 0

        monatsbilanz = monatsbilanz.rename(columns={
            "Gewonnen": "Siege",
            "Verloren": "Niederlagen"
        })

        monatsbilanz = monatsbilanz.sort_index()

        monatsbilanz["Matches"] = (
            monatsbilanz["Siege"] + monatsbilanz["Niederlagen"]
        )

        monatsbilanz["Siegquote"] = (
            monatsbilanz["Siege"]
            / monatsbilanz["Matches"] * 100
        )

        st.markdown("**Siege und Niederlagen pro Monat**")
        st.bar_chart(
            monatsbilanz[["Siege", "Niederlagen"]],
            color=["#2E8B57", "#DC3545"]
        )

        st.markdown("**Entwicklung deiner monatlichen Siegquote**")
        st.line_chart(monatsbilanz[["Siegquote"]], color="#FFFFFF")

        # ---------------------------------
        # KARRIEREENTWICKLUNG
        # ---------------------------------

        st.markdown("### 🏆 Deine Karriereentwicklung")
        st.caption(
            "Die Kurve zeigt deine Gesamt-Siegquote nach jedem gespielten Match. "
            "Alle gewerteten Matches werden chronologisch berücksichtigt."
        )

        karriere_verlauf = (
            df_verlauf
            .sort_values("Datum", kind="stable")
            .reset_index(drop=True)
            .copy()
        )

        karriere_verlauf["Matchnummer"] = range(
            1, len(karriere_verlauf) + 1
        )
        karriere_verlauf["Siege bis dahin"] = (
            karriere_verlauf["Ausgang"] == "Gewonnen"
        ).cumsum()
        karriere_verlauf["Matches bis dahin"] = (
            karriere_verlauf["Matchnummer"]
        )
        karriere_verlauf["Gesamt-Siegquote"] = (
            karriere_verlauf["Siege bis dahin"]
            / karriere_verlauf["Matches bis dahin"] * 100
        )

        karriere_chart = karriere_verlauf[
            ["Matchnummer", "Gesamt-Siegquote"]
        ].set_index("Matchnummer")

        st.line_chart(karriere_chart, color="#3B8F5A")

        letzter_stand = karriere_verlauf.iloc[-1]
        st.caption(
            f"Nach {int(letzter_stand['Matches bis dahin'])} Matches "
            f"liegt deine Gesamt-Siegquote bei "
            f"{letzter_stand['Gesamt-Siegquote']:.1f} %."
        )

        with st.expander("Karriereverlauf als Tabelle anzeigen"):
            karriere_tabelle = karriere_verlauf[
                [
                    "Matchnummer",
                    "Datum",
                    "Ausgang",
                    "Siege bis dahin",
                    "Gesamt-Siegquote"
                ]
            ].copy()
            karriere_tabelle["Gesamt-Siegquote"] = (
                karriere_tabelle["Gesamt-Siegquote"].round(1)
            )
            st.dataframe(
                karriere_tabelle,
                use_container_width=True,
                hide_index=True
            )

        with st.expander("Monatliche Zahlen anzeigen"):
            st.dataframe(
                monatsbilanz,
                use_container_width=True
            )

    else:
        st.info(
            "Sobald Matches mit gültigem Datum und Ergebnis gespeichert sind, "
            "wird hier deine Entwicklung angezeigt."
        )

    st.divider()

    # ---------------------------------
    # LETZTE MATCHES
    # ---------------------------------

    st.subheader("🕒 Deine letzten Matches")

    matches_mit_datum = []

    for match in matches:
        datum = pd.to_datetime(
            match.get("datum", ""),
            errors="coerce"
        )

        if pd.notna(datum):
            matches_mit_datum.append((datum, match))

    matches_mit_datum.sort(
        key=lambda eintrag: eintrag[0],
        reverse=True
    )

    if matches_mit_datum:

        for datum, match in matches_mit_datum[:5]:

            if match.get("ausgang") == "Gewonnen":
                symbol = "🏆"
            elif match.get("ausgang") == "Verloren":
                symbol = "❌"
            else:
                symbol = "🎾"

            if match.get("art", "Einzel") == "Doppel":
                gegner_text = (
                    f"{match.get('gegner', '')} und "
                    f"{match.get('gegner2', '')}"
                )
            else:
                gegner_text = match.get("gegner", "Unbekannter Gegner")

            st.markdown(
                f"**{datum.strftime('%d.%m.%Y')}** – "
                f"{symbol} gegen {gegner_text} – "
                f"{match.get('ergebnis', 'Kein Ergebnis')}"
            )

            st.caption(
                f"{match.get('art', 'Einzel')} | "
                f"Turnier: {match.get('turnier', '-')}"
            )

    else:
        st.info("Es sind noch keine Matches mit gültigem Datum vorhanden.")

    st.divider()

    st.caption(
        "Die angezeigten Kennzahlen werden automatisch aus deinen "
        "gespeicherten Matches berechnet."
    )


# =================================
# 7. TURNIERE UND STATISTIKEN
# =================================

elif bereich == "🏆 Turniere & Statistiken":


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
        st.bar_chart(
            df[["Siege", "Niederlagen"]],
            color=["#2E8B57", "#DC3545"]
        )

        st.write("Entwicklung deiner Siegquote")
        st.line_chart(df["Siegquote"], color="#FFFFFF")

        st.dataframe(df)

    else:
        st.info("Trage Matches ein, um deinen Fortschritt zu sehen.")

    st.divider()



    # ---------------------------------
    # MATCHÜBERSICHT MIT SUCHE UND LADEFUNKTION
    # ---------------------------------

    st.subheader("🎾 Matchübersicht")

    if daten["matches"]:

        # Suchfeld und Filter
        st.markdown("### 🔎 Matches suchen und filtern")

        suchbegriff = st.text_input(
            "Suche nach Gegner, Partner, Turnier, Datum oder Ergebnis",
            placeholder="z. B. Max Mustermann oder 6:4",
            key="match_suche"
        )

        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            filter_art = st.selectbox(
                "Match-Art",
                ["Alle", "Einzel", "Doppel"],
                key="match_filter_art"
            )

        with col_filter2:
            filter_ausgang = st.selectbox(
                "Ergebnis",
                ["Alle", "Gewonnen", "Verloren"],
                key="match_filter_ausgang"
            )

        # Alle Matches zunächst neueste zuerst
        alle_matches = list(reversed(daten["matches"]))

        # Suchbegriff und Filter anwenden
        gefilterte_matches = []

        for match in alle_matches:

            suchtext = " ".join([
                str(match.get("gegner", "")),
                str(match.get("gegner2", "")),
                str(match.get("partner", "")),
                str(match.get("turnier", "")),
                str(match.get("datum", "")),
                str(match.get("ergebnis", "")),
                str(match.get("art", "Einzel")),
                str(match.get("ausgang", ""))
            ]).casefold()

            if suchbegriff.strip():
                if suchbegriff.strip().casefold() not in suchtext:
                    continue

            if (
                filter_art != "Alle"
                and match.get("art", "Einzel") != filter_art
            ):
                continue

            if (
                filter_ausgang != "Alle"
                and match.get("ausgang", "Gewonnen") != filter_ausgang
            ):
                continue

            gefilterte_matches.append(match)

        # Anzahl der angezeigten Matches verwalten
        if "match_anzeige_limit" not in st.session_state:
            st.session_state.match_anzeige_limit = 10

        # Bei einer neuen Suche oder Filterauswahl wieder vorne beginnen
        filter_signatur = (
            suchbegriff,
            filter_art,
            filter_ausgang
        )

        if (
            st.session_state.get("match_filter_signatur")
            != filter_signatur
        ):
            st.session_state.match_filter_signatur = filter_signatur
            st.session_state.match_anzeige_limit = 10

        anzeige_limit = st.session_state.match_anzeige_limit

        sichtbare_matches = gefilterte_matches[:anzeige_limit]

        st.divider()

        st.write(
            f"**{len(gefilterte_matches)} Matches gefunden**"
        )

        st.caption(
            f"Du siehst {len(sichtbare_matches)} "
            f"von {len(gefilterte_matches)} Matches."
        )

        # ---------------------------------
        # EINZELNE MATCHES ANZEIGEN
        # ---------------------------------

        if gefilterte_matches:

            for match in sichtbare_matches:

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
                    titel = (
                        f"Doppel – {partner} / "
                        f"{gegner} und {gegner2}"
                    )
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
                        st.markdown("**Gegner:**")

                        col_gegner1, col_gegner2 = st.columns(2)

                        with col_gegner1:

                            if st.button(
                                f"👤 {gegner}",
                                key=f"h2h_gegner1_{match_id}"
                            ):
                                st.session_state["h2h_gegner"] = gegner
                                st.rerun()

                        with col_gegner2:

                            if st.button(
                                f"👤 {gegner2}",
                                key=f"h2h_gegner2_{match_id}"
                            ):
                                st.session_state["h2h_gegner"] = gegner2
                                st.rerun()

                    else:

                        st.markdown("**Gegner:**")

                        if st.button(
                            f"👤 {gegner}",
                            key=f"h2h_gegner_{match_id}"
                        ):
                            st.session_state["h2h_gegner"] = gegner
                            st.rerun()

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
                        st.session_state[
                            "aktives_match_bearbeiten"
                        ] = match_id
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
                                index=turnier_optionen.index(
                                    aktuelles_turnier
                                ),
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

                                    if (
                                        gegner_neu.strip()
                                        and ergebnis_neu.strip()
                                    ):

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
                                                    f"Match gegen {gegner} "
                                                    f"und {gegner2}"
                                                )
                                            else:
                                                alter_titel = (
                                                    f"Match gegen {gegner}"
                                                )

                                            if art_neu == "Doppel":
                                                neuer_titel = (
                                                    f"Match gegen {gegner_neu} "
                                                    f"und {gegner2_neu}"
                                                )
                                            else:
                                                neuer_titel = (
                                                    f"Match gegen {gegner_neu}"
                                                )

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

                                            st.success(
                                                "Match erfolgreich geändert!"
                                            )
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

            # ---------------------------------
            # WEITERE MATCHES LADEN
            # ---------------------------------

            if len(sichtbare_matches) < len(gefilterte_matches):

                st.divider()

                if st.button(
                    "⬇️ Weitere 10 Spiele laden",
                    key="mehr_matches_laden",
                    use_container_width=True
                ):

                    st.session_state.match_anzeige_limit += 10
                    st.rerun()

            else:

                st.success("Alle passenden Matches werden angezeigt.")

        else:
            st.info(
                "Keine Matches gefunden. "
                "Ändere deine Suche oder die Filter."
            )

        # ---------------------------------
        # HEAD-TO-HEAD-FENSTER ÖFFNEN
        # ---------------------------------

        if st.session_state.get("h2h_gegner"):

            head_to_head_dialog(
                st.session_state["h2h_gegner"],
                daten
            )

    else:
        st.info("Du hast noch keine Matches eingetragen.")

        # ---------------------------------
        # HEAD-TO-HEAD-FENSTER ÖFFNEN
        # ---------------------------------

        if st.session_state.get("h2h_gegner"):

            head_to_head_dialog(
                st.session_state["h2h_gegner"],
                daten
            )
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
# 8. VERBESSERUNG UND TRAINING
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
# 9. KALENDER UND PLANUNG
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
# 10. SIDEBAR
# =================================

st.sidebar.divider()
st.sidebar.caption("🎾 Tennis Analysis")
st.sidebar.caption("Dein persönliches Tennis-Portal")
