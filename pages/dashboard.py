import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from database.db import get_dashboard_stats, get_weekly_hours, get_subject_breakdown, get_pending_tasks, get_streak

# Require login
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']
name = st.session_state.get('name', 'User')

# DESIGN RULES
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
p, div, span, label {
    color: #A0A0A0 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# SECTION 1 - GREETING
st.title(f"Welcome back, {name}")
st.caption(f"Today is {date.today().strftime('%A, %d %B %Y')}")
st.divider()

# SECTION 2 - KPI CARDS
stats = get_dashboard_stats(user_id)
streak = get_streak(user_id)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Study Hours", value=round(stats['total_hours'], 1))
with col2:
    st.metric(label="Tasks Done", value=stats['tasks_done'])
with col3:
    st.metric(label="Active Tasks", value=stats['active_tasks'])
with col4:
    st.metric(label="Day Streak", value=streak)

# SECTION 3 - CHARTS
weekly_hours = get_weekly_hours(user_id)
subject_breakdown = get_subject_breakdown(user_id)

if not weekly_hours and not subject_breakdown:
    st.info("No study data yet — log your first session.")
else:
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if weekly_hours:
            df_weekly = pd.DataFrame(weekly_hours)
            chart1 = alt.Chart(df_weekly).mark_bar(color='#FFFFFF').encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('hours:Q', title='Hours')
            ).properties(
                title='Last 7 Days'
            ).configure_view(
                fill='#161B22'
            ).configure_axis(
                labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
            ).configure_title(
                color='#FFFFFF', fontSize=16
            )
            st.altair_chart(chart1, use_container_width=True)
        else:
            st.info("No weekly data.")

    with col_chart2:
        if subject_breakdown:
            df_subject = pd.DataFrame(subject_breakdown)
            chart2 = alt.Chart(df_subject).mark_bar(color='#FFFFFF').encode(
                x=alt.X('hours:Q', title='Hours'),
                y=alt.Y('subject:N', sort='-x', title='Subject')
            ).properties(
                title='Top Subjects'
            ).configure_view(
                fill='#161B22'
            ).configure_axis(
                labelColor='#A0A0A0', titleColor='#FFFFFF', gridColor='#2A2F36'
            ).configure_title(
                color='#FFFFFF', fontSize=16
            )
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info("No subject data.")

# SECTION 4 - RECENT TASKS
st.subheader("Pending Tasks")
pending_tasks = get_pending_tasks(user_id)
if pending_tasks:
    df_tasks = pd.DataFrame(pending_tasks)
    st.dataframe(df_tasks, hide_index=True, use_container_width=True)
else:
    st.info("No pending tasks.")
