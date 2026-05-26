import streamlit as st
import time
from datetime import date
from database.db import log_session

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Custom styling for strict design rules
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

st.title("Infera Flow")

# Session State Initialization
if 'seconds_left' not in st.session_state:
    st.session_state['seconds_left'] = 1500
if 'running' not in st.session_state:
    st.session_state['running'] = False
if 'sessions_today' not in st.session_state:
    st.session_state['sessions_today'] = 0
if 'pomodoro_subject' not in st.session_state:
    st.session_state['pomodoro_subject'] = ""

# Subject Input at top
subject = st.text_input("What are you studying?", value=st.session_state['pomodoro_subject'], key="subject_input")
st.session_state['pomodoro_subject'] = subject

# Timer Display (centered, large white monospace text)
mins, secs = divmod(st.session_state['seconds_left'], 60)
timer_text = f"{mins:02d}:{secs:02d}"
st.markdown(f'<div style="font-size: 80px; font-weight: bold; color: #FFFFFF; text-align: center; margin: 20px 0; font-family: monospace;">{timer_text}</div>', unsafe_allow_html=True)

# Sessions completed today below the timer
st.markdown(f"<div style='text-align: center; color: #A0A0A0; font-size: 16px; font-family: Inter, sans-serif; margin-bottom: 20px;'>Sessions completed today: {st.session_state['sessions_today']}</div>", unsafe_allow_html=True)

# Four buttons in a row
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("Start Flow", use_container_width=True):
        st.session_state['running'] = True
        st.rerun()

with c2:
    if st.button("Pause Flow", use_container_width=True):
        st.session_state['running'] = False
        st.rerun()

with c3:
    if st.button("Reset Flow", use_container_width=True):
        st.session_state['running'] = False
        st.session_state['seconds_left'] = 1500
        st.rerun()

with c4:
    if st.button("Complete Flow", use_container_width=True):
        st.session_state['running'] = False
        elapsed_minutes = (1500 - st.session_state['seconds_left']) // 60
        if elapsed_minutes < 1:
            elapsed_minutes = 1
        
        subj = st.session_state['pomodoro_subject'] or "General"
        log_session(user_id, date.today(), elapsed_minutes, subj, 'pomodoro')
        st.success(f"Flow complete! {elapsed_minutes} minutes saved.")
        st.session_state['seconds_left'] = 1500
        st.session_state['sessions_today'] += 1
        st.rerun()

# Timer Logic loop
if st.session_state['running'] and st.session_state['seconds_left'] > 0:
    time.sleep(1)
    st.session_state['seconds_left'] -= 1
    st.rerun()
elif st.session_state['running'] and st.session_state['seconds_left'] <= 0:
    st.session_state['running'] = False
    st.success("Time's up! Click 'Complete Flow' to log your session.")
    st.rerun()
