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

# Store correct answers and shuffled options
correct_answers_map = {}
options_map = {}
answers = {}

with st.form("exam_form"):
    colA, colB = st.columns(2)

    with colA:
        st.header("Section A — Radio Theory")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            st.markdown(f"**A{i+1}. {row['Question']}**")

            # Prepare options and shuffle
            opts = [
                ("A", row['OptionA']),
                ("B", row['OptionB']),
                ("C", row['OptionC']),
                ("D", row['OptionD'])
            ]
            random.shuffle(opts)

            # Store correct answer index
            for new_label, opt_text in opts:
                if new_label == row['Answer']:
                    correct_answers_map[qkey] = opts.index((new_label, opt_text))

            # Display options with A) etc.
            display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(opts)]
            options_map[qkey] = display_opts  # store shuffled options

            answers[qkey] = st.radio(
                "",
                display_opts,
                key=f"A_radio_{i}",
                index=None if qkey not in answers else display_opts.index(answers[qkey]),
                label_visibility="collapsed"
            )
            st.markdown("&nbsp;", unsafe_allow_html=True)  # spacing after options

    with colB:
        st.header("Section B — Radio Regulations")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            st.markdown(f"**B{i+1}. {row['Question']}**")

            # Prepare options and shuffle
            opts = [
                ("A", row['OptionA']),
                ("B", row['OptionB']),
                ("C", row['OptionC']),
                ("D", row['OptionD'])
            ]
            random.shuffle(opts)

            # Store correct answer index
            for new_label, opt_text in opts:
                if new_label == row['Answer']:
                    correct_answers_map[qkey] = opts.index((new_label, opt_text))

            # Display options with A) etc.
            display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(opts)]
            options_map[qkey] = display_opts  # store shuffled options

            answers[qkey] = st.radio(
                "",
                display_opts,
                key=f"B_radio_{i}",
                index=None if qkey not in answers else display_opts.index(answers[qkey]),
                label_visibility="collapsed"
            )
            st.markdown("&nbsp;", unsafe_allow_html=True)

    # ---- CHEAT MODE BUTTON ----
    if st.form_submit_button("💡 Cheat Mode (Fill All Correct Answers)"):
        for qkey in options_map:
            correct_idx = correct_answers_map[qkey]
            answers[qkey] = options_map[qkey][correct_idx]

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

    colA_res, colB_res = st.columns(2)

    correctA = 0
    with colA_res:
        st.subheader("Section A Results")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            picked_index = options_map[qkey].index(answers[qkey])
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctA += 1
            st.markdown(
                f"**A{i+1}.** {row['Question']}  \n"
                f"Your answer: **{answers[qkey]}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percA = correctA / len(sampleA) * 100

    correctB = 0
    with colB_res:
        st.subheader("Section B Results")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            picked_index = options_map[qkey].index(answers[qkey])
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctB += 1
            st.markdown(
                f"**B{i+1}.** {row['Question']}  \n"
                f"Your answer: **{answers[qkey]}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percB = correctB / len(sampleB) * 100

    # ---- GRAPHICAL SUMMARY ----
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
        st.success("🎉 Congratulations — You passed the ASOC mock test!")
    else:
        st.error("⚠ You did not meet the per-section pass criteria.")
