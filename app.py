import streamlit as st
from PIL import Image
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ------------------- Config -------------------
LEADERBOARD_SHEET_NAME = "From Egypt to Canaan Leaderboard"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QRG2EApQpkA4eWjmg7ZhWJJjRd52yZPpwCW_cgK4woE"

# ------------------- Game Data -------------------
locations = [
    {
        "name": "Egypte",
        "image": "images/egypt.jpg",
        "question": "Wie leidde het volk Israël uit Egypte?",
        "options": ["Mozes", "David", "Abraham"],
        "answer": "Mozes"
    },
    {
        "name": "Rode Zee",
        "image": "images/redsea.jpg",
        "question": "Wat gebeurde er bij de Rode Zee?",
        "options": ["Ze bouwden een boot", "Ze gingen er droog doorheen", "Ze keerden terug"],
        "answer": "Ze gingen er droog doorheen"
    },
    {
        "name": "Sinaï",
        "image": "images/sinai.jpg",
        "question": "Wat gaf God aan Mozes op de berg Sinaï?",
        "options": ["Een zwaard", "De Tien Geboden", "Een kroon"],
        "answer": "De Tien Geboden"
    },
    {
        "name": "Woestijn",
        "image": "images/desert.jpg",
        "question": "Wat gaf God te eten in de woestijn?",
        "options": ["Manna", "Vijgen", "Vis"],
        "answer": "Manna"
    },
    {
        "name": "Jordaan",
        "image": "images/jordan.jpg",
        "question": "Wie leidde het volk door de Jordaan?",
        "options": ["Jozua", "Mozes", "Aäron"],
        "answer": "Jozua"
    },
    {
        "name": "Kanaän",
        "image": "images/canaan.jpg",
        "question": "Hoe werd Kanaän genoemd?",
        "options": ["Land van wanhoop", "Land van melk en honing", "Land van oorlog"],
        "answer": "Land van melk en honing"
    }
]

# ------------------- Google Sheets Functions -------------------
def get_gspread_client():
    creds_dict = st.secrets["google"]
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client

def update_google_leaderboard(new_scores):
    client = get_gspread_client()
    sheet = client.open(LEADERBOARD_SHEET_NAME).sheet1
    existing = sheet.get_all_records()
    rows = existing.copy()

    for name, score in new_scores.items():
        today = str(date.today())
        updated = False
        for row in rows:
            if row["name"] == name:
                if score > int(row["score"]):
                    row["score"] = score
                    row["date"] = today
                updated = True
                break
        if not updated:
            rows.append({"name": name, "score": score, "date": today})

    rows = sorted(rows, key=lambda x: x["score"], reverse=True)[:10]
    sheet.clear()
    sheet.append_row(["name", "score", "date"])
    for row in rows:
        sheet.append_row([row["name"], row["score"], row["date"]])
    return rows

# ------------------- Streamlit Game -------------------

# Initialize session state variables
if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "started" not in st.session_state:
    st.session_state.started = False
if "confirm_clicks" not in st.session_state:
    st.session_state.confirm_clicks = 0
if "scores_uploaded" not in st.session_state:
    st.session_state.scores_uploaded = False
# To prevent double scoring per question
if "answered_flags" not in st.session_state:
    st.session_state.answered_flags = {}

# Clear irrelevant state on restart
def reset_state():
    for key in ["players", "scores", "stage", "started", "confirm_clicks", "scores_uploaded", "answered_flags"]:
        if key in st.session_state:
            del st.session_state[key]

if not st.session_state.started:
    st.title("🧭 Van Egypte naar Kanaän")
    st.subheader("Voer de naam in van de speler:")
    name = st.text_input("Speler naam:", key="player_name")

    if st.button("Start het spel") and name.strip() != "":
        reset_state()
        st.session_state.players = [name.strip()]  # Only one player
        st.session_state.scores = {name.strip(): 0}
        st.session_state.started = True
        st.session_state.confirm_clicks = 0
        st.session_state.scores_uploaded = False
        st.session_state.answered_flags = {}

    st.markdown("📊 Bekijk het live scorebord hieronder:")
    if st.button("📄 Open Google Sheets"):
        st.markdown(f"[Klik hier om het scorebord te openen 🡥]({GOOGLE_SHEET_URL})")
    st.stop()

stage = st.session_state.stage
player = st.session_state.players[0]  # only one player

if stage < len(locations):
    loc = locations[stage]
    st.header(f"📍 Locatie {stage+1}: {loc['name']} ({player} is aan de beurt)")
    st.image(Image.open(loc["image"]), use_container_width=True)
    st.subheader(loc["question"])
    choice = st.radio("Kies je antwoord:", loc["options"], key=f"choice_{stage}_{player}")

    if st.button("Bevestigen"):
        st.session_state.confirm_clicks += 1

    if st.session_state.confirm_clicks == 1:
        if choice == loc["answer"]:
            st.success("Goed gedaan!")
            if not st.session_state.answered_flags.get(stage, False):
                st.session_state.scores[player] += 1
                st.session_state.answered_flags[stage] = True
        else:
            st.error("Helaas, dat is niet correct
