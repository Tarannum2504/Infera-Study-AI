import streamlit as st
import datetime
from database.db import get_tasks, add_task, update_task_status, delete_task

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
/* Custom style to turn buttons under .btn-primary-container into white primary elements */
.btn-primary-container button {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.btn-primary-container button:hover {
    background: rgba(255,255,255,0.9) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Fetch tasks to get count
all_tasks = get_tasks(user_id)
total_tasks = len(all_tasks)

# HEADER
st.markdown(f"""
<div style="margin-bottom:28px;">
  <div style="display:flex; align-items:center; gap:12px;">
    <div class="section-title">Task Manager</div>
    <span style="background:rgba(255,255,255,0.07); border:1px solid 
    rgba(255,255,255,0.1); border-radius:99px; padding:2px 10px; 
    font-size:11px; color:rgba(255,255,255,0.5);">{total_tasks} tasks</span>
  </div>
</div>
""", unsafe_allow_html=True)

# 1. ADD TASK — collapsed by default
with st.expander("+ Add Task", expanded=False):
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Title")
        subject = st.text_input("Subject")
        
        c_date, c_prio = st.columns(2)
        with c_date:
            deadline = st.date_input("Deadline", value=datetime.date.today())
        with c_prio:
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            
        progress = st.slider("Progress", 0, 100, 0)
        
        st.markdown("<div class='btn-primary-container'>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Task")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if submitted:
            if title.strip() and subject.strip():
                add_task(user_id, title.strip(), subject.strip(), deadline, priority.lower(), progress)
                st.success("Task added successfully!")
                st.rerun()
            else:
                st.error("Please fill in Title and Subject.")

# Extract unique subjects for filtering
subjects = sorted(list(set([t['subject'] for t in all_tasks])))
subjects.insert(0, "All")

# 2. FILTER BAR
col_f1, col_f2 = st.columns(2)
with col_f1:
    subject_filter = st.selectbox("Filter by Subject", subjects, key="subj_filter")
with col_f2:
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_progress", "done"], key="stat_filter")

# Fetch filtered tasks
tasks = get_tasks(user_id, subject_filter, status_filter)

# 3. TASK TABLE
if not tasks:
    st.markdown("<p style='font-size:13px; color:rgba(255,255,255,0.3); margin-top:20px;'>No tasks found matching current filters.</p>", unsafe_allow_html=True)
else:
    def get_progress_color(p):
        if p <= 25: return "#EF5350"     # red
        if p <= 50: return "#FF7043"     # orange
        if p <= 75: return "#FDD835"     # yellow
        if p <= 99: return "#A0A0A0"     # grey
        return "#66BB6A"                 # green

    table_html = """
    <table class="data-table">
    <thead>
      <tr>
        <th>Task Name</th>
        <th>Subject</th>
        <th>Deadline</th>
        <th style="width: 25%;">Progress</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
    """

    for task in tasks:
        p = task['progress']
        color = get_progress_color(p)
        pb_html = f"""
        <div class="progress-track">
          <div class="progress-fill" style="width:{p}%; background:{color};"></div>
        </div>
        <div style="font-size:10px; color:rgba(255,255,255,0.3); margin-top:3px;">{p}%</div>
        """
        
        table_html += f"""
        <tr>
          <td>{task['title']}</td>
          <td>{task['subject']}</td>
          <td>{task['deadline']}</td>
          <td>{pb_html}</td>
          <td><span style="font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5);">{task['status']}</span></td>
          <td style="font-size:11px; color:rgba(255,255,255,0.25);">See below</td>
        </tr>
        """

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    # 4. QUICK ACTIONS SECTION
    st.markdown("""
    <div style="font-size:10px; color:rgba(255,255,255,0.25); 
    text-transform:uppercase; letter-spacing:0.08em; margin: 24px 0 10px;">
    Quick Actions</div>
    """, unsafe_allow_html=True)
    
    for task in tasks:
        c1, c2, c3 = st.columns([6, 2, 2])
        with c1:
            st.markdown(f"<div style='padding-top:8px; color:rgba(255,255,255,0.85); font-size:13px; font-weight: 500;'>{task['title']}</div>", unsafe_allow_html=True)
        with c2:
            if st.button("Done ✓", key=f"done_{task['task_id']}", use_container_width=True):
                update_task_status(task['task_id'], 'done', 100)
                st.rerun()
        with c3:
            if st.button("Delete ×", key=f"del_{task['task_id']}", use_container_width=True):
                delete_task(task['task_id'])
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
