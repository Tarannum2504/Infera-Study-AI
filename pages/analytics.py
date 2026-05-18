import streamlit as st
import pandas as pd
import altair as alt
import json

from database.db import get_all_sessions, get_tasks, get_connection

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
.insight-card {
    background-color: #161B22;
    border: 1px solid #2A2F36;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    margin-top: 20px;
}
.insight-value {
    font-size: 20px;
    font-weight: bold;
    color: #FFFFFF;
}
.insight-label {
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

# STEP 1 - LOAD DATA
sessions = get_all_sessions(user_id)
if not sessions:
    st.info("No study data yet. Log some sessions first.")
    st.stop()

df = pd.DataFrame(sessions)
df['date'] = pd.to_datetime(df['date'])

# STEP 2 - COMPUTE METRICS
total_hours = round(df['duration_minutes'].sum() / 60, 1)

daily_df = df.groupby('date')['duration_minutes'].sum().reset_index()
daily_avg_minutes = daily_df['duration_minutes'].mean()  # FIX: Get minutes, not hours
daily_avg_hours = round(daily_avg_minutes / 60, 1)

# 7-day rolling average
daily_series = daily_df.set_index('date')['duration_minutes'].resample('D').sum().fillna(0)
rolling_7 = daily_series.rolling(7, min_periods=1).mean()

# Focus score computation
tasks = get_tasks(user_id)
total_tasks = len(tasks)
done_tasks = len([t for t in tasks if t['status'] == 'done'])
completion_rate = (done_tasks / total_tasks * 100) if total_tasks > 0 else 0

seven_days_ago = pd.Timestamp.now().normalize() - pd.Timedelta(days=7)
recent_days = daily_df[daily_df['date'] >= seven_days_ago]['date'].nunique()
consistency_rate = (recent_days / 7) * 100

# FIX: Use daily average in minutes, divide by 120 (2 hours), cap at 1.0, then multiply by 100
volume_score = min(daily_avg_minutes / 120, 1.0) * 100
focus_score = round((completion_rate * 0.4) + (consistency_rate * 0.35) + (volume_score * 0.25), 1)

# FIX: Add tie-breaking for best_day - if multiple days have same max duration, pick the most recent
max_duration = daily_df['duration_minutes'].max()
best_day_rows = daily_df[daily_df['duration_minutes'] == max_duration]
best_day_row = best_day_rows.iloc[-1]  # Take the most recent if tie
best_day = best_day_row['date'].strftime('%Y-%m-%d')
best_day_hours = round(best_day_row['duration_minutes'] / 60, 1)

subj_df = df.groupby('subject')['duration_minutes'].sum().reset_index()
# FIX: Add tie-breaking for top_subject
max_subj_minutes = subj_df['duration_minutes'].max()
top_subj_rows = subj_df[subj_df['duration_minutes'] == max_subj_minutes]
top_subj_row = top_subj_rows.iloc[0]  # Take first if tie
top_subject = top_subj_row['subject']
top_subj_hours = round(top_subj_row['duration_minutes'] / 60, 1)

total_sessions = len(df)

# STEP 3 - DISPLAY METRIC CARDS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Hours", total_hours)
col2.metric("Daily Average (hrs)", daily_avg_hours)  # FIX: Use hours variable
col3.metric("Focus Score", focus_score)
col4.metric("Total Sessions", total_sessions)

st.divider()

# STEP 4 - CHARTS

# Chart 1: Daily Study Hours
bar_df = daily_df.copy()
bar_df['hours'] = bar_df['duration_minutes'] / 60

chart1 = alt.Chart(bar_df).mark_bar(color='#FFFFFF').encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('hours:Q', title='Hours')
).properties(
    title='Daily Study Hours'
).configure_view(
    fill='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=16
)
st.altair_chart(chart1, use_container_width=True)

# Chart 2: 7-Day Rolling Average
roll_df = rolling_7.reset_index()
roll_df.columns = ['date', 'rolling_mins']
roll_df['rolling_hours'] = roll_df['rolling_mins'] / 60

chart2 = alt.Chart(roll_df).mark_line(color='#A0A0A0', strokeWidth=3).encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('rolling_hours:Q', title='Rolling Average (Hours)')
).properties(
    title='7-Day Rolling Average'
).configure_view(
    fill='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=16
)
st.altair_chart(chart2, use_container_width=True)

# Chart 3: Subject Distribution
sub_df = subj_df.copy()
sub_df['hours'] = sub_df['duration_minutes'] / 60

chart3 = alt.Chart(sub_df).mark_bar(color='#FFFFFF').encode(
    x=alt.X('hours:Q', title='Hours'),
    y=alt.Y('subject:N', title='Subject', sort='-x')
).properties(
    title='Hours by Subject'
).configure_view(
    fill='#161B22'
).configure_axis(
    labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
).configure_title(
    color='#FFFFFF', fontSize=16
)
st.altair_chart(chart3, use_container_width=True)

# STEP 5 - INSIGHT ROW
col_i1, col_i2 = st.columns(2)
with col_i1:
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-label">Best Study Day</div>
        <div class="insight-value">{best_day} ({best_day_hours} hrs)</div>
    </div>
    """, unsafe_allow_html=True)
with col_i2:
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-label">Top Subject</div>
        <div class="insight-value">{top_subject} ({top_subj_hours} hrs)</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.subheader("AI Productivity Insight")

if st.button("Generate Insight"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
    total_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'done'", (user_id,))
    completed_tasks = cursor.fetchone()[0]
    conn.close()

    metrics = {
        "total_hours": total_hours,
        "daily_avg": daily_avg_hours,
        "focus_score": focus_score,
        "total_sessions": total_sessions,
        "best_day": str(best_day),
        "top_subject": top_subject,
        "consistency_rate": consistency_rate,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks
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

        st.markdown(f"""
        <div style="background-color: #161B22; border: 1px solid #2A2F36; border-radius: 8px; padding: 16px; color: #FFFFFF !important; font-size: 15px; line-height: 1.8; white-space: pre-wrap;">
{result_text}
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error calling AI service: {e}")