import streamlit as st
import pandas as pd
import random
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GIAR ASOC Mock Test", layout="wide")

# --- HEADER SECTION ---
logo_path = "logo_color_new_small.png"
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo_path, width=120)
with col2:
    st.title("Gujarat Institute of Amateur Radio — ASOC Mock Test")
    st.caption("www.giar.org — App by Ruchir Purohit")

st.markdown("---")

# --- DATA LOADING ---
sectionA_file = Path("sectionA_1000.xlsx")
sectionB_file = Path("sectionB_1000.xlsx")
try:
    dfA = pd.read_excel(sectionA_file)
    dfB = pd.read_excel(sectionB_file)
except FileNotFoundError:
    st.error("Error: The question files (sectionA_1000.xlsx or sectionB_1000.xlsx) were not found.")
    st.stop()

# --- SESSION STATE MANAGEMENT ---
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "seed" not in st.session_state:
    st.session_state.seed = random.randint(1, 10**9)

# --- USER INPUTS: GRADE SELECTION ---
grade = st.selectbox("Select Grade", ["Restricted (25 A + 25 B)", "General (50 A + 50 B)"])
if "Restricted" in grade:
    nA, nB = 25, 25
else:
    nA, nB = 50, 50

# --- RANDOM QUESTION SELECTION ---
random.seed(st.session_state.seed)
sampleA = dfA.sample(n=nA, random_state=st.session_state.seed).reset_index(drop=True)
sampleB = dfB.sample(n=nB, random_state=st.session_state.seed + 1).reset_index(drop=True)

# --- PRE-BUILD OPTIONS AND CORRECT ANSWERS MAPS ---
options_map = {}
correct_answers_map = {}

# Build Section A questions and options
for i, row in sampleA.iterrows():
    qkey = f"A{i+1}"
    opts = [
        ("A", row['OptionA']),
        ("B", row['OptionB']),
        ("C", row['OptionC']),
        ("D", row['OptionD'])
    ]
    shuffled_opts = opts[:]
    random.shuffle(shuffled_opts)
    
    for idx, (label, text) in enumerate(shuffled_opts):
        if label == row['Answer']:
            correct_answers_map[qkey] = idx
            break
            
    display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(shuffled_opts)]
    options_map[qkey] = display_opts

# Build Section B questions and options
for i, row in sampleB.iterrows():
    qkey = f"B{i+1}"
    opts = [
        ("A", row['OptionA']),
        ("B", row['OptionB']),
        ("C", row['OptionC']),
        ("D", row['OptionD'])
    ]
    shuffled_opts = opts[:]
    random.shuffle(shuffled_opts)

    for idx, (label, text) in enumerate(shuffled_opts):
        if label == row['Answer']:
            correct_answers_map[qkey] = idx
            break

    display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(shuffled_opts)]
    options_map[qkey] = display_opts

# --- CHEAT MODE BUTTON (REVISED) ---
# This button now directly updates the session state and forces a full rerun.
if st.button("💡 Cheat Mode (Fill All Correct Answers)", key="cheat_button"):
    st.success("Cheat Mode activated — all correct answers filled!")
    for qkey, correct_idx in correct_answers_map.items():
        st.session_state.answers[qkey] = options_map[qkey][correct_idx]
    st.rerun()

# --- EXAM QUESTIONS DISPLAY (FORM REMOVED) ---
colA, colB = st.columns(2)

with colA:
    st.header("Section A — Radio Theory")
    for i, row in sampleA.iterrows():
        qkey = f"A{i+1}"
        st.markdown(f"**A{i+1}.** {row['Question']}")
        display_opts = options_map[qkey]

        user_answer = st.session_state.answers.get(qkey)
        index_val = display_opts.index(user_answer) if user_answer in display_opts else None

        choice = st.radio(
            "",
            display_opts,
            key=f"A_radio_{i}",
            index=index_val,
            label_visibility="collapsed"
        )
        st.session_state.answers[qkey] = choice
        st.write("")

with colB:
    st.header("Section B — Radio Regulations")
    for i, row in sampleB.iterrows():
        qkey = f"B{i+1}"
        st.markdown(f"**B{i+1}.** {row['Question']}")
        display_opts = options_map[qkey]

        user_answer = st.session_state.answers.get(qkey)
        index_val = display_opts.index(user_answer) if user_answer in display_opts else None
        
        choice = st.radio(
            "",
            display_opts,
            key=f"B_radio_{i}",
            index=index_val,
            label_visibility="collapsed"
        )
        st.session_state.answers[qkey] = choice
        st.write("")

# --- SUBMIT BUTTON (OUTSIDE OF FORM) ---
submitted = st.button("Submit Exam & Show Results", key="submit_button")


# --- RESULTS SECTION ---
if submitted:
    unanswered_A = [f"A{i+1}" for i in range(len(sampleA)) if not st.session_state.answers.get(f"A{i+1}")]
    unanswered_B = [f"B{i+1}" for i in range(len(sampleB)) if not st.session_state.answers.get(f"B{i+1}")]

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

    colA_res, colB_res = st.columns(2)

    correctA = 0
    with colA_res:
        st.subheader("Section A Results")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            picked_index = options_map[qkey].index(st.session_state.answers[qkey])
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctA += 1
            st.markdown(
                f"**A{i+1}.** {row['Question']}  \n"
                f"Your answer: **{st.session_state.answers[qkey]}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percA = correctA / len(sampleA) * 100

    correctB = 0
    with colB_res:
        st.subheader("Section B Results")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            picked_index = options_map[qkey].index(st.session_state.answers[qkey])
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctB += 1
            st.markdown(
                f"**B{i+1}.** {row['Question']}  \n"
                f"Your answer: **{st.session_state.answers[qkey]}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percB = correctB / len(sampleB) * 100

    st.markdown("---")
    st.header("Summary")

    def custom_progress(label, value, pass_mark=40):
        bar_html = f"""
        <div style="margin-bottom: 10px;">
            <div style="font-weight: bold;">{label}: {value:.1f}%</div>
            <div style="position: relative; background-color: #ddd; height: 24px; border-radius: 12px; overflow: hidden;">
                <div style="width: {value}%; background-color: {'#4caf50' if value >= pass_mark else '#f44336'}; height: 100%;"></div>
                <div style="position: absolute; left: {pass_mark}%; top: 0; bottom: 0; border-left: 2px dashed red;"></div>
                <div style="position: absolute; width: 100%; text-align: center; line-height: 24px; font-weight: bold; color: black;">
                    {value:.1f}%
                </div>
            </div>
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)

    custom_progress(f"Section A — {correctA}/{len(sampleA)}", percA)
    st.success("✅ PASS in Section A" if percA >= 40 else "❌ FAIL — Need at least 40% in Section A")

    custom_progress(f"Section B — {correctB}/{len(sampleB)}", percB)
    st.success("✅ PASS in Section B" if percB >= 40 else "❌ FAIL — Need at least 40% in Section B")

    total_correct = correctA + correctB
    total_questions = len(sampleA) + len(sampleB)
    total_perc = total_correct / total_questions * 100
    custom_progress(f"Overall — {total_correct}/{total_questions}", total_perc)

    if percA >= 40 and percB >= 40:
        st.balloons()
        st.success("🎉 Congratulations — You passed the ASOC mock test!")
    else:
        st.error("⚠ You did not meet the per-section pass criteria.")
