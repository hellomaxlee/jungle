import streamlit as st
from openai import OpenAI
import re

# Load OpenAI API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Generate MCQs with explanations for the Introduction ---
def generate_mcqs_with_explanations():
    prompt = """
You are a literary expert creating a detailed and challenging quiz based **only** on the **Introduction** of *How the Other Half Lives* by Jacob Riis.

Generate 4 multiple-choice questions. Each must:
- Be highly specific to the Introduction (not the rest of the book)
- Reference specific details
- Be extremely challenging or tricky
- Include 4 answer choices labeled A–D
- Identify the correct answer using "Answer: X"
- Follow with a 3–4 sentence explanation for the correct answer

Use this exact format:

Q1: [question]
A. ...
B. ...
C. ...
D. ...
Answer: X
Explanation: ...

Repeat for Q2 to Q4. Do not include summaries, quotes, or extra commentary.
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

# --- Parse GPT output into questions, answers, explanations ---
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

# --- Format for markdown ---
def format_question(text):
    text = re.sub(r"(Q\d+:)", r"**\1**", text)
    text = re.sub(r"\nA\.", r"\n- **A.**", text)
    text = re.sub(r"\nB\.", r"\n- **B.**", text)
    text = re.sub(r"\nC\.", r"\n- **C.**", text)
    text = re.sub(r"\nD\.", r"\n- **D.**", text)
    return text

# --- UI ---
st.set_page_config(page_title="📸 How the Other Half Lives – Quiz", layout="centered")
st.title("📸 Quiz on *How the Other Half Lives* – Introduction")
st.write("Test your understanding of the **Introduction** to Jacob Riis’s groundbreaking book. All questions are based **only on the Introduction**, not the rest of the text.")

# Generate quiz
if st.button("Generate Quiz"):
    raw_quiz = generate_mcqs_with_explanations()
    questions, answers, explanations = parse_quiz(raw_quiz)
    st.session_state.questions = questions
    st.session_state.answers = answers
    st.session_state.explanations = explanations

# Display quiz
if "questions" in st.session_state:
    st.subheader("Quiz")
    for i, q in enumerate(st.session_state.questions):
        formatted_q = format_question(q)
        st.markdown(formatted_q, unsafe_allow_html=True)

    user_answers = []
    for i in range(1, 5):
        ans = st.text_input(f"Your answer to Q{i} (A/B/C/D):", key=f"q{i}")
        user_answers.append(ans.strip().upper())

    if st.button("Check My Answers"):
        score = 0
        for i, (user, correct, explanation) in enumerate(zip(user_answers, st.session_state.answers, st.session_state.explanations)):
            if user == correct:
                st.success(f"✅ Q{i+1} is correct!")
                score += 1
            else:
                st.error(f"❌ Q{i+1} is incorrect. Correct answer: {correct}")
            st.markdown(f"**Explanation:** {explanation}")

        if score == 4:
            st.markdown("🏆 **You earned 2 game points!**")
        elif score == 3:
            st.markdown("✅ **You earned 1 game point.**")
        else:
            st.markdown("❌ **You earned 0 game points.**")
