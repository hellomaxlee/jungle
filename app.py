import streamlit as st
import random
from openai import OpenAI

# Load OpenAI API key
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# --- Function to generate 4 extremely challenging MCQs ---
def generate_mcqs(chapter_num):
    prompt = f"""
You are a literary expert creating a difficult quiz on Chapter {chapter_num} of *The Jungle* by Upton Sinclair.

Generate 4 multiple-choice questions. Each question must:
- Be extremely challenging and test deep understanding of Chapter {chapter_num}
- Include 4 answer choices labeled A, B, C, and D

Format your response exactly like:

Q1: [question]
A. ...
B. ...
C. ...
D. ...

(Repeat for Q2 through Q4)
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

# --- Streamlit App ---
st.title("📘 The Jungle Quiz Challenge")
st.write("Test your knowledge of *The Jungle* by Upton Sinclair with 4 extremely challenging questions from a random chapter.")

if st.button("🎲 Generate Random Quiz"):
    chapter_num = random.randint(1, 31)
    st.session_state.chapter = chapter_num
    st.session_state.quiz = generate_mcqs(chapter_num)

# Show the quiz
if "quiz" in st.session_state:
    st.subheader(f"📖 Chapter {st.session_state.chapter}")
    st.code(st.session_state.quiz)

    # Capture user answers
    user_answers = []
    for i in range(1, 5):
        ans = st.text_input(f"Your answer to Q{i} (A/B/C/D):", key=f"q{i}")
        user_answers.append(ans.strip().upper())

    # Check answers
    if st.button("✅ Check My Answers"):
        correct_lines = [line for line in st.session_state.quiz.splitlines() if line.startswith("Answer: ")]
        if len(correct_lines) < 4:
            st.error("Could not parse answers correctly. Try generating the quiz again.")
        else:
            for i, correct_line in enumerate(correct_lines):
                correct = correct_line.split("Answer: ")[1].strip()
                user = user_answers[i]
                if user == correct:
                    st.success(f"✅ Q{i+1} is correct!")
                else:
                    st.error(f"❌ Q{i+1} is incorrect. Correct answer: {correct}")
