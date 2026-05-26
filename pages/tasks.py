import streamlit as st
from database.db import get_tasks, add_task, update_task_status, delete_task

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

st.markdown('<div class="dash-header">Task Manager</div>', unsafe_allow_html=True)

# 1. TASK INPUT FORM
with st.container():
    st.markdown('<div class="card-header">Add New Task</div>', unsafe_allow_html=True)
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            subject = st.text_input("Subject")
            deadline = st.date_input("Deadline")
        with col2:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            progress = st.slider("Progress", 0, 100, 0)
            st.write("") # spacing
            submitted = st.form_submit_button("Add Task", use_container_width=True)
            
        if submitted:
            if title and subject:
                add_task(user_id, title, subject, deadline, priority.lower(), progress)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.error("Please fill in Title and Subject.")

st.divider()

# Get all unique subjects for the filter
all_tasks = get_tasks(user_id)
subjects = sorted(list(set([t['subject'] for t in all_tasks])))
subjects.insert(0, "All")

# 2. FILTER BAR
st.markdown('<div class="card-header">Your Tasks</div>', unsafe_allow_html=True)
col_f1, col_f2 = st.columns(2)
with col_f1:
    subject_filter = st.selectbox("Filter by Subject", subjects, key="subj_filter")
with col_f2:
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_progress", "done"], key="stat_filter")

# Fetch filtered tasks
tasks = get_tasks(user_id, subject_filter, status_filter)

# 3. TASK TABLE
if not tasks:
    st.info("No tasks found.")
else:
    def get_progress_color(prog):
        if prog <= 25: return "#E53935"
        if prog <= 50: return "#FB8C00"
        if prog <= 75: return "#FDD835"
        if prog <= 99: return "#A0A0A0"
        return "#43A047"

    is_light_mode = st.session_state.get('app_theme') == "Light Mode"
    table_bg = "#FFFFFF" if is_light_mode else "#1F1F1F"
    table_border = "#F0DCD3" if is_light_mode else "#2C2C2C"
    text_color = "#2C1A1D" if is_light_mode else "#FFFFFF"
    header_bg = "#FFFFFF" if is_light_mode else "#1F1F1F"
    header_text = "#756668" if is_light_mode else "#A0A0A0"
    row_even_bg = "#FFFFFF" if is_light_mode else "#1F1F1F"
    row_odd_bg = "#FFEFE6" if is_light_mode else "#1A1A1A"
    pb_track = "#F0DCD3" if is_light_mode else "#2C2C2C"

    table_html = f"""<style>
.task-table {{
    width: 100%;
    border-collapse: collapse;
    background-color: {table_bg};
    border: 1px solid {table_border};
    color: {text_color};
    font-size: 14px;
    margin-bottom: 20px;
    border-radius: 12px;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
}}
.task-table th {{
    background-color: {header_bg};
    color: {header_text};
    text-align: left;
    padding: 12px 20px;
    border-bottom: 1px solid {table_border};
    font-weight: 500;
}}
.task-table td {{
    padding: 12px 20px;
    border-bottom: 1px solid {table_border};
    color: {text_color};
    font-weight: 500;
}}
.task-table tr:nth-child(even) {{
    background-color: {row_even_bg};
}}
.task-table tr:nth-child(odd) {{
    background-color: {row_odd_bg};
}}
</style>
<table class="task-table">
<thead>
<tr>
<th>Task Name</th>
<th>Subject</th>
<th>Deadline</th>
<th style="width: 25%;">Progress</th>
<th>Status</th>
<th>Action</th>
</tr>
</thead>
<tbody>"""

    for task in tasks:
        prog = task['progress']
        color = get_progress_color(prog)
        pb_html = f"""<div style="background:{pb_track}; border-radius:4px; height:8px; width:100%; margin-bottom:4px;">
<div style="background:{color}; width:{prog}%; height:8px; border-radius:4px;"></div>
</div>
<small style="color:{header_text};">{prog}%</small>"""
        
        table_html += f"""<tr>
<td>{task['title']}</td>
<td>{task['subject']}</td>
<td>{task['deadline']}</td>
<td>{pb_html}</td>
<td>{task['status']}</td>
<td style="color:{header_text}; font-size:12px;">See below</td>
</tr>"""

    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

    # 4. ACTION COLUMN
    st.markdown(f"<p style='color:{header_text}; margin-bottom: 5px; font-family: Inter, sans-serif;'>Task Actions</p>", unsafe_allow_html=True)
    for task in tasks:
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1:
            st.markdown(f"<div style='padding-top:8px; color:{text_color}; font-weight: 500; font-family: Inter, sans-serif;'>{task['title']}</div>", unsafe_allow_html=True)
        with c2:
            if st.button("Done", key=f"done_{task['task_id']}", use_container_width=True):
                update_task_status(task['task_id'], 'done', 100)
                st.rerun()
        with c3:
            if st.button("Delete", key=f"del_{task['task_id']}", use_container_width=True):
                delete_task(task['task_id'])
                st.rerun()

