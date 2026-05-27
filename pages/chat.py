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

# Custom padding & style system
st.markdown("""
<style>
.main .block-container {
    padding: 32px 40px !important;
    max-width: 1100px !important;
}

/* Chat input container — semi transparent */
[data-testid="stBottom"] {
    background: rgba(8, 6, 18, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stBottom"] > div {
    background: transparent !important;
}

/* Chat input field */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #FFFFFF !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(180,140,220,0.4) !important;
    box-shadow: 0 0 0 3px rgba(150,100,200,0.12) !important;
}

/* Chat messages visibility */
.msg-user-inner, .msg-ai-inner {
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
}
.msg-user-inner {
    background: rgba(100, 80, 160, 0.35) !important;
    border: 1px solid rgba(180,140,220,0.2) !important;
    color: #FFFFFF !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4) !important;
}
.msg-ai-inner {
    background: rgba(8, 6, 18, 0.55) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.92) !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.4) !important;
}

/* Token badge */
.token-badge {
    background: rgba(8,6,18,0.5) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Initialize states
if 'chat_messages' not in st.session_state:
    st.session_state['chat_messages'] = []
if 'token_stats' not in st.session_state:
    st.session_state['token_stats'] = {"total_input": 0, "total_output": 0, "calls": 0}

# HEADER (compact)
c_header, c_clear = st.columns([0.8, 0.2])
with c_header:
    st.markdown("""
        <div style="display:flex; align-items:baseline; gap:12px; margin-bottom:20px;">
          <div class="section-title" style="font-size:1.3rem;">AI Assistant</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.25);">
          Infera Study Mentor</div>
        </div>
    """, unsafe_allow_html=True)
with c_clear:
    if st.button("Clear Chat"):
        st.session_state['chat_messages'] = []
        st.rerun()

# Render chat messages
for msg in st.session_state['chat_messages']:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
          <div class="msg-user-inner">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-ai">
          <div class="msg-ai-inner">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display token badge if stats are stored in the message dict
        if "prompt_tokens" in msg:
            in_tok = msg["prompt_tokens"]
            out_tok = msg["completion_tokens"]
            total_tok = in_tok + out_tok
            session_total_tok = st.session_state['token_stats']['total_input'] + st.session_state['token_stats']['total_output']
            
            st.markdown(f"""
                <div class="token-badge">
                  <span>Tokens used</span> {in_tok} in · {out_tok} out
                  · <span>Total</span> {total_tok} · <span>Session</span> {session_total_tok}
                </div>
            """, unsafe_allow_html=True)

# Session Summary Line above the input
calls_count = st.session_state['token_stats']['calls']
total_tokens_used = st.session_state['token_stats']['total_input'] + st.session_state['token_stats']['total_output']

st.markdown(f"""
<div style="text-align:center; font-size:11px; 
color:rgba(255,255,255,0.2); padding:8px 0;">
Session · {calls_count} calls · {total_tokens_used} tokens used</div>
""", unsafe_allow_html=True)

# Chat Input
user_input = st.chat_input("Ask your study mentor...")

if user_input:
    # 1. Append user message
    st.session_state['chat_messages'].append({"role": "user", "content": user_input})
    
    # 2. Build full prompt for API, trimmed to last 8 messages for token optimization
    system_prompt = (
        "You are Infera, a dedicated academic study mentor. "
        "Help students plan studies, understand concepts and stay motivated. "
        "Be concise. Maximum 3 sentences unless detail is explicitly requested. Plain text only."
    )
    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in st.session_state['chat_messages'][-8:]:
        messages.append({"role": msg['role'], "content": msg['content']})
        
    try:
        # 3. Call HF Inference Client
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            max_tokens=1000,
            messages=messages
        )
        result_text = response.choices[0].message.content
        
        # 4. Extract token counts safely
        prompt_tokens = 0
        completion_tokens = 0
        if hasattr(response, 'usage') and response.usage:
            prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
            completion_tokens = getattr(response.usage, 'completion_tokens', 0)
            
        # Update session token totals
        st.session_state['token_stats']['total_input'] += prompt_tokens
        st.session_state['token_stats']['total_output'] += completion_tokens
        st.session_state['token_stats']['calls'] += 1
        
        # 5. Append assistant message with token info
        st.session_state['chat_messages'].append({
            "role": "assistant",
            "content": result_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })
        
        # Save chat to Database
        save_chat(user_id, user_input, result_text)
        
    except Exception as e:
        st.error(f"Error calling AI service: {e}")
        
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
