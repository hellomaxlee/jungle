import streamlit as st
import random
from openai import OpenAI
import re

# Load OpenAI API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Generate MCQs with explanations for Chapter 1 ---
def generate_mcqs_with_explanations():
    prompt = """
You are a literary expert creating a highly specific and challenging quiz on Chapter 1 of *The Jungle* by Upton Sinclair.

Generate 4 multiple-choice questions. Each must:
- Be extremely specific to Chapter 1 (e.g., people, places, customs, settings) OR talk about general themes and use of rhetorical devices
- Include 4 answer choices (A–D)
- Identify the correct answer using "Answer: X"
- Provide a 3-4 sentence explanation after each correct answer

Use this exact format:

Q1: [question text]
A. ...
B. ...
C. ...
D. ...
Answer: X
Explanation: ...

Repeat for Q2 to Q4. No summaries or extra commentary.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- Parse output into questions, answers, and explanations ---
def parse_quiz(raw_text):
    questions = []
    answers = []
    explanations = []
    current_q = []

    for line in raw_text.splitlines():
        if line.startswith("Q") and current_q:
            questions.append("\n".join(current_q))
            current_q = [line]
        elif line.startswith("Answer:"):
            answers.append(line.split("Answer:")[1].strip())
        elif line.startswith("Explanation:"):
            explanations.append(line.split("Explanation:")[1].strip())
        else:
            current_q.append(line)

    if current_q:
        questions.append("\n".join(current_q))

    return questions, answers, explanations

# --- Format each question nicely ---
def format_question(text):
    text = re.sub(r"(Q\d+:)", r"**\1**", text)
    text = re.sub(r"\nA\.", r"\n- **A.**", text)
    text = re.sub(r"\nB\.", r"\n- **B.**", text)
    text = re.sub(r"\nC\.", r"\n- **C.**", text)
    text = re.sub(r"\nD\.", r"\n- **D.**", text)
    return text

# --- Streamlit UI ---
st.title("📘 The Jungle – Chapter 1 Quiz")

if st.button("🎲 Generate Quiz"):
    st.session_state.chapter = 1
    raw_quiz = generate_mcqs_with_explanations()
    questions, answers, explanations = parse_quiz(raw_quiz)
    st.session_state.questions = questions
    st.session_state.answers = answers
    st.session_state.explanations = explanations

# --- Display Quiz ---
if "questions" in st.session_state:
    for i, q in enumerate(st.session_state.questions):
        formatted_q = format_question(q)
        st.markdown(formatted_q, unsafe_allow_html=True)

    # --- User Answers ---
    user_answers = []
    for i in range(1, 5):
        ans = st.text_input(f"Your answer to Q{i} (A/B/C/D):", key=f"q{i}")
        user_answers.append(ans.strip().upper())

    # --- Check Answers + Show Explanations ---
    if st.button("✅ Check My Answers"):
        score = 0
        for i, (user, correct, explain) in enumerate(zip(user_answers, st.session_state.answers, st.session_state.explanations)):
            if user == correct:
                st.success(f"✅ Q{i+1} is correct!")
                score += 1
            else:
                st.error(f"❌ Q{i+1} is incorrect. Correct answer: {correct}")
            st.markdown(f"**Explanation:** {explain}")

        st.markdown(f"### Total Score: **{score} / 4 Points**")
