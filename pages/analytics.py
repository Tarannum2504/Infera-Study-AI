import streamlit as st
import pandas as pd
import altair as alt
import json
from datetime import date

from database.db import get_all_sessions, get_tasks, get_connection, get_recent_sessions

# Load environment variables
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
client = InferenceClient(
    provider="novita",
    api_key=os.getenv("HF_API_KEY")
)

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
.metric-card {
    background-color: #161B22;
    border: 1px solid #2A2F36;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #FFFFFF;
}
.metric-label {
    font-size: 14px;
    color: #A0A0A0;
}
p, div, span, label {
    color: #A0A0A0 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Analytics Dashboard")

# Fetch data
sessions = get_all_sessions(user_id)
tasks = get_tasks(user_id)

total_tasks = len(tasks)
completed_tasks = len([t for t in tasks if t['status'] == 'done'])
productivity_pct = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

if sessions:
    df = pd.DataFrame(sessions)
    df['date'] = pd.to_datetime(df['date'])
    
    total_hours = round(df['duration_minutes'].sum() / 60, 1)
    
    daily_df = df.groupby('date')['duration_minutes'].sum().reset_index()
    daily_avg_minutes = daily_df['duration_minutes'].mean()
    daily_avg_hours = round(daily_avg_minutes / 60, 1)
    
    # 7-day rolling average
    seven_days_ago = pd.Timestamp.now().normalize() - pd.Timedelta(days=7)
    recent_days = daily_df[daily_df['date'] >= seven_days_ago]['date'].nunique()
    consistency_rate = (recent_days / 7) * 100
    
    volume_score = min(daily_avg_minutes / 120, 1.0) * 100
    focus_score = round((productivity_pct * 0.4) + (consistency_rate * 0.35) + (volume_score * 0.25), 1)
else:
    total_hours = 0.0
    daily_avg_hours = 0.0
    consistency_rate = 0.0
    volume_score = 0.0
    focus_score = round(productivity_pct * 0.4, 1)

# SECTION 1 — KPI CARDS (st.columns(4))
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Study Hours</div>
        <div class="metric-value">{total_hours}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Focus Score</div>
        <div class="metric-value">{focus_score}</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Completed Tasks</div>
        <div class="metric-value">{completed_tasks}</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Productivity %</div>
        <div class="metric-value">{productivity_pct}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# SECTION 2 — CHARTS
chart_col1, chart_col2 = st.columns(2)

# Chart 1: Weekly Study Hours
last_7_days = []
for i in range(7):
    d = (pd.Timestamp.now().normalize() - pd.Timedelta(days=i)).date()
    last_7_days.append(d)

weekly_data = []
for d in last_7_days:
    day_sessions = [s for s in sessions if pd.to_datetime(s['date']).date() == d] if sessions else []
    day_mins = sum([s['duration_minutes'] for s in day_sessions])
    weekly_data.append({"Date": d.strftime("%m-%d"), "Hours": round(day_mins / 60, 2)})

weekly_df = pd.DataFrame(weekly_data).iloc[::-1]

chart1 = alt.Chart(weekly_df).mark_bar(color='#FFFFFF').encode(
    x=alt.X('Date:N', title='Date', sort=None),
    y=alt.Y('Hours:Q', title='Hours')
).properties(
    title='Weekly Study Hours',
    height=250,
    background='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=14
)

with chart_col1:
    st.altair_chart(chart1, use_container_width=True)

# Chart 2: Subject Distribution
if sessions:
    subj_df = df.groupby('subject')['duration_minutes'].sum().reset_index()
    subj_df['hours'] = round(subj_df['duration_minutes'] / 60, 2)
    subj_df = subj_df.sort_values(by='hours', ascending=False).head(5)
else:
    subj_df = pd.DataFrame(columns=['subject', 'hours'])

chart2 = alt.Chart(subj_df).mark_bar(color='#A0A0A0').encode(
    x=alt.X('hours:Q', title='Hours'),
    y=alt.Y('subject:N', title='Subject', sort='-x')
).properties(
    title='Hours by Subject',
    height=250,
    background='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=14
)

with chart_col2:
    st.altair_chart(chart2, use_container_width=True)

# Chart 3: Productivity Trend (full width)
if sessions:
    daily_df = df.groupby('date')['duration_minutes'].sum().reset_index()
    trend_data = []
    for index, row in daily_df.iterrows():
        d = row['date']
        day_mins = row['duration_minutes']
        day_volume_score = min(day_mins / 120, 1.0) * 100
        day_focus_score = round((productivity_pct * 0.4) + (consistency_rate * 0.35) + (day_volume_score * 0.25), 1)
        trend_data.append({"Date": d, "Focus Score": day_focus_score})
    trend_df = pd.DataFrame(trend_data).sort_values(by='Date')
else:
    trend_df = pd.DataFrame(columns=['Date', 'Focus Score'])

chart3 = alt.Chart(trend_df).mark_line(color='#FFFFFF', strokeWidth=3).encode(
    x=alt.X('Date:T', title='Date'),
    y=alt.Y('Focus Score:Q', title='Focus Score', scale=alt.Scale(domain=[0, 100]))
).properties(
    title='Productivity Trend (Daily Focus Score)',
    height=250,
    background='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=14
)

st.altair_chart(chart3, use_container_width=True)

# SECTION 3 — RECENT SESSIONS TABLE
st.subheader("Recent Sessions")
recent_sessions = get_recent_sessions(user_id, limit=20)
if recent_sessions:
    table_data = []
    for s in recent_sessions:
        duration = s['duration_minutes']
        status = "Complete" if duration >= 25 else "Partial"
        table_data.append({
            "Subject": s['subject'],
            "Duration": f"{duration} mins",
            "Date": s['date'],
            "Status": status
        })
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, hide_index=True, width='stretch')
else:
    st.info("No study sessions logged yet.")

st.divider()

# SECTION 4 — AI PRODUCTIVITY INSIGHT
st.subheader("AI Productivity Insight")

if st.button("Generate Insight"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
    total_tasks_db = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'done'", (user_id,))
    completed_tasks_db = cursor.fetchone()[0]
    conn.close()

    metrics = {
        "total_hours": total_hours,
        "daily_avg": daily_avg_hours,
        "focus_score": focus_score,
        "total_sessions": len(sessions) if sessions else 0,
        "consistency_rate": consistency_rate,
        "total_tasks": total_tasks_db,
        "completed_tasks": completed_tasks_db
    }

    try:
        with st.spinner("Analyzing your study patterns..."):
            system_prompt = (
                "You are an academic productivity coach analyzing a student's study data. \n"
                "Give honest, specific, actionable feedback in 4-5 sentences. \n"
                "Reference the actual numbers from the data. \n"
                "End with one specific recommendation. Plain text only, no formatting."
            )
            user_message = (
                f"Here is my study data this week: {json.dumps(metrics, indent=2)}\n\n"
                f"Give me an honest productivity insight and one specific recommendation."
            )
            response = client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct",
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            result_text = response.choices[0].message.content

        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #2A2F36; border-radius: 8px; padding: 16px; color: #FFFFFF !important; font-size: 15px; line-height: 1.8; white-space: pre-wrap;">
{result_text}
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error calling AI service: {e}")