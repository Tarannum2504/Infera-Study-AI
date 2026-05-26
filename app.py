import streamlit as st
from database.db import init_db
from components.auth import auth_page, logout, is_session_valid

# Force sidebar to start expanded
st.set_page_config(
    page_title="Infera Study AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    init_db()

    # Global CSS injection featuring Animated Subtle Grain Overlay and Glowing Orbs
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap');

        /* Base */
        html, body, .stApp {
            background-color: #060810 !important;
            font-family: 'Inter', sans-serif !important;
            color: #FFFFFF !important;
        }

        /* Animated orb background */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(ellipse 700px 500px at 15% 15%,
                    rgba(255,255,255,0.04) 0%,
                    transparent 70%),
                radial-gradient(ellipse 500px 400px at 85% 75%,
                    rgba(255,255,255,0.025) 0%,
                    transparent 65%),
                radial-gradient(ellipse 400px 600px at 60% 20%,
                    rgba(255,255,255,0.015) 0%,
                    transparent 60%);
            animation: orbShift 18s ease-in-out infinite alternate;
        }

        @keyframes orbShift {
            0%   { opacity: 0.7; transform: scale(1) translateY(0px); }
            33%  { opacity: 1;   transform: scale(1.05) translateY(-20px); }
            66%  { opacity: 0.8; transform: scale(0.97) translateY(10px); }
            100% { opacity: 1;   transform: scale(1.03) translateY(-10px); }
        }

        /* Noise texture overlay */
        .stApp::after {
            content: '';
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            opacity: 0.025;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)'/%3E%3C/svg%3E");
        }

        /* Ensure content renders above background */
        .main, [data-testid="stSidebar"],
        .block-container, section {
            position: relative;
            z-index: 1;
        }

        /* Page fade-in animation */
        .block-container {
            animation: pageIn 0.3s ease forwards;
            padding: 32px 40px !important;
            max-width: 1100px !important;
        }
        @keyframes pageIn {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Sidebar base ── */
        [data-testid="stSidebar"] {
            background: rgba(8, 10, 16, 0.95) !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
            backdrop-filter: blur(20px) !important;
        }

        /* Force sidebar toggle button to always show */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: all !important;
            z-index: 99999 !important;
            position: fixed !important;
            top: 16px !important;
            left: 16px !important;
            background: rgba(13,15,20,0.9) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
            padding: 6px !important;
            backdrop-filter: blur(10px) !important;
            cursor: pointer !important;
        }
        [data-testid="collapsedControl"]:hover,
        [data-testid="stSidebarCollapsedControl"]:hover {
            background: rgba(255,255,255,0.08) !important;
            border-color: rgba(255,255,255,0.2) !important;
        }
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {
            fill: rgba(255,255,255,0.6) !important;
            color: rgba(255,255,255,0.6) !important;
            width: 18px !important;
            height: 18px !important;
        }

        /* Sidebar open state — make sure it's visible */
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: block !important;
            visibility: visible !important;
            transform: translateX(0) !important;
            width: 288px !important;
        }

        /* Sidebar collapsed state */
        [data-testid="stSidebar"][aria-expanded="false"] {
            transform: translateX(-288px) !important;
            width: 288px !important;
        }

        /* Main content shifts when sidebar opens */
        [data-testid="stSidebar"][aria-expanded="true"] ~ 
        .main .block-container {
            margin-left: 288px !important;
            transition: margin-left 0.25s ease !important;
        }

        /* Nav button hover glow effect */
        [data-testid="stSidebar"] .stButton button {
            position: relative !important;
            overflow: hidden !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] .stButton button::before {
            content: '' !important;
            position: absolute !important;
            left: 0 !important; top: 0 !important; bottom: 0 !important;
            width: 2px !important;
            background: rgba(255,255,255,0) !important;
            transition: background 0.2s ease !important;
            border-radius: 0 !important;
        }
        [data-testid="stSidebar"] .stButton button:hover::before {
            background: rgba(255,255,255,0.4) !important;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background: rgba(255,255,255,0.06) !important;
            color: #FFFFFF !important;
            padding-left: 18px !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer { visibility: hidden !important; }
        [data-testid="stToolbar"] { display: none !important; }
        .stDeployButton { display: none !important; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { 
            background: rgba(255,255,255,0.08); 
            border-radius: 99px; 
        }

        /* ── Input fields ── */
        .stTextInput input, .stTextArea textarea,
        .stSelectbox select, .stNumberInput input {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            transition: border-color 0.2s ease !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(255,255,255,0.2) !important;
            box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
            outline: none !important;
        }
        .stTextInput label, .stTextArea label,
        .stSelectbox label, .stNumberInput label {
            color: rgba(255,255,255,0.35) !important;
            font-size: 10px !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        /* ── Buttons ── */
        .stButton button {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            border-radius: 8px !important;
            color: rgba(255,255,255,0.8) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
            letter-spacing: 0.01em !important;
        }
        .stButton button:hover {
            background: rgba(255,255,255,0.09) !important;
            border-color: rgba(255,255,255,0.18) !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
        }

        /* ── Primary button ── */
        .btn-primary {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        .btn-primary:hover {
            background: rgba(255,255,255,0.9) !important;
        }

        /* ── Metrics ── */
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 10px !important;
            padding: 16px 20px !important;
            position: relative !important;
            overflow: hidden !important;
            transition: border-color 0.2s ease !important;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(255,255,255,0.12) !important;
        }
        [data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, 
                rgba(255,255,255,0.12), transparent);
        }
        [data-testid="stMetricValue"] {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            font-size: 2.2rem !important;
            color: #FFFFFF !important;
            letter-spacing: -1px !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: rgba(255,255,255,0.3) !important;
            font-weight: 500 !important;
        }

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(255,255,255,0.06) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* ── Altair charts ── */
        .vega-embed, canvas { background: transparent !important; }

        /* ── Headings ── */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            color: #FFFFFF !important;
            letter-spacing: -0.5px !important;
        }
        p, span, div, label {
            color: rgba(255,255,255,0.75);
        }

        /* ── Liquid glass card ── */
        .glass-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 20px;
            transition: border-color 0.2s ease;
        }
        .glass-card:hover {
            border-color: rgba(255,255,255,0.15);
        }

        /* ── KPI metric cards ── */
        .kpi-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 10px;
            padding: 18px 20px;
            position: relative;
            overflow: hidden;
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,255,255,0.15), 
                transparent);
        }
        .kpi-value {
            font-family: 'Instrument Serif', serif;
            font-style: italic;
            font-size: 2.2rem;
            color: #FFFFFF;
            line-height: 1;
            letter-spacing: -1px;
        }
        .kpi-label {
            font-size: 11px;
            color: rgba(255,255,255,0.4);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 6px;
            font-weight: 500;
        }
        .kpi-delta {
            font-size: 11px;
            color: rgba(255,255,255,0.3);
            margin-top: 4px;
        }

        /* ── Section headings ── */
        .section-title {
            font-family: 'Instrument Serif', serif;
            font-style: italic;
            font-size: 1.8rem;
            color: #FFFFFF;
            letter-spacing: -0.5px;
            line-height: 1.1;
        }
        .section-sub {
            font-size: 12px;
            color: rgba(255,255,255,0.35);
            font-weight: 400;
            margin-top: 4px;
            letter-spacing: 0.02em;
        }

        /* ── Dividers ── */
        .subtle-divider {
            height: 1px;
            background: rgba(255,255,255,0.06);
            margin: 16px 0;
        }

        /* ── Table styling ── */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .data-table th {
            text-align: left;
            padding: 8px 12px;
            color: rgba(255,255,255,0.3);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .data-table td {
            padding: 10px 12px;
            color: rgba(255,255,255,0.8);
            border-bottom: 1px solid rgba(255,255,255,0.04);
            vertical-align: middle;
        }
        .data-table tr:hover td {
            background: rgba(255,255,255,0.02);
        }

        /* ── Progress bar ── */
        .progress-track {
            background: rgba(255,255,255,0.07);
            border-radius: 99px;
            height: 4px;
            width: 100%;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 99px;
            transition: width 0.3s ease;
        }

        /* ── Chat bubbles ── */
        .msg-user {
            display: flex;
            justify-content: flex-end;
            margin: 6px 0;
        }
        .msg-user-inner {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px 12px 2px 12px;
            padding: 10px 14px;
            max-width: 62%;
            font-size: 13px;
            line-height: 1.55;
            color: #FFFFFF;
        }
        .msg-ai {
            display: flex;
            justify-content: flex-start;
            margin: 6px 0;
        }
        .msg-ai-inner {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 2px 12px 12px 12px;
            padding: 10px 14px;
            max-width: 62%;
            font-size: 13px;
            line-height: 1.55;
            color: rgba(255,255,255,0.85);
        }

        /* ── Token stats badge ── */
        .token-badge {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 99px;
            padding: 5px 14px;
            font-size: 11px;
            color: rgba(255,255,255,0.35);
            font-family: 'Inter', sans-serif;
            margin-top: 8px;
        }
        .token-badge span {
            color: rgba(255,255,255,0.6);
            font-weight: 500;
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
            pages_list = [
                st.Page("pages/dashboard.py", title="Dashboard"),
                st.Page("pages/planner.py", title="Planner"),
                st.Page("pages/tasks.py", title="Task Manager"),
                st.Page("pages/infera_flow.py", title="Infera Flow"),
                st.Page("pages/analytics.py", title="Analytics"),
                st.Page("pages/chat.py", title="AI Assistant"),
                st.Page("pages/profile.py", title="Profile"),
            ]
            pg = st.navigation(pages_list, position="hidden")

            # Route mapping to resolve st.switch_page paths
            page_paths = {
                "Dashboard": "pages/dashboard.py",
                "Planner": "pages/planner.py",
                "Task Manager": "pages/tasks.py",
                "Infera Flow": "pages/infera_flow.py",
                "Analytics": "pages/analytics.py",
                "AI Assistant": "pages/chat.py",
                "Profile": "pages/profile.py"
            }

            # Map the currently selected streamlit page returned by st.navigation to keep state in sync
            title_to_key = {
                "Dashboard": "Dashboard",
                "Planner": "Planner",
                "Task Manager": "Task Manager",
                "Infera Flow": "Infera Flow",
                "Analytics": "Analytics",
                "AI Assistant": "AI Assistant",
                "Profile": "Profile"
            }
            st.session_state['current_page'] = title_to_key.get(pg.title, "Dashboard")

            with st.sidebar:
                # Logo block
                st.markdown("""
                <div style="padding:24px 20px 20px; border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="font-family:'Instrument Serif',serif; font-style:italic; 
                    font-size:1.3rem; color:#FFFFFF; letter-spacing:-0.3px;">Infera</div>
                    <div style="font-size:9px; color:rgba(255,255,255,0.2); margin-top:2px; 
                    text-transform:uppercase; letter-spacing:0.15em;">Study AI</div>
                </div>
                <div style="padding:16px 12px 8px; font-size:9px; color:rgba(255,255,255,0.2); 
                text-transform:uppercase; letter-spacing:0.12em;">Navigation</div>
                """, unsafe_allow_html=True)

                pages = ["Dashboard", "Planner", "Task Manager", 
                         "Infera Flow", "Analytics", "AI Assistant"]
                
                for page in pages:
                    is_active = st.session_state.get('current_page') == page
                    
                    # Style active vs inactive with CSS injection per button
                    if is_active:
                        st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:has(button[key="{page}_nav"]) button {{
                            background: rgba(255,255,255,0.08) !important;
                            color: #FFFFFF !important;
                            border: 1px solid rgba(255,255,255,0.12) !important;
                            text-align: left !important;
                            font-weight: 500 !important;
                            border-radius: 8px !important;
                            padding: 9px 14px !important;
                            width: 100% !important;
                            font-size: 13px !important;
                            margin: 1px 0 !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <style>
                        div[data-testid="stButton"]:has(button[key="{page}_nav"]) button {{
                            background: transparent !important;
                            color: rgba(255,255,255,0.45) !important;
                            border: 1px solid transparent !important;
                            text-align: left !important;
                            font-weight: 400 !important;
                            border-radius: 8px !important;
                            padding: 9px 14px !important;
                            width: 100% !important;
                            font-size: 13px !important;
                            margin: 1px 0 !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                    
                    if st.button(page, key=f"{page}_nav", use_container_width=True):
                        st.session_state['current_page'] = page
                        st.switch_page(page_paths[page])

                # Spacer to push bottom section down
                st.markdown("""
                <div style="flex:1; min-height:40px;"></div>
                """, unsafe_allow_html=True)

                # Bottom user section - fixed at bottom
                st.markdown("""
                <style>
                .user-bottom-block {
                    position: fixed;
                    bottom: 0;
                    left: 0;
                    width: 288px;
                    padding: 14px 16px;
                    background: #0D0F14;
                    border-top: 1px solid rgba(255,255,255,0.06);
                }
                .user-bottom-block .logged-label {
                    font-size: 9px;
                    color: rgba(255,255,255,0.2);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 4px;
                }
                .user-bottom-block .user-name {
                    font-size: 13px;
                    font-weight: 500;
                    color: #FFFFFF;
                    margin-bottom: 10px;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="user-bottom-block">
                    <div class="logged-label">Logged in as</div>
                    <div class="user-name">{st.session_state.get('name', 'User')}</div>
                </div>
                """, unsafe_allow_html=True)

                # Profile and Logout buttons pinned at bottom
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    <style>
                    div[data-testid="stButton"]:has(button[key="profile_nav"]) button {
                        background: rgba(255,255,255,0.05) !important;
                        border: 1px solid rgba(255,255,255,0.08) !important;
                        color: rgba(255,255,255,0.6) !important;
                        font-size: 11px !important;
                        padding: 6px 10px !important;
                        border-radius: 6px !important;
                        width: 100% !important;
                        position: fixed;
                        bottom: 16px;
                        left: 16px;
                        width: 120px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("Profile", key="profile_nav"):
                        st.session_state['current_page'] = 'Profile'
                        st.switch_page(page_paths['Profile'])
                with col2:
                    st.markdown("""
                    <style>
                    div[data-testid="stButton"]:has(button[key="logout_nav"]) button {
                        background: rgba(255,255,255,0.05) !important;
                        border: 1px solid rgba(255,255,255,0.08) !important;
                        color: rgba(255,255,255,0.6) !important;
                        font-size: 11px !important;
                        padding: 6px 10px !important;
                        border-radius: 6px !important;
                        position: fixed;
                        bottom: 16px;
                        left: 148px;
                        width: 120px !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    if st.button("Logout", key="logout_nav"):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()

    pg.run()

if __name__ == "__main__":
    main()
