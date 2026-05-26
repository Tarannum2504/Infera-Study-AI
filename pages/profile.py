import streamlit as st
import bcrypt
from database.db import update_user_profile, update_user_password, get_user_by_id, get_profile_stats

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.warning("Please log in to view this page.")
    st.stop()

user_id = st.session_state['user_id']

# Custom CSS matching design rules and block padding
st.markdown("""
    <style>
    .main .block-container {
        padding: 32px 40px !important;
        max-width: 1100px !important;
    }
    div[data-testid="stForm"] {
        background-color: #161B22 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    p, label, span, div {
        color: rgba(255,255,255,0.4) !important;
    }
    h1, h2, h3, h4, h5, h6, strong, b {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# PAGE TITLE & SUBTITLE
st.markdown("""
<div style="margin-bottom:28px;">
  <div style="font-size:11px; color:rgba(255,255,255,0.25); 
  text-transform:uppercase; letter-spacing:0.1em; 
  margin-bottom:8px;">// Profile</div>
  <div class="section-title">Profile Settings</div>
  <div class="section-sub">Manage your account details</div>
</div>
""", unsafe_allow_html=True)

# SECTION 1 — ACCOUNT DETAILS
st.subheader("Account Information")

with st.form("profile_form"):
    new_name = st.text_input("Full Name", value=st.session_state.get('name', ''))
    new_email = st.text_input("Email Address", value=st.session_state.get('email', ''))
    
    st.markdown("---")
    st.markdown("**Change Password**", unsafe_allow_html=True)
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    submitted = st.form_submit_button("Save Changes")
    
    if submitted:
        # Validate name
        if not new_name.strip():
            st.error("Name cannot be empty.")
        # Validate email
        elif not new_email.strip() or "@" not in new_email:
            st.error("Enter a valid email address.")
        else:
            # Update name and email in DB
            update_user_profile(user_id, new_name.strip(), new_email.strip())
            # Update session state
            st.session_state['name'] = new_name.strip()
            st.session_state['email'] = new_email.strip()
            
            pwd_error = False
            # Handle password change only if filled
            if current_password or new_password or confirm_password:
                if not current_password:
                    st.error("Enter your current password to change it.")
                    pwd_error = True
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                    pwd_error = True
                elif len(new_password) < 6:
                    st.error("New password must be at least 6 characters.")
                    pwd_error = True
                else:
                    # Verify current password with bcrypt
                    user_data = get_user_by_id(user_id)
                    if user_data and bcrypt.checkpw(current_password.encode('utf-8'), user_data['password'].encode('utf-8')):
                        # Hashing password using standard rounds
                        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
                        update_user_password(user_id, hashed_pw)
                    else:
                        st.error("Current password is incorrect.")
                        pwd_error = True
            
            if not pwd_error:
                st.success("Profile updated successfully.")

st.write("")

# SECTION 2 — ACCOUNT STATS
st.subheader("Account Stats")
stats = get_profile_stats(user_id)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Member Since", stats.get('member_since', 'N/A'))
with col2:
    st.metric("Total Sessions", stats.get('total_sessions', 0))
with col3:
    st.metric("Tasks Created", stats.get('tasks_created', 0))

st.markdown('</div>', unsafe_allow_html=True)
