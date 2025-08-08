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

# ---- DISPLAY QUESTIONS SIDE-BY-SIDE ----
answers = {}
with st.form("exam_form"):
    colA, colB = st.columns(2)

    with colA:
        st.header("Section A — Radio Theory")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            st.markdown(f"**A{i+1}. {row['Question']}**")
            options = [f"A) {row['OptionA']}",
                       f"B) {row['OptionB']}",
                       f"C) {row['OptionC']}",
                       f"D) {row['OptionD']}"]
            answers[qkey] = st.radio(
                "",
                options,
                key=f"A_radio_{i}",
                index=None
            )

    with colB:
        st.header("Section B — Radio Regulations")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            st.markdown(f"**B{i+1}. {row['Question']}**")
            options = [f"A) {row['OptionA']}",
                       f"B) {row['OptionB']}",
                       f"C) {row['OptionC']}",
                       f"D) {row['OptionD']}"]
            answers[qkey] = st.radio(
                "",
                options,
                key=f"B_radio_{i}",
                index=None
            )

    submitted = st.form_submit_button("Submit Exam & Show Results")

# ---- EVALUATE & SHOW RESULTS ----
if submitted:
    # ---- CHECK FOR UNANSWERED ----
    unanswered_A = [f"A{i+1}" for i in range(len(sampleA)) if answers[f"A{i+1}"] is None]
    unanswered_B = [f"B{i+1}" for i in range(len(sampleB)) if answers[f"B{i+1}"] is None]

    if unanswered_A or unanswered_B:
        st.warning(
            "You have not answered: "
            + (", ".join(unanswered_A) if unanswered_A else "")
            + ("; " if unanswered_A and unanswered_B else "")
            + (", ".join(unanswered_B) if unanswered_B else "")
        )
        st.stop()

    # Helper: match picked option string to option letter
    def opt_label_from_choice(choice):
        return choice.split(")")[0] if choice else "?"

    # ---- RESULTS SIDE-BY-SIDE ----
    colA_res, colB_res = st.columns(2)

    # Section A
    correctA = 0
    with colA_res:
        st.subheader("Section A Results")
        for i, row in sampleA.iterrows():
            picked = answers[f"A{i+1}"]
            picked_label = opt_label_from_choice(picked)
            is_correct = (picked_label == str(row['Answer']))
            if is_correct:
                correctA += 1
            st.markdown(
                f"**A{i+1}.** {row['Question']}  \n"
                f"Your answer: **{picked_label or '—'}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {row['Answer']}"
            )
    percA = correctA / len(sampleA) * 100

    # Section B
    correctB = 0
    with colB_res:
        st.subheader("Section B Results")
        for i, row in sampleB.iterrows():
            picked = answers[f"B{i+1}"]
            picked_label = opt_label_from_choice(picked)
            is_correct = (picked_label == str(row['Answer']))
            if is_correct:
                correctB += 1
            st.markdown(
                f"**B{i+1}.** {row['Question']}  \n"
                f"Your answer: **{picked_label or '—'}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {row['Answer']}"
            )
    percB = correctB / len(sampleB) * 100

    # ---- GRAPHICAL SUMMARY ----
    st.markdown("---")
    st.header("Summary")

    def custom_progress(label, value, pass_mark=40):
        """
        value = percentage (0-100)
        pass_mark = threshold to pass (percentage)
        """
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

    # Section A
    custom_progress(f"Section A — {correctA}/{len(sampleA)}", percA)
    if percA < 40:
        st.error("❌ FAIL — Need at least 40% in Section A")
    else:
        st.success("✅ PASS in Section A")

    # Section B
    custom_progress(f"Section B — {correctB}/{len(sampleB)}", percB)
    if percB < 40:
        st.error("❌ FAIL — Need at least 40% in Section B")
    else:
        st.success("✅ PASS in Section B")

    # Overall
    total_correct = correctA + correctB
    total_questions = len(sampleA) + len(sampleB)
    total_perc = total_correct / total_questions * 100
    custom_progress(f"Overall — {total_correct}/{total_questions}", total_perc)

    if percA >= 40 and percB >= 40:
        st.success("🎉 Congratulations — You passed the ASOC mock test!")
    else:
        st.error("⚠ You did not meet the per-section pass criteria.")
