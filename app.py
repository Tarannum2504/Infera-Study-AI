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
            background-color: #161B22;
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
                st.Page("pages/tasks.py", title="Tasks"),
                st.Page("pages/sessions.py", title="Sessions"),
                st.Page("pages/pomodoro.py", title="Pomodoro"),
                st.Page("pages/analytics.py", title="Analytics"),
                st.Page("pages/chat.py", title="Chat"),
                st.Page("pages/planner.py", title="AI Study Planner"),
            ]
            pg = st.navigation(pages)
            
            with st.sidebar:
                st.write(f"Welcome, {st.session_state.get('name')}!")
                if st.button("Logout"):
                    logout()

    pg.run()

if __name__ == "__main__":
    main()
