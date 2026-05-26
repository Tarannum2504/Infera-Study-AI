import streamlit as st
from database.db import init_db
from components.auth import auth_page, logout, is_session_valid

def main():
    init_db()

    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        [data-testid="stSidebar"] {
            background-color: #0E1117;
            border-right: 1px solid #2A2F36;
        }
        p, div, span, label {
            color: #A0A0A0 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        pg = st.navigation([st.Page(auth_page, title="Login / Register")])
    else:
        # Check session validity
        if not is_session_valid():
            pg = st.navigation([st.Page(auth_page, title="Login / Register")])
        else:
            pages = [
                st.Page("pages/dashboard.py", title="Dashboard"),
                st.Page("pages/planner.py", title="Planner"),
                st.Page("pages/tasks.py", title="Task Manager"),
                st.Page("pages/infera_flow.py", title="Infera Flow"),
                st.Page("pages/analytics.py", title="Analytics"),
                st.Page("pages/chat.py", title="AI Assistant"),
                st.Page("pages/profile.py", title="Profile"),
            ]
            pg = st.navigation(pages, position="hidden")
            
            with st.sidebar:
                st.markdown("""
                    <style>
                    [data-testid="stSidebar"] {
                        background-color: #0E1117 !important;
                        border-right: 1px solid #2A2F36 !important;
                    }
                    /* Nav items styling */
                    [data-testid="stSidebar"] .stButton > button {
                        background-color: transparent !important;
                        border: none !important;
                        color: #FFFFFF !important;
                        text-align: left !important;
                        display: flex !important;
                        justify-content: flex-start !important;
                        padding: 8px 0 !important;
                        border-radius: 0 !important;
                        box-shadow: none !important;
                        font-size: 16px !important;
                        font-weight: 500 !important;
                        width: 100% !important;
                    }
                    [data-testid="stSidebar"] .stButton > button:hover {
                        color: #FFFFFF !important;
                        background-color: transparent !important;
                    }
                    [data-testid="stSidebar"] .stButton > button:focus {
                        color: #FFFFFF !important;
                        background-color: transparent !important;
                        box-shadow: none !important;
                    }
                    /* Specific styling for logout button */
                    [data-testid="stSidebar"] div.logout-btn button {
                        border: 1px solid #2A2F36 !important;
                        border-radius: 4px !important;
                        color: #A0A0A0 !important;
                        font-size: 12px !important;
                        padding: 4px 10px !important;
                        text-align: center !important;
                        width: auto !important;
                        display: inline-block !important;
                    }
                    [data-testid="stSidebar"] div.logout-btn button:hover {
                        border-color: #FFFFFF !important;
                        color: #FFFFFF !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                
                # Render custom navigation links
                for p in pages:
                    is_active = (pg.title == p.title)
                    if is_active:
                        st.markdown("<div style='border-left: 2px solid #FFFFFF; padding-left: 10px;'>", unsafe_allow_html=True)
                        if st.button(p.title, key=f"nav_{p.title.lower().replace(' ', '_')}", use_container_width=True):
                            st.switch_page(p)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='padding-left: 12px;'>", unsafe_allow_html=True)
                        if st.button(p.title, key=f"nav_{p.title.lower().replace(' ', '_')}", use_container_width=True):
                            st.switch_page(p)
                        st.markdown("</div>", unsafe_allow_html=True)

                # Sidebar Bottom section (divider + fixed block)
                st.markdown("<div style='position:fixed; bottom:20px; width:200px;'>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:0; border: none; border-top: 1px solid #2A2F36; margin-bottom: 10px;'>", unsafe_allow_html=True)
                st.markdown("<p style='font-size: 12px; margin-bottom: 2px; color: #A0A0A0; font-family: inherit;'>Welcome back,</p>", unsafe_allow_html=True)
                
                user_name = st.session_state.get('name', 'User')
                st.markdown(f"<p style='color: white; font-weight: bold; margin-bottom: 12px; font-size: 16px; font-family: inherit;'>{user_name}</p>", unsafe_allow_html=True)
                
                st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
                if st.button("Logout", key="logout_btn"):
                    logout()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    pg.run()

if __name__ == "__main__":
    main()
