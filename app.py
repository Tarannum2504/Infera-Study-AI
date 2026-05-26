import streamlit as st
from database.db import init_db
from components.auth import auth_page, logout, is_session_valid

def main():
    init_db()

    # Global CSS injection
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap');

        /* ── Reset & Base ── */
        * { box-sizing: border-box; margin: 0; padding: 0; }

        .stApp {
            background-color: #080A0F !important;
            font-family: 'Inter', sans-serif !important;
            color: #FFFFFF !important;
        }

        /* ── Hide Streamlit chrome ── */
        #MainMenu, footer, header { visibility: hidden !important; }
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: #0D0F14 !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] > div {
            padding: 0 !important;
            height: 100vh;
            display: flex;
            flex-direction: column;
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

        /* ── Navigation items ── */
        .nav-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 9px 16px;
            margin: 1px 8px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 400;
            color: rgba(255,255,255,0.45);
            transition: all 0.15s ease;
            text-decoration: none;
            border: none;
            background: transparent;
            width: calc(100% - 16px);
            text-align: left;
        }
        .nav-item:hover {
            background: rgba(255,255,255,0.05);
            color: rgba(255,255,255,0.85);
        }
        .nav-item.active {
            background: rgba(255,255,255,0.07);
            color: #FFFFFF;
            font-weight: 500;
        }
        .nav-dot {
            width: 5px; height: 5px;
            border-radius: 50%;
            background: rgba(255,255,255,0.25);
            flex-shrink: 0;
        }
        .nav-item.active .nav-dot {
            background: #FFFFFF;
        }

        /* ── Transparent button overlay for nav ── */
        .sidebar-btn-overlay button {
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            width: calc(100% - 16px) !important;
            height: 35px !important;
            margin-left: 8px !important;
            margin-top: -37px !important; /* Slide up to overlap the nav-item exactly */
            padding: 0 !important;
            z-index: 10 !important;
            cursor: pointer !important;
            box-shadow: none !important;
        }
        .sidebar-btn-overlay button:hover, .sidebar-btn-overlay button:focus {
            background: transparent !important;
            color: transparent !important;
            box-shadow: none !important;
        }

        /* ── Bottom section buttons styling ── */
        .bottom-btn-container {
            position: fixed !important;
            bottom: 14px !important;
            width: 208px !important; /* 240px - 32px padding */
            left: 16px !important;
            z-index: 100 !important;
            display: flex !important;
            gap: 8px !important;
        }
        .bottom-btn-container button {
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 6px !important;
            padding: 5px 10px !important;
            font-size: 11px !important;
            color: rgba(255,255,255,0.6) !important;
            width: 100% !important;
            text-align: center !important;
            cursor: pointer !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 450 !important;
        }
        .bottom-btn-container button:hover {
            background: rgba(255,255,255,0.1) !important;
            border-color: rgba(255,255,255,0.15) !important;
            color: #FFFFFF !important;
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

        /* ── Input fields ── */
        .stTextInput input, .stTextArea textarea,
        .stSelectbox select, .stNumberInput input {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            padding: 10px 14px !important;
            transition: border-color 0.2s ease !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(255,255,255,0.25) !important;
            outline: none !important;
            box-shadow: none !important;
        }
        .stTextInput label, .stTextArea label,
        .stSelectbox label, .stNumberInput label {
            color: rgba(255,255,255,0.4) !important;
            font-size: 11px !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.07em !important;
        }

        /* ── Buttons ── */
        .stButton button {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
        }
        .stButton button:hover {
            background: rgba(255,255,255,0.1) !important;
            border-color: rgba(255,255,255,0.2) !important;
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

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { 
            background: rgba(255,255,255,0.1); 
            border-radius: 99px; 
        }

        /* ── Page transition feel ── */
        .main-content {
            animation: fadeUp 0.25s ease forwards;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Streamlit metric override ── */
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 10px !important;
            padding: 16px !important;
        }
        [data-testid="stMetricValue"] {
            font-family: 'Instrument Serif', serif !important;
            font-style: italic !important;
            font-size: 2rem !important;
            color: #FFFFFF !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            color: rgba(255,255,255,0.35) !important;
        }

        /* ── Altair/Vega chart background ── */
        .vega-embed { background: transparent !important; }
        canvas { background: transparent !important; }
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

            # TOP — Logo block
            st.sidebar.markdown("""
                <div style="padding:20px 16px 16px;">
                  <div style="font-family:'Instrument Serif',serif; font-style:italic; 
                  font-size:1.2rem; color:#FFFFFF; letter-spacing:-0.3px;">Infera</div>
                  <div style="font-size:10px; color:rgba(255,255,255,0.25); 
                  margin-top:2px; text-transform:uppercase; letter-spacing:0.1em;">
                  Study AI</div>
                </div>
                <div class="subtle-divider" style="margin:0;"></div>
            """, unsafe_allow_html=True)

            # MIDDLE — Navigation Label
            st.sidebar.markdown("""
                <div style="font-size:10px; color:rgba(255,255,255,0.2); 
                text-transform:uppercase; letter-spacing:0.1em; padding:12px 16px 4px;">
                Navigation</div>
            """, unsafe_allow_html=True)

            # RENDER Custom Navigation links
            # We iterate over the first 6 pages in the list (excluding Profile)
            for p in pages[:-1]:
                is_active = (pg.title == p.title)
                st.sidebar.markdown(f"""
                    <div class="nav-item {'active' if is_active else ''}">
                      <div class="nav-dot"></div>
                      {p.title}
                    </div>
                """, unsafe_allow_html=True)

                # Transparent Overlay Button
                st.sidebar.markdown("<div class='sidebar-btn-overlay'>", unsafe_allow_html=True)
                if st.sidebar.button("", key=f"btn_overlay_{p.title.lower().replace(' ', '_')}"):
                    st.switch_page(p)
                st.sidebar.markdown("</div>", unsafe_allow_html=True)

            # BOTTOM — User block (fixed bottom background card)
            user_name = st.session_state.get('name', 'User')
            st.sidebar.markdown(f"""
                <div style="position:fixed; bottom:0; left:0; width:240px; height:95px;
                padding:14px 16px; border-top:1px solid rgba(255,255,255,0.06); 
                background:#0D0F14; z-index:90;">
                  <div style="font-size:10px; color:rgba(255,255,255,0.25); 
                  text-transform:uppercase; letter-spacing:0.08em;">Logged in as</div>
                  <div style="font-size:13px; font-weight:500; color:#FFFFFF; 
                  margin-top:3px;">{user_name}</div>
                </div>
            """, unsafe_allow_html=True)

            # Fixed overlay columns for Profile & Logout buttons
            st.sidebar.markdown("<div class='bottom-btn-container'>", unsafe_allow_html=True)
            col_prof, col_logo = st.sidebar.columns(2)
            with col_prof:
                if st.button("Profile", key="sidebar_profile_btn"):
                    st.switch_page("pages/profile.py")
            with col_logo:
                if st.button("Logout", key="sidebar_logout_btn"):
                    logout()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)

    pg.run()

if __name__ == "__main__":
    main()
