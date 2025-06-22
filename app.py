import streamlit as st
from PIL import Image
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# ------------------- Config -------------------
LEADERBOARD_SHEET_NAME = "From Egypt to Canaan Leaderboard voor Tante Coco"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1QRG2EApQpkA4eWjmg7ZhWJJjRd52yZPpwCW_cgK4woE"

# ------------------- Game Data -------------------
locations = [
    {
        "name": "Egypte",
        "image": "images/egypt.jpg",
        "question": "Wie leidde het volk Israël uit Egypte?",
        "options": ["Mozes", "David", "Abraham"],
        "answer": "Mozes",
    },
    {
        "name": "Rode Zee",
        "image": "images/redsea.jpg",
        "question": "Wat gebeurde er bij de Rode Zee?",
        "options": ["Ze bouwden een boot", "Ze gingen er droog doorheen", "Ze keerden terug"],
        "answer": "Ze gingen er droog doorheen",
    },
    {
        "name": "Sinaï",
        "image": "images/sinai.jpg",
        "question": "Wat gaf God aan Mozes op de berg Sinaï?",
        "options": ["Een zwaard", "De Tien Geboden", "Een kroon"],
        "answer": "De Tien Geboden",
    },
    {
        "name": "Woestijn",
        "image": "images/desert.jpg",
        "question": "Wat gaf God te eten in de woestijn?",
        "options": ["Manna", "Vijgen", "Vis"],
        "answer": "Manna",
    },
    {
        "name": "Jordaan",
        "image": "images/jordan.jpg",
        "question": "Wie leidde het volk door de Jordaan?",
        "options": ["Jozua", "Mozes", "Aäron"],
        "answer": "Jozua",
    },
    {
        "name": "Kanaän",
        "image": "images/canaan.jpg",
        "question": "Hoe werd Kanaän genoemd?",
        "options": ["Land van wanhoop", "Land van melk en honing", "Land van oorlog"],
        "answer": "Land van melk en honing",
    },
]

# ------------------- Google Sheets Functions -------------------
def get_gspread_client():
    creds_dict = st.secrets["google"]
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

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

# ------------------- State Management -------------------
def reset_state():
    st.session_state.update({
        "input_name": "",
        "players": [],
        "scores": {},
        "stage": 0,
        "started": False,
        "answered": False,
        "answered_flags": {},
        "scores_uploaded": False,
        "leaderboard_data": [],
    })

def start_game():
    name = st.session_state.input_name.strip()
    if name:
        st.session_state.players = [name]
        st.session_state.scores = {name: 0}
        st.session_state.started = True
        st.session_state.stage = 0
        st.session_state.answered = False
        st.session_state.answered_flags = {}
        st.session_state.scores_uploaded = False

def submit_answer():
    stage = st.session_state.stage
    player = st.session_state.players[0]
    loc = locations[stage]
    choice = st.session_state[f"choice_{stage}"]

    if choice == loc["answer"]:
        if not st.session_state.answered_flags.get(stage, False):
            st.session_state.scores[player] += 1
        st.success("Goed gedaan!")
    else:
        st.error("Helaas, dat is niet correct.")

    st.session_state.answered = True
    st.session_state.answered_flags[stage] = True

def next_question():
    st.session_state.stage += 1
    st.session_state.answered = False

# ------------------- Main -------------------
# Initialize state
if "started" not in st.session_state:
    reset_state()

# Start screen
if not st.session_state.started:
    st.title("🧭 Van Egypte naar Kanaän")
    st.text_input("Voer je naam in:", key="input_name")
    st.button("Start het spel", key="btn_start", on_click=start_game)

    st.markdown("📄  [Open Google Sheets 🡥](%s)" % GOOGLE_SHEET_URL)

    st.stop()

# Gameplay
stage = st.session_state.stage
player = st.session_state.players[0]

if stage < len(locations):
    loc = locations[stage]
    st.header(f"📍 Locatie {stage+1}: {loc['name']} ({player} is aan de beurt)")
    st.image(Image.open(loc["image"]), use_container_width=True)
    st.subheader(loc["question"])

    st.radio(
        "Kies je antwoord:",
        loc["options"],
        key=f"choice_{stage}"
    )

    if not st.session_state.answered:
        st.button(
            "Beantwoord",
            key=f"btn_answer_{stage}",
            on_click=submit_answer
        )
    else:
        st.button(
            "Volgende vraag",
            key=f"btn_next_{stage}",
            on_click=next_question
        )

else:
    # End screen
    st.balloons()
    st.header("🎉 Jullie hebben Kanaän bereikt!")
    st.subheader(f"🏆 {player}'s score: {st.session_state.scores[player]} punten
