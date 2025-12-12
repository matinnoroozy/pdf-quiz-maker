import streamlit as st 
import random 
import pdfplumber 
import pandas as pd 
import matplotlib.pyplot as plt
import time

st.title("Create question from pdf")

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers_submitted' not in st.session_state:
    st.session_state.answers_submitted = {}

uploaded_file = st.file_uploader("upload your file", type=["pdf"])

def extract_pdf_text(uploaded_pdf):
    text = ""
    with pdfplumber.open(uploaded_pdf) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + " "
    return text 

def generate_question(sentence):
    words = sentence.split()
    if len(words) < 5:
        return None 
    idx = random.randint(0, len(words)-1)
    answer = words[idx].strip(".,!?").lower()
    if len(answer) < 4:
        return None
    words[idx] = "_"*len(answer)
    question = " ".join(words)
    return question, answer
    
def grade_answer(student_answer, correct_answer):
    if student_answer.lower().strip() == correct_answer.lower().strip():
        score = 1 
        feedback = "Correct"
    else:
        score = 0 
        feedback = "Wrong"
    return score, feedback

def save_result(question, student_answer, answer, score):
    df = pd.DataFrame([{
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "question": question,
        "student_answer": student_answer,
        "correct_answer": answer,
        "score": score
    }])
    try:
        old = pd.read_csv("results.csv")
        df = pd.concat([old, df], ignore_index=True)
    except:
        pass 
    df.to_csv("results.csv", index=False)

if uploaded_file:
    st.success("Your file uploaded!")
    
    # Extract text and create sentences only once
    if 'text_extracted' not in st.session_state:
        text = extract_pdf_text(uploaded_file)
        sentences = []
        for s in text.split("."):
            if len(s.split()) > 6 and len(s.split()) < 30:
                sentences.append(s)
        st.session_state.sentences = sentences
        st.session_state.text_extracted = True
    
    num_q = st.slider("Please select the number of questions ", 1, 10, 3)
    
    # Generate questions button
    if st.button("Generate Questions"):
        st.session_state.questions = []
        st.session_state.answers_submitted = {}
        for i in range(num_q):
            sentence = random.choice(st.session_state.sentences)
            q = generate_question(sentence)
            if q:
                st.session_state.questions.append(q)
    
    # Display questions
    if st.session_state.questions:
        st.subheader("Generated Questions")
        
        for i, (question, answer) in enumerate(st.session_state.questions):
            st.write(f"#### Question {i+1}: {question}")
            
            # Create unique key for each question
            answer_key = f"answer_{i}"
            student_answer = st.text_input(f"Answer for question {i+1}", key=answer_key)
            
            # Submit button for each question
            if st.button(f"Submit Answer {i+1}", key=f"submit_{i}"):
                if student_answer:
                    score, feedback = grade_answer(student_answer, answer)
                    st.session_state.answers_submitted[i] = {
                        'score': score,
                        'feedback': feedback,
                        'student_answer': student_answer
                    }
                    save_result(question, student_answer, answer, score)
            
            # Show feedback if answer was submitted
            if i in st.session_state.answers_submitted:
                result = st.session_state.answers_submitted[i]
                st.write(f"**Your answer:** {result['student_answer']}")
                st.write(f"**Correct answer:** {answer}")
                st.write(f"**Score:** {result['score']}")
                st.write(f"**Feedback:** {result['feedback']}")
                st.markdown("---")

st.subheader("Progress Result")
try:
    df = pd.read_csv("results.csv")
    st.line_chart(df["score"])
    st.dataframe(df)
except:
    st.info("You do not have any data yet")