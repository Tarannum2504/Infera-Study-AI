import streamlit as st

from database.db import save_chat

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

# Initialize chat history state
if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []

# Styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}
</style>
""", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([0.85, 0.15])
with col1:
    st.title("AI Study Assistant")
with col2:
    if st.button("Clear Chat"):
        st.session_state['chat_messages'] = []
        st.rerun()

# Render chat messages
for msg in st.session_state['chat_messages']:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="background-color: #1E2A3A; color: white; border-radius: 12px; padding: 10px 14px; max-width: 75%; margin-left: auto; margin-bottom: 10px; white-space: pre-wrap;">
{msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: #161B22; color: white; border: 1px solid #2A2F36; border-radius: 12px; padding: 10px 14px; max-width: 75%; margin-bottom: 10px; white-space: pre-wrap;">
{msg["content"]}
        </div>
        """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask your study mentor...")

if user_input:
    # 1. Append user message
    st.session_state['chat_messages'].append({"role": "user", "content": user_input})
    
    # 2. Build full prompt for API
    messages = [{"role": "system", "content": "You are Infera, a dedicated academic study mentor. Help students plan studies, understand concepts and stay motivated. Be concise and practical. Plain text only."}]
    for msg in st.session_state['chat_messages'][-10:]:
        messages.append({"role": msg['role'], "content": msg['content']})
    
    try:
        # 3. Call Gemini API
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            max_tokens=1000,
            messages=messages
        )
        result_text = response.choices[0].message.content
        
        # 4. Append assistant message
        st.session_state['chat_messages'].append({"role": "assistant", "content": result_text})
        
        # 5. Save to DB
        save_chat(user_id, user_input, result_text)
        
    except Exception as e:
        st.error(f"Error calling AI service: {e}")
        
    # 6. st.rerun()
    st.rerun()
