import streamlit as st
import time
from datetime import date
from database.db import log_session

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# 1. STATE INITIALIZATION
if 'pomodoro_running' not in st.session_state:
    st.session_state.pomodoro_running = False
if 'pomodoro_seconds_left' not in st.session_state:
    st.session_state.pomodoro_seconds_left = 1500
if 'pomodoro_subject' not in st.session_state:
    st.session_state.pomodoro_subject = ""
if 'pomodoro_sessions_today' not in st.session_state:
    st.session_state.pomodoro_sessions_today = 0

# Design Rules
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
.timer-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 40px 0;
}
.timer-text {
    font-size: 120px;
    font-weight: bold;
    color: #FFFFFF;
    font-family: monospace;
    line-height: 1;
}
.stButton > button {
    background-color: #161B22;
    color: #FFFFFF;
    border: 1px solid #2A2F36;
    width: 100%;
}
.stButton > button:hover {
    border-color: #A0A0A0;
    color: #FFFFFF;
}
p, div, span, label {
    color: #A0A0A0 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Pomodoro Timer")

# Subject Input
st.session_state.pomodoro_subject = st.text_input(
    "What are you studying?", 
    value=st.session_state.pomodoro_subject
)

# Timer Display Placeholder
timer_placeholder = st.empty()

def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

def render_timer(time_str):
    timer_placeholder.markdown(f"""
        <div class="timer-container">
            <div class="timer-text">{time_str}</div>
        </div>
    """, unsafe_allow_html=True)

# Initial render
render_timer(format_time(st.session_state.pomodoro_seconds_left))

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.session_state.pomodoro_running:
        if st.button("Pause"):
            st.session_state.pomodoro_running = False
            st.rerun()
    else:
        if st.button("Start"):
            st.session_state.pomodoro_running = True
            st.rerun()

with col2:
    if st.button("Reset"):
        st.session_state.pomodoro_running = False
        st.session_state.pomodoro_seconds_left = 1500
        st.rerun()

st.write(f"Sessions today: {st.session_state.pomodoro_sessions_today}")

# Timer Logic Place
msg_placeholder = st.empty()

if st.session_state.pomodoro_running:
    while st.session_state.pomodoro_seconds_left > 0 and st.session_state.pomodoro_running:
        time.sleep(1)
        st.session_state.pomodoro_seconds_left -= 1
        render_timer(format_time(st.session_state.pomodoro_seconds_left))
    
    # When timer hits 0
    if st.session_state.pomodoro_seconds_left == 0:
        st.session_state.pomodoro_running = False
        subject = st.session_state.pomodoro_subject.strip()
        if not subject:
            subject = "General"
            
        # Log session
        log_session(user_id, date.today(), 25, subject, 'pomodoro')
        
        st.session_state.pomodoro_sessions_today += 1
        st.session_state.pomodoro_seconds_left = 1500
        
        msg_placeholder.success("Pomodoro complete! Session saved.")
        time.sleep(3) # Show message for 3 seconds before rerunning to reset timer display
        st.rerun()
