import streamlit as st
import datetime
from database.db import get_tasks, add_task, update_task_status, delete_task, update_task_progress

# Auth check
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

def mark_done(task_id):
    update_task_status(task_id, 'done', 100)
    key = f"progress_slider_{task_id}"
    if key in st.session_state:
        del st.session_state[key]

# Custom padding system & Slider styling
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

/* Glass Card styling for Streamlit container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    padding: 16px 20px !important;
    transition: border-color 0.2s ease, transform 0.2s ease !important;
    margin-bottom: 16px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(255,255,255,0.15) !important;
}

/* Slim dark slider */
.stSlider [data-baseweb="slider"] {
    padding: 0 !important;
    margin: 0 !important;
}
.stSlider [data-testid="stSlider"] {
    padding: 0 !important;
}
/* Track */
.stSlider [data-baseweb="slider"] > div:first-child {
    height: 3px !important;
    background: rgba(255,255,255,0.08) !important;
    border-radius: 99px !important;
}
/* Filled portion - changes dynamically */
.stSlider [data-baseweb="slider"] [role="progressbar"] {
    background: rgba(255,255,255,0.4) !important;
    height: 3px !important;
}
/* Thumb handle */
.stSlider [data-baseweb="slider"] [role="slider"] {
    background: #FFFFFF !important;
    border: none !important;
    width: 12px !important;
    height: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5) !important;
    top: -4px !important;
}
.stSlider [role="slider"]:focus {
    box-shadow: 0 0 0 3px rgba(255,255,255,0.15) !important;
}
/* Hide slider label completely */
.stSlider label { display: none !important; }
/* Tooltip on drag */
.stSlider [data-baseweb="tooltip"] {
    background: rgba(13,15,20,0.95) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    font-size: 11px !important;
    padding: 4px 8px !important;
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

# 3. TASK CARDS LOOP (with inline interactive progress sliders)
if not tasks:
    st.markdown("<p style='font-size:13px; color:rgba(255,255,255,0.3); margin-top:20px;'>No tasks found matching current filters.</p>", unsafe_allow_html=True)
else:
    for task in tasks:
        task_id = task['task_id']
        current_progress = task['progress']
        
        # Determine progress bar color
        if current_progress <= 25:
            bar_color = "#E53935"
        elif current_progress <= 50:
            bar_color = "#FB8C00"
        elif current_progress <= 75:
            bar_color = "#FDD835"
        elif current_progress < 100:
            bar_color = "#A0A0A0"
        else:
            bar_color = "#43A047"
            
        # Custom premium glass card container per task using st.container(border=True)
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div style="font-size:14px; font-weight:600; color:#FFFFFF;">{task['title']}</div>
                <div style="font-size:10px; text-transform:uppercase; letter-spacing:0.05em; color:rgba(255,255,255,0.4); font-weight:600;">{task['priority']} priority</div>
            </div>
            <div style="display:flex; gap:16px; font-size:12px; color:rgba(255,255,255,0.6); margin-bottom:12px;">
                <div>Subject: <span style="color:#FFFFFF; font-weight:500;">{task['subject']}</span></div>
                <div>Deadline: <span style="color:#FFFFFF; font-weight:500;">{task['deadline']}</span></div>
                <div>Status: <span style="color:#FFFFFF; font-weight:500; text-transform:uppercase; font-size:10px;">{task['status']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar visualization
            st.markdown(f"""
            <div style="margin:4px 0 2px;">
                <div style="background:rgba(255,255,255,0.07); 
                border-radius:99px; height:5px; width:100%; overflow:hidden;">
                    <div style="background:{bar_color}; width:{current_progress}%; 
                    height:5px; border-radius:99px; 
                    transition:width 0.3s ease, background 0.3s ease;">
                    </div>
                </div>
                <div style="font-size:10px; color:rgba(255,255,255,0.3); 
                margin-top:3px;">{current_progress}% complete</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Inline progress slider
            new_progress = st.slider(
                label="",
                min_value=0,
                max_value=100,
                value=current_progress,
                step=5,
                key=f"progress_slider_{task_id}",
                label_visibility="collapsed"
            )
            
            # Auto-save when slider changes
            if new_progress != current_progress:
                # Update DB
                if new_progress == 100:
                    update_task_progress(task_id, new_progress, 'done')
                elif new_progress > 0:
                    update_task_progress(task_id, new_progress, 'in_progress')
                else:
                    update_task_progress(task_id, new_progress, 'pending')
                st.rerun()
                
            # Pinned Done and Delete buttons below the slider
            c1, c2 = st.columns([1, 1])
            with c1:
                st.button("Done ✓", key=f"done_{task_id}", use_container_width=True, on_click=mark_done, args=(task_id,))
            with c2:
                if st.button("Delete ×", key=f"del_{task_id}", use_container_width=True):
                    delete_task(task_id)
                    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
