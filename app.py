import streamlit as st
import pandas as pd
import random
from pathlib import Path

st.set_page_config(page_title="GIAR ASOC Mock Test", layout="wide")

# --- FILE PATHS ---
LOGO_PATH = "logo_color_new_small.png"
SECTION_A_FILE = Path("sectionA_1000.xlsx")
SECTION_B_FILE = Path("sectionB_1000.xlsx")

# --- HELPER FUNCTIONS ---
def reset_session():
    """Resets all relevant session state variables."""
    st.session_state.answers = {}
    st.session_state.seed = random.randint(1, 10**9)
    st.session_state.generated_questions = False
    st.session_state.submitted = False

def generate_questions(df, n_questions, seed_offset, section_prefix):
    """
    Generates questions and their shuffled options for a given section.
    Returns: a tuple of (sample_df, options_map, correct_answers_map)
    """
    random.seed(st.session_state.seed + seed_offset)
    sample_df = df.sample(n=n_questions, random_state=st.session_state.seed + seed_offset).reset_index(drop=True)
    
    options_map = {}
    correct_answers_map = {}

    for i, row in sample_df.iterrows():
        qkey = f"{section_prefix}{i+1}"
        opts = [
            ("A", row['OptionA']),
            ("B", row['OptionB']),
            ("C", row['OptionC']),
            ("D", row['OptionD'])
        ]
        random.shuffle(opts)
        
        # Store the correct answer's index for later validation
        for new_label, opt_text in opts:
            if new_label == row['Answer']:
                correct_answers_map[qkey] = opts.index((new_label, opt_text))
        
        # Format options for display
        display_opts = [f"{chr(65+j)}) {opt_text}" for j, (_, opt_text) in enumerate(opts)]
        options_map[qkey] = display_opts

    return sample_df, options_map, correct_answers_map

# --- INITIAL SETUP ---
# Initialize session state variables if they don't exist
if "generated_questions" not in st.session_state:
    reset_session()
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- HEADER ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image(LOGO_PATH, width=120)
with col2:
    st.title("Gujarat Institute of Amateur Radio — ASOC Mock Test")
    st.caption("www.giar.org — App by Ruchir Purohit")
st.markdown("---")

# --- LOAD DATA (cached for performance) ---
@st.cache_data
def load_data():
    """Loads and cleans dataframes, caching them for faster reruns."""
    dfA = pd.read_excel(SECTION_A_FILE).drop_duplicates(subset=['Question'])
    dfB = pd.read_excel(SECTION_B_FILE).drop_duplicates(subset=['Question'])
    return dfA, dfB

dfA, dfB = load_data()

# --- GRADE SELECTION & NEW TEST BUTTON ---
st.selectbox(
    "Select Grade",
    ["Restricted (25 A + 25 B)", "General (50 A + 50 B)"],
    key="grade",
    on_change=reset_session
)
if st.button("Start New Test", key="new_test_button", type="secondary"):
    reset_session()
    st.rerun()

# --- QUESTION GENERATION (CONDITIONAL) ---
if not st.session_state.generated_questions:
    if "Restricted" in st.session_state.grade:
        nA, nB = 25, 25
    else:
        nA, nB = 50, 50
    
    sampleA, options_mapA, correct_answers_mapA = generate_questions(dfA, nA, 0, "A")
    sampleB, options_mapB, correct_answers_mapB = generate_questions(dfB, nB, 1, "B")
    
    # Store generated questions and maps in session state
    st.session_state.sampleA = sampleA
    st.session_state.sampleB = sampleB
    st.session_state.options_map = {**options_mapA, **options_mapB}
    st.session_state.correct_answers_map = {**correct_answers_mapA, **correct_answers_mapB}
    st.session_state.generated_questions = True
else:
    # Use existing data from session state
    sampleA = st.session_state.sampleA
    sampleB = st.session_state.sampleB
    options_map = st.session_state.options_map
    correct_answers_map = st.session_state.correct_answers_map

# --- CHEAT MODE ---
if st.button("💡 Cheat Mode (Fill All Correct Answers)"):
    for qkey, correct_idx in st.session_state.correct_answers_map.items():
        st.session_state.answers[qkey] = st.session_state.options_map[qkey][correct_idx]
    st.session_state.submitted = False # Don't show results yet
    st.rerun()

# --- EXAM FORM ---
with st.form("exam_form", clear_on_submit=False):
    colA, colB = st.columns(2)

    with colA:
        st.header("Section A — Radio Theory")
        for i, row in sampleA.iterrows():
            qkey = f"A{i+1}"
            st.markdown(f"**A{i+1}. {row['Question']}**")
            display_opts = options_map[qkey]
            index_val = display_opts.index(st.session_state.answers.get(qkey)) if qkey in st.session_state.answers else None
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
            st.markdown(f"**B{i+1}. {row['Question']}**")
            display_opts = options_map[qkey]
            index_val = display_opts.index(st.session_state.answers.get(qkey)) if qkey in st.session_state.answers else None
            choice = st.radio(
                "",
                display_opts,
                key=f"B_radio_{i}",
                index=index_val,
                label_visibility="collapsed"
            )
            st.session_state.answers[qkey] = choice
            st.write("")
    
    submitted = st.form_submit_button("✅ Submit Exam & Show Results", type="primary")
    if submitted:
        st.session_state.submitted = True
        st.rerun()

# --- RESULTS ---
if st.session_state.submitted:
    # Existing results logic here
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
            picked_answer_text = st.session_state.answers[qkey]
            picked_index = options_map[qkey].index(picked_answer_text)
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctA += 1
            st.markdown(
                f"**A{i+1}.** {row['Question']}  \n"
                f"Your answer: **{picked_answer_text}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percA = correctA / len(sampleA) * 100

    correctB = 0
    with colB_res:
        st.subheader("Section B Results")
        for i, row in sampleB.iterrows():
            qkey = f"B{i+1}"
            picked_answer_text = st.session_state.answers[qkey]
            picked_index = options_map[qkey].index(picked_answer_text)
            is_correct = (picked_index == correct_answers_map[qkey])
            if is_correct:
                correctB += 1
            st.markdown(
                f"**B{i+1}.** {row['Question']}  \n"
                f"Your answer: **{picked_answer_text}** — {'✅ Correct' if is_correct else '❌ Incorrect'}  \n"
                f"**Correct:** {options_map[qkey][correct_answers_map[qkey]]}"
            )
    percB = correctB / len(sampleB) * 100

    st.markdown("---")
    st.header("Summary")

    def custom_progress(label, value, pass_mark=40):
        # The HTML code remains the same as your original
        st.markdown(f"""
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
        """, unsafe_allow_html=True)

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
