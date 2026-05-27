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

# Custom padding & style system
st.markdown("""
<style>
.main .block-container {
    padding: 32px 40px !important;
    max-width: 1100px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# HEADER
st.markdown("""
<div style="margin-bottom:28px;">
  <div class="section-title">Productivity Intelligence</div>
</div>
""", unsafe_allow_html=True)

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

# SECTION 1 â€” KPI ROW (using custom HTML grid with Instrument Serif italic digits)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{total_hours}h</div>
          <div class="kpi-label">Total Hours</div>
          <div class="kpi-delta">all time</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{focus_score}</div>
          <div class="kpi-label">Focus Score</div>
          <div class="kpi-delta">composite score</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{completed_tasks}</div>
          <div class="kpi-label">Tasks Done</div>
          <div class="kpi-delta">completed</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{productivity_pct}%</div>
          <div class="kpi-label">Productivity %</div>
          <div class="kpi-delta">completion rate</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# SECTION 2 â€” CHARTS
chart_col1, chart_col2 = st.columns(2)

# Chart 1: Weekly Study Hours Data
last_7_days = []
for i in range(7):
    d = (pd.Timestamp.now().normalize() - pd.Timedelta(days=i)).date()
    last_7_days.append(d)

weekly_data = []
for d in last_7_days:
    day_sessions = [s for s in sessions if pd.to_datetime(s['date']).date() == d] if sessions else []
    day_mins = sum([s['duration_minutes'] for s in day_sessions])
    weekly_data.append({"date": pd.to_datetime(d), "hours": round(day_mins / 60, 2)})

weekly_df = pd.DataFrame(weekly_data).iloc[::-1]



# Weekly hours chart
with chart_col1:
    st.markdown("<div style='background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:8px; backdrop-filter:blur(20px);'>", unsafe_allow_html=True)
    chart1 = alt.Chart(weekly_df).mark_bar(
        color='rgba(200, 180, 255, 0.85)',
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X('date:T', axis=alt.Axis(
            labelColor='rgba(255,255,255,0.5)',
            gridColor='rgba(255,255,255,0.06)',
            titleColor='rgba(255,255,255,0.4)',
            domainColor='rgba(255,255,255,0.1)',
            tickColor='rgba(255,255,255,0.1)',
            labelFont='Inter',
            titleFont='Inter',
            labelAngle=-30
        )),
        y=alt.Y('hours:Q', axis=alt.Axis(
            labelColor='rgba(255,255,255,0.5)',
            gridColor='rgba(255,255,255,0.06)',
            titleColor='rgba(255,255,255,0.4)',
            domainColor='rgba(255,255,255,0.1)',
            tickColor='rgba(255,255,255,0.1)',
            labelFont='Inter',
            titleFont='Inter'
        ))
    ).properties(
        background='transparent',
        height=220,
        padding={"left": 25, "top": 15, "right": 30, "bottom": 15},
        title=alt.TitleParams(
            text='Daily Study Hours',
            color='rgba(255,255,255,0.55)',
            fontSize=12,
            font='Inter'
        )
    )
    st.altair_chart(chart1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Chart 2: Subject Distribution Data
if sessions:
    subject_df = df.groupby('subject')['duration_minutes'].sum().reset_index()
    subject_df['hours'] = round(subject_df['duration_minutes'] / 60, 2)
    subject_df = subject_df.sort_values(by='hours', ascending=False).head(5)
else:
    subject_df = pd.DataFrame(columns=['subject', 'hours'])

# Subject distribution chart
with chart_col2:
    st.markdown("<div style='background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:8px; backdrop-filter:blur(20px);'>", unsafe_allow_html=True)
    chart2 = alt.Chart(subject_df).mark_bar(
        color='rgba(200, 180, 255, 0.85)',
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X('hours:Q', axis=alt.Axis(
            labelColor='rgba(255,255,255,0.5)',
            gridColor='rgba(255,255,255,0.06)',
            titleColor='rgba(255,255,255,0.4)',
            domainColor='rgba(255,255,255,0.1)',
            tickColor='rgba(255,255,255,0.1)',
            labelFont='Inter',
            titleFont='Inter'
        )),
        y=alt.Y('subject:N', sort='-x', axis=alt.Axis(
            labelColor='rgba(255,255,255,0.5)',
            gridColor='rgba(255,255,255,0.06)',
            titleColor='rgba(255,255,255,0.4)',
            domainColor='rgba(255,255,255,0.1)',
            tickColor='rgba(255,255,255,0.1)',
            labelFont='Inter',
            titleFont='Inter'
        ))
    ).properties(
        background='transparent',
        height=220,
        padding={"left": 35, "top": 15, "right": 30, "bottom": 15},
        title=alt.TitleParams(
            text='Hours by Subject',
            color='rgba(255,255,255,0.55)',
            fontSize=12,
            font='Inter'
        )
    )
    st.altair_chart(chart2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Chart 3: Productivity Trend Data (full width)
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

# Productivity trend line chart with Inline Axis settings to avoid TypeError
st.markdown("<div style='background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:8px; backdrop-filter:blur(20px);'>", unsafe_allow_html=True)
chart3 = alt.Chart(trend_df).mark_line(
    color='rgba(220, 180, 255, 0.9)',
    strokeWidth=2
).encode(
    x=alt.X('Date:T', axis=alt.Axis(
        labelColor='rgba(255,255,255,0.5)',
        gridColor='rgba(255,255,255,0.06)',
        titleColor='rgba(255,255,255,0.4)',
        domainColor='rgba(255,255,255,0.1)',
        tickColor='rgba(255,255,255,0.1)',
        labelFont='Inter',
        titleFont='Inter'
    )),
    y=alt.Y('Focus Score:Q', scale=alt.Scale(domain=[0, 100]), axis=alt.Axis(
        labelColor='rgba(255,255,255,0.5)',
        gridColor='rgba(255,255,255,0.06)',
        titleColor='rgba(255,255,255,0.4)',
        domainColor='rgba(255,255,255,0.1)',
        tickColor='rgba(255,255,255,0.1)',
        labelFont='Inter',
        titleFont='Inter'
    ))
).properties(
    background='transparent',
    height=220,
    padding={"left": 25, "top": 15, "right": 30, "bottom": 15},
    title=alt.TitleParams(
        text='Productivity Trend (Daily Focus Score)',
        color='rgba(255,255,255,0.55)',
        fontSize=12,
        font='Inter'
    )
)
st.altair_chart(chart3, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# SECTION 3 â€” RECENT SESSIONS TABLE
st.markdown("""
<div class="section-title" style="font-size:1.1rem; margin:28px 0 12px;">
Recent Sessions</div>
""", unsafe_allow_html=True)



recent_sessions = get_recent_sessions(user_id, limit=20)
rows = ""
if not recent_sessions:
    rows = "<tr><td colspan='4' style='padding:16px 14px; color:rgba(255,255,255,0.25); text-align:center; font-size:13px;'>No study sessions logged yet</td></tr>"
else:
    for i, s in enumerate(recent_sessions):
        status = "Complete" if s["duration_minutes"] >= 25 else "Partial"
        sc = "rgba(150,220,150,0.8)" if status == "Complete" else "rgba(255,180,100,0.8)"
        bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
        rows += f"<tr style='background:{bg};'><td style='padding:10px 14px; color:rgba(255,255,255,0.85); border-bottom:1px solid rgba(255,255,255,0.04); font-size:13px;'>{s['subject']}</td><td style='padding:10px 14px; color:rgba(255,255,255,0.55); border-bottom:1px solid rgba(255,255,255,0.04); font-size:13px;'>{s['duration_minutes']} min</td><td style='padding:10px 14px; color:rgba(255,255,255,0.55); border-bottom:1px solid rgba(255,255,255,0.04); font-size:13px;'>{s['date']}</td><td style='padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.04);'><span style='font-size:11px; padding:2px 10px; border-radius:99px; border:1px solid {sc}; color:{sc};'>{status}</span></td></tr>"

st.markdown(f"<table style='width:100%; border-collapse:collapse; background:rgba(8,6,18,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:10px; overflow:hidden; backdrop-filter:blur(20px);'><thead><tr style='border-bottom:1px solid rgba(255,255,255,0.08);'><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Subject</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Duration</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Date</th><th style='padding:10px 14px; text-align:left; font-size:10px; color:rgba(255,255,255,0.3); text-transform:uppercase; letter-spacing:0.1em; font-weight:500;'>Status</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)


st.write("")

# SECTION 4 â€” AI PRODUCTIVITY INSIGHT (styled with .glass-card)
st.markdown("""
<div class="section-title" style="font-size:1.1rem; margin:28px 0 12px;">
AI Productivity Insight</div>
""", unsafe_allow_html=True)

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

        # Styled within premium liquid glass card
        st.markdown(f"""
        <div class="glass-card" style="font-size: 13px; line-height: 1.6; white-space: pre-wrap; color: rgba(255,255,255,0.85);">
{result_text}
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error calling AI service: {e}")

st.markdown('</div>', unsafe_allow_html=True)
