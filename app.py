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
    # … your other locations …
    {
        "name": "Kanaän",
        "image": "images/canaan.jpg",
        "question": "Hoe werd Kanaän genoemd?",
        "options": ["Land van wanhoop", "Land van melk en honing", "Land van oorlog"],
        "answer": "Land van melk en honing",
    },
]

# ------------------- Google Sheets -------------------
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
    today = str(date.today())

    for name, score in new_scores.items():
        found = False
        for r in rows:
            if r["name"] == name:
                found = True
                if score > int(r["score"]):
                    r["score"] = score
                    r["date"] = today
        if not found:
            rows.append({"name": name, "score": score, "date": today})

    rows = sorted(rows, key=lambda x: x["score"], reverse=True)[:10]
    sheet.clear()
    sheet.append_row(["name", "score", "date"])
    for r in rows:
        sheet.append_row([r["name"], r["score"], r["date"]])

    return rows

# ------------------- State Helpers -------------------
def reset_state():
    for k in [
        "input_name",
        "players",
        "scores",
        "stage",
        "started",
        "scores_uploaded",
        "leaderboard_data",
    ]:
        if k in st.session_state:
            del st.session_state[k]

def start_game():
    name = st.session_state.input_name.strip()
    if name:
        st.session_state.players = [name]
        st.session_state.scores = {name: 0}
        st.session_state.stage = 0
        st.session_state.started = True
        st.session_state.scores_uploaded = False

def submit_answer_and_next():
    stage = st.session_state.stage
    player = st.session_state.players[0]
    choice = st.session_state[f"choice_{stage}"]
    correct = locations[stage]["answer"]
    if choice == correct:
        st.session_state.scores[player] += 1
    # advance instantly
    st.session_state.stage += 1

# ------------------- App -------------------
if "started" not in st.session_state:
    reset_state()

# 1) Entry screen
if not st.session_state.get("started", False):
    st.title("🧭 Van Egypte naar Kanaän")
    st.text_input("Voer je naam in:", key="input_name")
    st.button("Start het spel", key="btn_start", on_click=start_game)
    st.markdown(f"📄  [Open Google Sheets 🡥]({GOOGLE_SHEET_URL})")
    st.stop()

# 2) Questions
stage = st.session_state.stage
player = st.session_state.players[0]

if stage < len(locations):
    loc = locations[stage]
    st.header(f"📍 Locatie {stage+1}: {loc['name']}")
    st.image(Image.open(loc["image"]), use_container_width=True)
    st.subheader(loc["question"])

    # radio with unique key
    st.radio(
        "Kies je antwoord:",
        loc["options"],
        key=f"choice_{stage}"
    )

    # one-click answer & next
    st.button(
        "Beantwoord",
        key=f"btn_answer_{stage}",
        on_click=submit_answer_and_next
    )

else:
    # 3) End screen & leaderboard
    st.balloons()
    score = st.session_state.scores[player]
    st.header("🎉 Kanaän bereikt!")
    st.subheader(f"🏆 {player}'s score: {score} punten")

    if not st.session_state.get("scores_uploaded", False):
        with st.spinner("Scores uploaden..."):
            lb = update_google_leaderboard(st.session_state.scores)
        st.session_state.scores_uploaded = True
        st.session_state.leaderboard_data = lb

    df = pd.DataFrame(st.session_state.leaderboard_data)
    if not df.empty:
        st.subheader("🌍 Publiek scorebord")
        st.table(df)

    st.markdown(f"📄  [Bekijk Google Sheets 🡥]({GOOGLE_SHEET_URL})")
    st.button("🔁 Opnieuw spelen", on_click=reset_state)
