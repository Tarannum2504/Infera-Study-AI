import streamlit as st
from database.db import get_tasks, add_task, update_task_status, delete_task

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Custom CSS matching strict design rules
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
.task-card {
    background-color: #161B22;
    border: 1px solid #2A2F36;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 10px;
}
.task-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #FFFFFF;
    margin-bottom: 8px;
}
.task-detail {
    color: #A0A0A0;
    font-size: 0.9rem;
    margin-bottom: 4px;
}
.priority-badge {
    font-weight: bold;
    color: #A0A0A0;
}
</style>
""", unsafe_allow_html=True)

st.title("Task Manager")

# 1. ADD TASK FORM
with st.container():
    st.subheader("Add New Task")
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title")
            subject = st.text_input("Subject")
        with col2:
            deadline = st.date_input("Deadline")
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if title and subject:
                add_task(user_id, title, subject, deadline, priority)
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
st.subheader("Your Tasks")
col_f1, col_f2 = st.columns(2)
with col_f1:
    subject_filter = st.selectbox("Filter by Subject", subjects, key="subj_filter")
with col_f2:
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "in_progress", "done"], key="stat_filter")

# 3. TASK CARDS
tasks = get_tasks(user_id, subject_filter, status_filter)

# 4. EMPTY STATE
if not tasks:
    st.info("No tasks yet. Add your first task above.")
else:
    for task in tasks:
        with st.container():
            st.markdown(f"""
            <div class="task-card">
                <div class="task-title">{task['title']}</div>
                <div class="task-detail">Subject: {task['subject']}</div>
                <div class="task-detail">Deadline: {task['deadline']}</div>
                <div class="task-detail">Priority: <span class="priority-badge">[ {task['priority'].upper()} ]</span></div>
                <div class="task-detail">Status: {task['status']}</div>
                <div class="task-detail">Progress: {task['progress']}% complete</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons placed below the card HTML
            col_b1, col_b2, col_empty = st.columns([2, 2, 8])
            with col_b1:
                if st.button("Mark Done", key=f"done_{task['task_id']}", use_container_width=True):
                    update_task_status(task['task_id'], 'done', 100)
                    st.rerun()
            with col_b2:
                if st.button("Delete", key=f"del_{task['task_id']}", use_container_width=True):
                    delete_task(task['task_id'])
                    st.rerun()
            
            # Add some spacing between task entries
            st.write("")
