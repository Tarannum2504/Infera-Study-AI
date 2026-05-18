import streamlit as st
import pandas as pd
from datetime import date
from database.db import log_session, get_recent_sessions, get_session_stats

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Custom styling
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
.stat-card {
    background-color: #161B22;
    border: 1px solid #2A2F36;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.stat-value {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 4px;
}
.stat-label {
    color: #A0A0A0;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.title("Study Session Logger")

# 3. QUICK STATS
stats = get_session_stats(user_id)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats['total_sessions']}</div>
        <div class="stat-label">Total Sessions</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats['total_hours']}</div>
        <div class="stat-label">Total Study Hours</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{stats['top_subject']}</div>
        <div class="stat-label">Most Studied Subject</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# 1. LOG SESSION FORM
st.subheader("Log a New Session")
with st.form("log_session_form", clear_on_submit=True):
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        subject = st.text_input("Subject")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=480, value=None, placeholder="Enter minutes...")
    with col_s2:
        session_date = st.date_input("Date", value=date.today())
        session_type = st.selectbox("Session Type", ["free", "scheduled", "pomodoro"])
        
    submitted = st.form_submit_button("Log Session")
    
    if submitted:
        # Hard server-side validation guards
        if not subject or subject.strip() == "":
            st.error("Subject cannot be empty.")
        elif duration is None or duration <= 0:
            st.error("Duration must be at least 1 minute.")
        else:
            log_session(user_id, session_date, duration, subject.strip(), session_type)
            st.success(f"Session logged — {duration} minutes of {subject.strip()}")
            st.rerun()

st.divider()

# 2. RECENT SESSIONS TABLE
st.subheader("Recent Sessions")
recent_sessions = get_recent_sessions(user_id, limit=10)

if not recent_sessions:
    st.info("No study sessions logged yet.")
else:
    df = pd.DataFrame(recent_sessions)
    df = df[['date', 'subject', 'duration_minutes', 'session_type']]
    df.columns = ['Date', 'Subject', 'Duration', 'Type']
    df['Duration'] = df['Duration'].astype(str) + " min"
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    