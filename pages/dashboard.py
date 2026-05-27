import streamlit as st
import pandas as pd
import datetime
from database.db import get_connection, get_all_sessions

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']
name = st.session_state.get('name', 'User')

# Page transition wrapping & padding system
st.markdown("""
<style>
.main .block-container {
    padding: 32px 40px !important;
    overflow-x: hidden !important;
    max-width: 100% !important;
}
table {
    max-width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Fetch current greeting and date
hour = datetime.datetime.now().hour
if hour < 12:
    greeting = "morning"
elif hour < 18:
    greeting = "afternoon"
else:
    greeting = "evening"

today_str = datetime.datetime.now().strftime("%A, %d %B %Y")

# HEADER BLOCK
st.markdown(f"""
<div style="margin-bottom:28px;">
  <div class="section-title">Good {greeting},<br/>{name}</div>
  <div class="section-sub">{today_str}</div>
</div>
""", unsafe_allow_html=True)

# Fetch Data for KPIs
conn = get_connection()
cursor = conn.cursor()

# 1. Study Hours
cursor.execute("SELECT SUM(duration_minutes)/60.0 as total_hours FROM study_sessions WHERE user_id=?", (user_id,))
row = cursor.fetchone()
study_hours = round(row['total_hours'], 1) if row and row['total_hours'] else 0.0

# 2. Tasks Completed
cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE user_id=? AND status='done'", (user_id,))
completed_tasks = cursor.fetchone()['completed']

# 3. Focus Score
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

# DISPLAY KPI CARDS (using custom HTML grid)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{study_hours}h</div>
          <div class="kpi-label">Study Hours</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{focus_score}</div>
          <div class="kpi-label">Focus Score</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{completed_tasks}</div>
          <div class="kpi-label">Tasks Completed</div>
        </div>
    """, unsafe_allow_html=True)



# HIGH PRIORITY SECTION
st.markdown("""
<div class="section-title" style="font-size:1.1rem; margin:28px 0 12px;">
High Priority</div>
""", unsafe_allow_html=True)

cursor.execute("""
    SELECT title as Title, subject as Subject, deadline as Deadline 
    FROM tasks 
    WHERE user_id=? AND status != 'done' AND priority='high'
    ORDER BY deadline ASC LIMIT 5
""", (user_id,))
high_priority_tasks = cursor.fetchall()

rows = ""
if not high_priority_tasks:
    rows = "<tr><td colspan='3' style='padding:16px 14px; color:rgba(255,255,255,0.25); text-align:center; font-size:13px;'>No high priority tasks</td></tr>"
else:
    for t in high_priority_tasks:
        rows += f"<tr><td style='padding:10px 14px; color:rgba(255,255,255,0.85); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Title']}</td><td style='padding:10px 14px; color:rgba(255,255,255,0.5); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Subject']}</td><td style='padding:10px 14px; color:rgba(255,255,255,0.5); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Deadline']}</td></tr>"

st.markdown(f"<table style='width:100%; border-collapse:collapse; background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:10px; overflow:hidden; backdrop-filter:blur(20px);'><thead><tr style='border-bottom:1px solid rgba(255,255,255,0.08);'><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Task</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Subject</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Deadline</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

# UPCOMING DEADLINES SECTION
st.markdown("""
<div class="section-title" style="font-size:1.1rem; margin:28px 0 12px;">
Upcoming Deadlines</div>
""", unsafe_allow_html=True)

cursor.execute("""
    SELECT title as Title, subject as Subject, deadline as Deadline 
    FROM tasks 
    WHERE user_id=? AND status != 'done' AND deadline >= date('now') AND deadline <= date('now', '+7 days')
    ORDER BY deadline ASC LIMIT 5
""", (user_id,))
upcoming_tasks = cursor.fetchall()
conn.close()

rows2 = ""
if not upcoming_tasks:
    rows2 = "<tr><td colspan='3' style='padding:16px 14px; color:rgba(255,255,255,0.25); text-align:center; font-size:13px;'>No upcoming deadlines in the next 7 days</td></tr>"
else:
    for t in upcoming_tasks:
        rows2 += f"<tr><td style='padding:10px 14px; color:rgba(255,255,255,0.85); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Title']}</td><td style='padding:10px 14px; color:rgba(255,255,255,0.5); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Subject']}</td><td style='padding:10px 14px; color:rgba(255,255,255,0.5); border-bottom:1px solid rgba(255,255,255,0.05); font-size:13px;'>{t['Deadline']}</td></tr>"

st.markdown(f"<table style='width:100%; border-collapse:collapse; background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:10px; overflow:hidden; backdrop-filter:blur(20px);'><thead><tr style='border-bottom:1px solid rgba(255,255,255,0.08);'><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Task</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Subject</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Deadline</th></tr></thead><tbody>{rows2}</tbody></table>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

