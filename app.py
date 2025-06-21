import streamlit as st
from PIL import Image
import random

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

# ------------------- Session Setup -------------------
if "players" not in st.session_state:
    st.session_state.players = []
    st.session_state.current_player = 0
    st.session_state.stage = 0
    st.session_state.scores = {}
    st.session_state.started = False

# ------------------- Start Screen -------------------
if not st.session_state.started:
    st.title("🧭 Van Egypte naar Kanaän")

    st.subheader("Voer de namen in van de spelers:")
    names = []
    for i in range(4):
        name = st.text_input(f"Speler {i+1} naam:", key=f"player_{i}")
        if name:
            names.append(name)

    if st.button("Start het spel") and names:
        st.session_state.players = names
        st.session_state.scores = {name: 0 for name in names}
        st.session_state.started = True
        st.experimental_rerun()
    st.stop()

# ------------------- Game in Progress -------------------
stage = st.session_state.stage
player = st.session_state.players[st.session_state.current_player]

if stage < len(locations):
    loc = locations[stage]
    st.header(f"📍 Locatie {stage+1}: {loc['name']} ({player} is aan de beurt)")

    img = Image.open(loc["image"])
    st.image(img, use_column_width=True)

    st.subheader(loc["question"])
    choice = st.radio("Kies je antwoord:", loc["options"], key=f"choice_{stage}_{player}")

    if st.button("Bevestigen"):
        if choice == loc["answer"]:
            st.success("Goed gedaan!")
            st.session_state.scores[player] += 1
        else:
            st.error("Helaas, dat is niet correct.")

        st.session_state.current_player += 1

        if st.session_state.current_player >= len(st.session_state.players):
            st.session_state.current_player = 0
            st.session_state.stage += 1

        st.experimental_rerun()
else:
    st.balloons()
    st.header("🎉 Jullie hebben Kanaän bereikt!")
    st.subheader("🏆 Scorebord")

    sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(sorted_scores):
        st.write(f"{i+1}. **{name}**: {score} punten")

    if st.button("Opnieuw spelen"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
