import streamlit as st
import random
from openai import OpenAI
import re

# Load OpenAI API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Function to generate MCQs ---
def generate_mcqs(chapter_num):
    prompt = f"""
You are a literary expert creating a difficult quiz on Chapter {chapter_num} of *The Jungle* by Upton Sinclair.

Generate 4 multiple-choice questions. Each question must:
- Be extremely challenging and test deep understanding of Chapter {chapter_num}
- Include 4 answer choices labeled A, B, C, and D
- Clearly indicate the correct answer using the format "Answer: X"

Format exactly like:

Q1: [question text]
A. ...
B. ...
C. ...
D. ...
Answer: X

(Repeat for Q2–Q4)
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=900
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Function to split quiz and extract answers ---
def parse_quiz(raw_text):
    questions = []
    answers = []
    current_question = []

    for line in raw_text.splitlines():
        if line.startswith("Q") and current_question:
            questions.append("\n".join(current_question))
            current_question = [line]
        elif line.startswith("Answer:"):
            answers.append(line.split("Answer:")[1].strip())
        else:
            current_question.append(line)

    if current_question:
        questions.append("\n".join(current_question))

    return questions, answers

# --- Streamlit App UI ---
st.title("📘 The Jungle Quiz Challenge")
st.write("Test your knowledge of *The Jungle* by Upton Sinclair with 4 extremely challenging questions from a random chapter.")

if st.button("🎲 Generate Random Quiz"):
    chapter_num = random.randint(1, 31)
    st.session_state.chapter = chapter_num
    raw_quiz = generate_mcqs(chapter_num)
    questions, answers = parse_quiz(raw_quiz)
    st.session_state.questions = questions
    st.session_state.answers = answers

# --- Display Questions ---
if "questions" in st.session_state:
    st.subheader(f"📖 Chapter {st.session_state.chapter}")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}**:\n\n{q}", unsafe_allow_html=False)

    # --- Capture User Answers ---
    user_answers = []
    for i in range(1, 5):
        ans = st.text_input(f"Your answer to Q{i} (A/B/C/D):", key=f"q{i}")
        user_answers.append(ans.strip().upper())

    # --- Check User Answers ---
    if st.button("✅ Check My Answers"):
        for i, (user, correct) in enumerate(zip(user_answers, st.session_state.answers)):
            if user == correct:
                st.success(f"✅ Q{i+1} is correct!")
            else:
                st.error(f"❌ Q{i+1} is incorrect. Correct answer: {correct}")

