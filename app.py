# app.py
import streamlit as st
import pandas as pd
import random
from pathlib import Path

st.set_page_config(page_title="GIAR ASOC Mock Test", layout="centered")

# ---- HEADER WITH LOGO AND CREDITS ----
logo_path = "logo_color_new_small.png"
col1, col2 = st.columns([1,5])
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
    seed = random.randint(1,10**9)
    st.session_state["seed"] = seed
random.seed(seed)

sampleA = dfA.sample(n=nA, random_state=seed).reset_index(drop=True)
sampleB = dfB.sample(n=nB, random_state=seed+1).reset_index(drop=True)

st.info("Exam layout: Section A (Radio Theory) first, then Section B (Radio Regulations). Numbering restarts per section.")

# ---- DISPLAY QUESTIONS ----
answers = {}
with st.form("exam_form"):
    st.header("Section A — Radio Theory")
    for i, row in sampleA.iterrows():
        qkey = f"A{i+1}"
        st.markdown(f"**A{i+1}. {row['Question']}**")
        answers[qkey] = st.radio(
            "",
            (row['OptionA'], row['OptionB'], row['OptionC'], row['OptionD']),
            key=f"A_radio_{i}", index=0
        )
    st.markdown("---")
    st.header("Section B — Radio Regulations")
    for i, row in sampleB.iterrows():
        qkey = f"B{i+1}"
        st.markdown(f"**B{i+1}. {row['Question']}**")
        answers[qkey] = st.radio(
            "",
            (row['OptionA'], row['OptionB'], row['OptionC'], row['OptionD']),
            key=f"B_radio_{i}", index=0
        )
    submitted = st.form_submit_button("Submit Exam & Show Results")

# ---- EVALUATE & SHOW RESULTS ----
if submitted:
    def opt_label_for_text(row, text):
        if text == row['OptionA']: return "A"
        if text == row['OptionB']: return "B"
        if text == row['OptionC']: return "C"
        if text == row['OptionD']: return "D"
        return "?"

    # Section A
    correctA = 0
    st.subheader("Section A Results")
    for i, row in sampleA.iterrows():
        picked = answers[f"A{i+1}"]
        picked_label = opt_label_for_text(row, picked)
        is_correct = (picked_label == str(row['Answer']))
        if is_correct: correctA += 1
        st.markdown(
            f"**A{i+1}.** {row['Question']}  \n"
            f"Your answer: **{picked_label}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
            f"**Correct:** {row['Answer']}"
        )
    percA = correctA / len(sampleA) * 100

    # Section B
    correctB = 0
    st.subheader("Section B Results")
    for i, row in sampleB.iterrows():
        picked = answers[f"B{i+1}"]
        picked_label = opt_label_for_text(row, picked)
        is_correct = (picked_label == str(row['Answer']))
        if is_correct: correctB += 1
        st.markdown(
            f"**B{i+1}.** {row['Question']}  \n"
            f"Your answer: **{picked_label}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
            f"**Correct:** {row['Answer']}"
        )
    percB = correctB / len(sampleB) * 100

    # ---- SUMMARY ----
    st.markdown("---")
    st.header("Summary")
    st.write(f"Section A: {correctA} / {len(sampleA)}  ({percA:.1f}%)  — {'PASS' if percA>=40 else 'FAIL'}")
    st.write(f"Section B: {correctB} / {len(sampleB)}  ({percB:.1f}%)  — {'PASS' if percB>=40 else 'FAIL'}")
    total_correct = correctA + correctB
    total_questions = len(sampleA) + len(sampleB)
    total_perc = total_correct / total_questions * 100
    st.write(f"Overall: {total_correct} / {total_questions}  ({total_perc:.1f}%)")

    if percA >= 40 and percB >= 40:
        st.success("Congratulations — you passed the per-section pass criteria!")
    else:
        st.error("You did not meet the per-section pass criteria. At least 40% is required in each section.")

    st.caption("Question bank maintained in sectionA_1000.xlsx and sectionB_1000.xlsx in the app folder. Edit them to change/add questions.")
