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
        max-width: 750px !important;
    }
    
    /* Profile form card — frosted glass like rest of app */
    [data-testid="stForm"] {
        background: rgba(8, 6, 18, 0.55) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        padding: 24px !important;
    }
    [data-testid="stForm"] > div {
        background: transparent !important;
    }

    /* Input fields inside form — semi transparent */
    [data-testid="stForm"] .stTextInput input {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #FFFFFF !important;
    }

    /* Style subheaders, headings, and strong texts to be solid white */
    .main-content h3, .main-content h2, .main-content h1, .main-content strong {
        color: #FFFFFF !important;
    }

    /* Target profile specific typography to be highly legible */
    .main-content .stats-heading {
        color: #FFFFFF !important;
    }
    .main-content .stats-value {
        color: #FFFFFF !important;
    }
    .main-content .stats-label {
        color: rgba(255,255,255,0.7) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# PAGE TITLE & SUBTITLE
st.markdown("""
<div style="margin-bottom:28px;">
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
stats = get_profile_stats(user_id)

st.markdown("<div style='margin-top:32px;'>", 
    unsafe_allow_html=True)
st.markdown("""
<div class="stats-heading" style="font-family:'Instrument Serif',serif; 
font-style:italic; font-size:1.4rem; color:#FFFFFF; 
margin-bottom:16px;">Account Stats</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background:rgba(8,6,18,0.55); 
    border:1px solid rgba(255,255,255,0.1); 
    border-radius:10px; padding:20px; 
    backdrop-filter:blur(20px);
    position:relative; overflow:hidden;">
    <div style="position:absolute; top:0; left:0; right:0; 
    height:1px; background:linear-gradient(90deg, transparent, 
    rgba(255,255,255,0.12), transparent);"></div>
    <div class="stats-value" style="font-family:'Instrument Serif',serif; 
    font-style:italic; font-size:1.8rem; color:#FFFFFF; 
    line-height:1; letter-spacing:-0.5px;">
    {stats['member_since']}</div>
    <div class="stats-label" style="font-size:10px; color:rgba(255,255,255,0.7); 
    text-transform:uppercase; letter-spacing:0.1em; 
    margin-top:8px; font-weight:500;">Member Since</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background:rgba(8,6,18,0.55); 
    border:1px solid rgba(255,255,255,0.1); 
    border-radius:10px; padding:20px; 
    backdrop-filter:blur(20px);
    position:relative; overflow:hidden;">
    <div style="position:absolute; top:0; left:0; right:0; 
    height:1px; background:linear-gradient(90deg, transparent, 
    rgba(255,255,255,0.12), transparent);"></div>
    <div class="stats-value" style="font-family:'Instrument Serif',serif; 
    font-style:italic; font-size:1.8rem; color:#FFFFFF; 
    line-height:1; letter-spacing:-0.5px;">
    {stats['total_sessions']}</div>
    <div class="stats-label" style="font-size:10px; color:rgba(255,255,255,0.7); 
    text-transform:uppercase; letter-spacing:0.1em; 
    margin-top:8px; font-weight:500;">Total Sessions</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background:rgba(8,6,18,0.55); 
    border:1px solid rgba(255,255,255,0.1); 
    border-radius:10px; padding:20px; 
    backdrop-filter:blur(20px);
    position:relative; overflow:hidden;">
    <div style="position:absolute; top:0; left:0; right:0; 
    height:1px; background:linear-gradient(90deg, transparent, 
    rgba(255,255,255,0.12), transparent);"></div>
    <div class="stats-value" style="font-family:'Instrument Serif',serif; 
    font-style:italic; font-size:1.8rem; color:#FFFFFF; 
    line-height:1; letter-spacing:-0.5px;">
    {stats['tasks_created']}</div>
    <div class="stats-label" style="font-size:10px; color:rgba(255,255,255,0.7); 
    text-transform:uppercase; letter-spacing:0.1em; 
    margin-top:8px; font-weight:500;">Tasks Created</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
