# app.py
import streamlit as st
import pandas as pd
import random
from pathlib import Path

st.set_page_config(page_title="GIAR Mock ASOC Test", page_icon="📻", layout="centered")

# --- Configuration ---
SECTION_A_FILE = "Section_A_1000_questions.xlsx"
SECTION_B_FILE = "Section_B_1000_questions.xlsx"
LOGO_FILE = "logo_color_new_small.png"  # your uploaded logo filename
PASS_PERCENT = 40  # passing criterion per section (in percent)

# --- Helpers ---
def load_questions_from_excel(path):
    """Load dataframe and validate columns."""
    df = pd.read_excel(path)
    expected_cols = ["Question", "Option A", "Option B", "Option C", "Option D", "Answer"]
    if not all(col in df.columns for col in expected_cols):
        missing = [c for c in expected_cols if c not in df.columns]
        raise ValueError(f"Excel file {path} missing columns: {missing}")
    df = df[expected_cols].dropna(subset=["Question"]).reset_index(drop=True)
    return df

def sample_questions(df, n):
    if n >= len(df):
        return df.sample(frac=1).reset_index(drop=True)
    return df.sample(n=n).reset_index(drop=True)

def shuffle_options(row):
    opts = [("Option A", row["Option A"]), ("Option B", row["Option B"]),
            ("Option C", row["Option C"]), ("Option D", row["Option D"])]
    random.shuffle(opts)
    labels = ["A", "B", "C", "D"]
    mapping = {}
    for new_label, (_, text) in zip(labels, opts):
        mapping[f"Opt_{new_label}"] = text
    # find new correct answer label
    correct_text = row["Answer"]
    correct_label = None
    for new_label in labels:
        if mapping[f"Opt_{new_label}"] == correct_text:
            correct_label = new_label
            break
    return mapping, correct_label

# --- UI ---
st.sidebar.title("GIAR Mock Test")
st.sidebar.markdown("Gujarat Institute of Amateur Radio — Mock ASOC Test")
st.sidebar.markdown("[www.giar.org](https://www.giar.org)")

# Logo + header
col1, col2 = st.columns([1,8])
with col1:
    if Path(LOGO_FILE).exists():
        st.image(LOGO_FILE, width=90)
    else:
        st.write("")  # no logo found
with col2:
    st.title("GIAR — Mock ASOC Exam")
    st.caption("App designed by Ruchir Purohit")

# Load or upload question banks
st.write("---")
st.header("Question bank / Admin")
st.info("You can either keep Excel files (`Section_A_1000_questions.xlsx`, `Section_B_1000_questions.xlsx`) in the app folder, or upload replacements here.")

colu1, colu2 = st.columns(2)
with colu1:
    st.write("**Section A file (Radio Theory)**")
    uploaded_a = st.file_uploader("Upload Section A Excel", type=["xlsx"], key="up_a")
with colu2:
    st.write("**Section B file (Radio Regulations)**")
    uploaded_b = st.file_uploader("Upload Section B Excel", type=["xlsx"], key="up_b")

if uploaded_a:
    df_a = pd.read_excel(uploaded_a)
    df_a.to_excel(SECTION_A_FILE, index=False)
    st.success(f"Saved uploaded Section A to `{SECTION_A_FILE}`")
if uploaded_b:
    df_b = pd.read_excel(uploaded_b)
    df_b.to_excel(SECTION_B_FILE, index=False)
    st.success(f"Saved uploaded Section B to `{SECTION_B_FILE}`")

# Attempt to load question banks
load_error = False
try:
    if Path(SECTION_A_FILE).exists():
        df_section_a = load_questions_from_excel(SECTION_A_FILE)
    else:
        df_section_a = pd.DataFrame(columns=["Question","Option A","Option B","Option C","Option D","Answer"])
    if Path(SECTION_B_FILE).exists():
        df_section_b = load_questions_from_excel(SECTION_B_FILE)
    else:
        df_section_b = pd.DataFrame(columns=["Question","Option A","Option B","Option C","Option D","Answer"])
except Exception as e:
    st.error(f"Error loading Excel files: {e}")
    df_section_a = pd.DataFrame()
    df_section_b = pd.DataFrame()
    load_error = True

st.write(f"Loaded Section A questions: **{len(df_section_a)}**, Section B questions: **{len(df_section_b)}**")

st.write("---")
st.header("Start a Practice Exam")

# Choose grade
grade = st.radio("Select candidate type", ("Restricted Grade", "General Grade"))
if grade == "Restricted Grade":
    n_per_section = 25
else:
    n_per_section = 50

st.markdown(f"**This test will show {n_per_section} questions from Section A and {n_per_section} from Section B.**")

# Random seed option
randomize_seed = st.checkbox("Use random seed (different each time)", value=True)
if not randomize_seed:
    seed_val = st.number_input("Seed (integer)", min_value=0, value=42)
else:
    seed_val = None

start_test = st.button("Generate Test")

