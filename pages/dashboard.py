import streamlit as st
import pandas as pd
from database.db import get_connection, get_all_sessions

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']
name = st.session_state.get('name', 'User')

# Design rules styling
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

st.title(f"Welcome back, {name}")

# Fetch data
conn = get_connection()
cursor = conn.cursor()

# 1. Study Hours
cursor.execute("SELECT SUM(duration_minutes)/60.0 as total_hours FROM study_sessions WHERE user_id=?", (user_id,))
row = cursor.fetchone()
study_hours = round(row['total_hours'], 1) if row and row['total_hours'] else 0.0

# 2. Tasks Completed
cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE user_id=? AND status='done'", (user_id,))
completed_tasks = cursor.fetchone()['completed']

# 3. Focus Score Logic
sessions = get_all_sessions(user_id)
cursor.execute("SELECT * FROM tasks WHERE user_id=?", (user_id,))
tasks = [dict(r) for r in cursor.fetchall()]

total_tasks = len(tasks)
completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

if sessions:
    df = pd.DataFrame(sessions)
    df['date'] = pd.to_datetime(df['date'])
    daily_df = df.groupby('date')['duration_minutes'].sum().reset_index()
    daily_avg_minutes = daily_df['duration_minutes'].mean()
    
    seven_days_ago = pd.Timestamp.now().normalize() - pd.Timedelta(days=7)
    recent_days = daily_df[daily_df['date'] >= seven_days_ago]['date'].nunique()
    consistency_rate = (recent_days / 7) * 100
    
    volume_score = min(daily_avg_minutes / 120, 1.0) * 100
    focus_score = round((completion_rate * 0.4) + (consistency_rate * 0.35) + (volume_score * 0.25), 1)
else:
    focus_score = round(completion_rate * 0.4, 1)

# DISPLAY METRIC CARDS
col1, col2, col3 = st.columns(3)
col1.metric("Study Hours", f"{study_hours}")
col2.metric("Focus Score", f"{focus_score}")
col3.metric("Tasks Completed", f"{completed_tasks}")

st.write("")
st.write("")

# HIGH PRIORITY TASKS
st.subheader("High Priority & Upcoming")
cursor.execute("""
    SELECT title as Title, subject as Subject, deadline as Deadline 
    FROM tasks 
    WHERE user_id=? AND status != 'done' AND priority='high'
    ORDER BY deadline ASC LIMIT 5
""", (user_id,))
high_priority_tasks = cursor.fetchall()

if high_priority_tasks:
    df_hp = pd.DataFrame([dict(r) for r in high_priority_tasks])
    st.dataframe(df_hp, hide_index=True, width='stretch')
else:
    st.info("No high priority tasks.")

st.write("")

# UPCOMING DEADLINES
st.subheader("Upcoming Deadlines")
cursor.execute("""
    SELECT title as Title, subject as Subject, deadline as Deadline 
    FROM tasks 
    WHERE user_id=? AND status != 'done' AND deadline >= date('now')
    ORDER BY deadline ASC LIMIT 5
""", (user_id,))
upcoming_tasks = cursor.fetchall()
conn.close()

if upcoming_tasks:
    df_up = pd.DataFrame([dict(r) for r in upcoming_tasks])
    st.dataframe(df_up, hide_index=True, width='stretch')
else:
    st.info("No upcoming deadlines.")
