import streamlit as st
import time
from datetime import date
from database.db import log_session

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Custom padding system
st.markdown("""
<style>
.main .block-container {
    padding: 32px 40px !important;
    max-width: 1100px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Session State Initialization
if 'seconds_left' not in st.session_state:
    st.session_state['seconds_left'] = 1500
if 'running' not in st.session_state:
    st.session_state['running'] = False
if 'sessions_today' not in st.session_state:
    st.session_state['sessions_today'] = 0
if 'pomodoro_subject' not in st.session_state:
    st.session_state['pomodoro_subject'] = ""

# HEADER
st.markdown("""
<div style="margin-bottom:28px;">
  <div class="section-title">Infera Flow</div>
  <div class="section-sub">Deep work, tracked.</div>
</div>
""", unsafe_allow_html=True)

# SUBJECT INPUT (above timer)
subject = st.text_input("What are you working on?", value=st.session_state['pomodoro_subject'], placeholder="What are you working on?", key="subject_input")
st.session_state['pomodoro_subject'] = subject

# TIMER DISPLAY (centered, large)
mins, secs = divmod(st.session_state['seconds_left'], 60)
timer_text = f"{mins:02d}:{secs:02d}"

st.markdown(f"""
<div style="text-align:center; padding:48px 0;">
  <div style="font-family:'Instrument Serif',serif; font-style:italic;
  font-size:6rem; color:#FFFFFF; letter-spacing:-4px; line-height:1;">
  {timer_text}</div>
  <div style="font-size:11px; color:rgba(255,255,255,0.25); 
  text-transform:uppercase; letter-spacing:0.15em; margin-top:12px;">
  25 minute focus session</div>
</div>
""", unsafe_allow_html=True)

# FOUR BUTTONS (Start Flow · Pause Flow · Reset Flow · Complete Flow in equal columns)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("Start Flow", key="btn_start_flow", use_container_width=True):
        st.session_state['running'] = True
        st.rerun()

with col2:
    if st.button("Pause Flow", key="btn_pause_flow", use_container_width=True):
        st.session_state['running'] = False
        st.rerun()

with col3:
    if st.button("Reset Flow", key="btn_reset_flow", use_container_width=True):
        st.session_state['running'] = False
        st.session_state['seconds_left'] = 1500
        st.rerun()

with col4:
    if st.button("Complete Flow", key="btn_complete_flow", use_container_width=True):
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

# SESSIONS TODAY COUNTER
st.markdown(f"""
<div style="text-align:center; margin-top:20px; font-size:12px; 
color:rgba(255,255,255,0.25);">
{st.session_state['sessions_today']} sessions completed today</div>
""", unsafe_allow_html=True)

# Timer loop logic
if st.session_state['running'] and st.session_state['seconds_left'] > 0:
    time.sleep(1)
    st.session_state['seconds_left'] -= 1
    st.rerun()
elif st.session_state['running'] and st.session_state['seconds_left'] <= 0:
    st.session_state['running'] = False
    st.success("Time's up! Click 'Complete Flow' to log your session.")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
