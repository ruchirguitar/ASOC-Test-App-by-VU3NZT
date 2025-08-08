# app.py
import streamlit as st
import pandas as pd
import random
from pathlib import Path

st.set_page_config(page_title="GIAR ASOC Mock Test", layout="wide")

# ---- HEADER WITH LOGO AND CREDITS ----
logo_path = "logo_color_new_small.png"
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo_path, width=120)
with col2:
    st.title("Gujarat Institute of Amateur Radio — ASOC Mock Test")
    st.caption("www.giar.org — App by Ruchir Purohit")

st.markdown("---")

# ---- LOAD QUESTION BANKS ----
sectionA_file = Path("sectionA_1000.xlsx")
sectionB_file = Path("sectionB_1000.xlsx")

dfA = pd.read_excel(sectionA_file)
dfB = pd.read_excel(sectionB_file)

# ---- SELECT GRADE ----
grade = st.selectbox(
    "Select Grade",
    ["Restricted (25 A + 25 B)", "General (50 A + 50 B)"]
)
if "Restricted" in grade:
    nA, nB = 25, 25
else:
    nA, nB = 50, 50

# ---- RANDOM SELECTION ----
seed = st.session_state.get("seed", None)
if seed is None:
    seed = random.randint(1, 10**9)
    st.session_state["seed"] = seed
random.seed(seed)

sampleA = dfA.sample(n=nA, random_state=seed).reset_index(drop=True)
sampleB = dfB.sample(n=nB, random_state=seed+1).reset_index(drop=True)

st.info("Exam layout: Section A (Radio Theory) on the left, Section B (Radio Regulations) on the right.")

# Store correct answers after shuffle
correct_answers_map = {}

# ---- DISPLAY QUESTIONS SIDE-BY-SIDE ----
answers = {}
with st.form("exam_form"):
    colA, colB = st.columns(2)

    with colA:
        st.header("Section A — Radio Theory")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            st.markdown(f"**A{i+1}. {row['Question']}**")

            # Prepare options with labels
            opts = [
                ("A", row['OptionA']),
                ("B", row['OptionB']),
                ("C", row['OptionC']),
                ("D", row['OptionD'])
            ]
            random.shuffle(opts)

            # Store correct answer letter after shuffle
            for new_label, opt_text in opts:
                if new_label == row['Answer']:
                    correct_answers_map[qkey] = opts.index((new_label, opt_text))

            # Create options with A) etc.
            display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(opts)]

            answers[qkey] = st.radio(
                "",
                display_opts,
                key=f"A_radio_{i}",
                index=None,
                label_visibility="collapsed"
            )
            st.markdown("&nbsp;", unsafe_allow_html=True)  # One blank line after options

    with colB:
        st.header("Section B — Radio Regulations")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            st.markdown(f"**B{i+1}. {row['Question']}**")

            # Prepare options with labels
            opts = [
                ("A", row['OptionA']),
                ("B", row['OptionB']),
                ("C", row['OptionC']),
                ("D", row['OptionD'])
            ]
            random.shuffle(opts)

            # Store correct answer letter after shuffle
            for new_label, opt_text in opts:
                if new_label == row['Answer']:
                    correct_answers_map[qkey] = opts.index((new_label, opt_text))

            # Create options with A) etc.
            display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(opts)]

            answers[qkey] = st.radio(
                "",
                display_opts,
                key=f"B_radio_{i}",
                index=None,
                label_visibility="collapsed"
            )
            st.markdown("&nbsp;", unsafe_allow_html=True)  # One blank line after options

    submitted = st.form_submit_button("Submit Exam & Show Results")

# ---- EVALUATE & SHOW RESULTS ----
if submitted:
        # ---- CHECK FOR UNANSWERED ----
    unanswered_A = [f"A{i+1}" for i in range(len(sampleA)) if answers[f"A{i+1}"] is None]
    unanswered_B = [f"B{i+1}" for i in range(len(sampleB)) if answers[f"B{i+1}"] is None]

    if unanswered_A or unanswered_B:
        warning_msg = "You have not answered: "
        if unanswered_A:
            warning_msg += ", ".join(unanswered_A)
        if unanswered_A and unanswered_B:
            warning_msg += "; "
        if unanswered_B:
            warning_msg += ", ".join(unanswered_B)
        st.warning(warning_msg)
        st.stop()