if start_test:
    if load_error:
        st.error("Cannot start test: failed to load question banks.")
    elif len(df_section_a) < n_per_section or len(df_section_b) < n_per_section:
        st.error(f"Not enough questions in one or both sections. Need at least {n_per_section} in each.")
    else:
        # Prepare test
        if seed_val is not None:
            random.seed(int(seed_val))
        else:
            random.seed()

        # sample
        sampled_a = sample_questions(df_section_a, n_per_section).copy()
        sampled_b = sample_questions(df_section_b, n_per_section).copy()

        # prepare structure to hold randomized options and correct labels
        exam_questions = []

        for idx, row in sampled_a.iterrows():
            mapping, correct_label = shuffle_options(row)
            exam_questions.append({
                "section": "A",
                "qnum": f"A{idx+1}",
                "question": row["Question"],
                "opts": mapping,
                "correct": correct_label
            })
        for idx, row in sampled_b.iterrows():
            mapping, correct_label = shuffle_options(row)
            exam_questions.append({
                "section": "B",
                "qnum": f"B{idx+1}",
                "question": row["Question"],
                "opts": mapping,
                "correct": correct_label
            })

        # Shuffle overall order keeping section tags (if you want section order separated you can skip)
        random.shuffle(exam_questions)

        # Store exam in session state
        st.session_state["current_exam"] = exam_questions
        st.session_state["n_per_section"] = n_per_section
        st.session_state["grade"] = grade

        st.success("Test generated. Scroll down to take the test.")

# Render test if present
if "current_exam" in st.session_state:
    st.write("---")
    st.subheader(f"Mock Test — {st.session_state['grade']}")
    st.write("Answer all questions then click **Submit**. Correct answers and result will show immediately.")
    form = st.form("exam_form")
    answers = {}
    q_index = 0
    for q in st.session_state["current_exam"]:
        q_index += 1
        with form.container():
            st.markdown(f"**Q{q_index}** ({q['section']}) {q['question']}")
            # options displayed in A-D order
            opts = [
                ("A", q["opts"]["Opt_A"]),
                ("B", q["opts"]["Opt_B"]),
                ("C", q["opts"]["Opt_C"]),
                ("D", q["opts"]["Opt_D"]),
            ]
            # radio key must be unique
            key = f"resp_{q_index}"
            choice = form.radio("", [f"{lbl}) {txt}" for lbl, txt in opts], key=key, index=0)
            # store only label (A/B/C/D)
            answers[str(q_index)] = choice.split(")")[0]
    submitted = form.form_submit_button("Submit")

    if submitted:
        total = len(st.session_state["current_exam"])
        correct_count = 0
        correct_a = 0
        correct_b = 0
        total_a = sum(1 for q in st.session_state["current_exam"] if q["section"]=="A")
        total_b = sum(1 for q in st.session_state["current_exam"] if q["section"]=="B")

        # Build per-question result structure
        results = []
        for i, q in enumerate(st.session_state["current_exam"], start=1):
            user_label = answers.get(str(i))
            correct_label = q["correct"]
            is_correct = (user_label == correct_label)
            if is_correct:
                correct_count += 1
                if q["section"] == "A":
                    correct_a += 1
                else:
                    correct_b += 1
            results.append({
                "index": i,
                "section": q["section"],
                "question": q["question"],
                "user": user_label,
                "correct": correct_label,
                "opts": q["opts"],
                "is_correct": is_correct
            })

        # Scores
        pct_a = (correct_a / total_a) * 100 if total_a>0 else 0
        pct_b = (correct_b / total_b) * 100 if total_b>0 else 0
        overall_pct = (correct_count / total) * 100 if total>0 else 0

        st.write("## Results")
        st.metric("Section A (Radio Theory) score", f"{correct_a} / {total_a} ({pct_a:.1f}%)", delta=None)
        st.metric("Section B (Radio Regulations) score", f"{correct_b} / {total_b} ({pct_b:.1f}%)", delta=None)
        st.metric("Overall", f"{correct_count} / {total} ({overall_pct:.1f}%)", delta=None)

        pass_a = pct_a >= PASS_PERCENT
        pass_b = pct_b >= PASS_PERCENT
        if pass_a and pass_b:
            st.success(f"PASS — You have >= {PASS_PERCENT}% in both sections.")
        else:
            st.error(f"FAIL — You must score at least {PASS_PERCENT}% in each section to pass. Section A pass: {pass_a}, Section B pass: {pass_b}")

        st.write("---")
        st.subheader("Per-question feedback")
        for r in results:
            if r["is_correct"]:
                st.markdown(f"✅ **Q{r['index']} ({r['section']})** — {r['question']}")
                st.write(f"Your answer: **{r['user']}** | Correct: **{r['correct']}**")
            else:
                st.markdown(f"❌ **Q{r['index']} ({r['section']})** — {r['question']}")
                st.write(f"Your answer: **{r['user']}** | Correct: **{r['correct']}**")
            # Show options with highlight
            opts_display = []
            for lbl in ["A","B","C","D"]:
                text = r["opts"][f"Opt_{lbl}"]
                if lbl == r["correct"]:
                    opts_display.append(f"**{lbl}) {text}** ✅")
                elif lbl == r["user"]:
                    opts_display.append(f"~~{lbl}) {text}~~ ❌")
                else:
                    opts_display.append(f"{lbl}) {text}")
            st.write(";  ".join(opts_display))
            st.write("---")

        # clear exam so a new one can be generated
        st.session_state.pop("current_exam", None)

st.write("")
st.markdown("---")
st.caption("Gujarat Institute of Amateur Radio — www.giar.org · App designed by Ruchir Purohit")
