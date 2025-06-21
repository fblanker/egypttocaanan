import streamlit as st
from PIL import Image
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# Config en data blijven hetzelfde als in jouw code

# ... (Google Sheets functies en data zoals jij had) ...

# Initialize session state variabelen
if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "started" not in st.session_state:
    st.session_state.started = False
if "answered" not in st.session_state:
    st.session_state.answered = False
if "scores_uploaded" not in st.session_state:
    st.session_state.scores_uploaded = False
if "answered_flags" not in st.session_state:
    st.session_state.answered_flags = {}

def reset_state():
    for key in ["players", "scores", "stage", "started", "scores_uploaded", "answered_flags", "answered"]:
        if key in st.session_state:
            del st.session_state[key]

if not st.session_state.started:
    st.title("🧭 Van Egypte naar Kanaän")
    name = st.text_input("Voer je naam in:")
    if st.button("Start het spel") and name.strip() != "":
        reset_state()
        st.session_state.players = [name.strip()]
        st.session_state.scores = {name.strip(): 0}
        st.session_state.started = True
        st.session_state.answered = False
        st.session_state.scores_uploaded = False
        st.session_state.answered_flags = {}

    st.markdown("📊 Bekijk het live scorebord hieronder:")
    if st.button("📄 Open Google Sheets"):
        st.markdown(f"[Klik hier om het scorebord te openen 🡥]({GOOGLE_SHEET_URL})")
    st.stop()

stage = st.session_state.stage
player = st.session_state.players[0]

if stage < len(locations):
    loc = locations[stage]
    st.header(f"📍 Locatie {stage+1}: {loc['name']} ({player} is aan de beurt)")
    st.image(Image.open(loc["image"]), use_container_width=True)
    st.subheader(loc["question"])
    choice = st.radio("Kies je antwoord:", loc["options"], key=f"choice_{stage}_{player}")

    if not st.session_state.answered:
        if st.button("Beantwoord"):
            if choice == loc["answer"]:
                st.success("Goed gedaan!")
                if not st.session_state.answered_flags.get(stage, False):
                    st.session_state.scores[player] += 1
                    st.session_state.answered_flags[stage] = True
            else:
                st.error("Helaas, dat is niet correct.")
            st.session_state.answered = True
    else:
        if st.button("Volgende vraag"):
            st.session_state.answered = False
            st.session_state.stage += 1
            if st.session_state.answered_flags.get(stage, False):
                del st.session_state.answered_flags[stage]

else:
    st.balloons()
    st.header("🎉 Jullie hebben Kanaän bereikt!")
    st.subheader(f"🏆 {player}'s score: {st.session_state.scores[player]} punten")

    if not st.session_state.scores_uploaded:
        with st.spinner("Scores uploaden naar Google Sheets..."):
            leaderboard_data = update_google_leaderboard(st.session_state.scores)
        st.session_state.scores_uploaded = True
        st.session_state.leaderboard_data = leaderboard_data
    else:
        leaderboard_data = st.session_state.get('leaderboard_data', [])

    if leaderboard_data:
        st.subheader("🌍 Publiek scorebord")
        st.table(pd.DataFrame(leaderboard_data))

    if st.button("📄 Bekijk Google Sheets"):
        st.markdown(f"[Open scorebord 🡥]({GOOGLE_SHEET_URL})")

    if st.button("🔁 Opnieuw spelen"):
        reset_state()
        st.experimental_rerun()
