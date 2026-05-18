import streamlit as st

from database.db import add_ai_plan

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Load environment variables
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
client = InferenceClient(
    provider="novita",
    api_key=os.getenv("HF_API_KEY")
)

# Custom CSS styling for strict dark mode rules
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
p, div, span, label {
    color: #A0A0A0 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("AI Study Planner")

# Input field
syllabus = st.text_area("Paste your syllabus or topics here", height=200, key="syllabus_input")

# Numeric inputs in columns
col1, col2 = st.columns(2)
with col1:
    study_days = st.number_input("Study days available", min_value=1, max_value=90, value=7)
with col2:
    hours_per_day = st.number_input("Hours per day", min_value=1, max_value=12, value=3)

# Button to trigger plan generation
if st.button("Generate Study Plan"):
    if not syllabus.strip():
        st.error("Please enter your syllabus or topics.")
    else:
        system_prompt = (
            "You are an expert academic study planner. Create a detailed, structured day-by-day study plan. \n"
            "Format your response as plain text with clear day headings like 'Day 1:', 'Day 2:' etc. \n"
            "List specific topics and time allocations for each day. \n"
            "Be practical and realistic. No markdown formatting, no bold, no bullet symbols."
        )
        
        user_message = (
            f"Create a study plan for the following syllabus:\n{syllabus}\n\n"
            f"Available days: {study_days}\nHours per day: {hours_per_day}\n\n"
            f"Create a complete day-by-day schedule."
        )
        
        try:
            with st.spinner("Generating your study plan..."):
                full_prompt = f"{system_prompt}\n\n{user_message}"
                response = client.chat.completions.create(
                    model="meta-llama/llama-3.1-8b-instruct",
                    max_tokens=1000,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ]
                )
                result_text = response.choices[0].message.content

            # Display plan inside a styled container
            st.markdown(f"""
            <div style="background-color: #161B22; border: 1px solid #2A2F36; border-radius: 8px; padding: 20px; color: #FFFFFF !important; white-space: pre-wrap;">
{result_text}
            </div>
            """, unsafe_allow_html=True)
            
            # Save to database
            add_ai_plan(user_id, syllabus, result_text)
            st.success("Plan saved!")
            
        except Exception as e:
            st.error(f"Error calling AI service: {e}")
