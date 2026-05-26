import streamlit as st
import bcrypt
import sqlite3
import re
import time
from datetime import datetime, timedelta
from database.db import get_connection

# Rate limiting storage (use Redis or database in production with multiple users)
FAILED_LOGINS = {}

def hash_password(password: str) -> str:
    """Hash password with bcrypt - 12 rounds is secure and performant"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_rate_limited(email: str) -> tuple[bool, str]:
    """
    Prevent brute-force attacks with progressive delays and lockouts
    Returns: (is_limited, message)
    """
    if email not in FAILED_LOGINS:
        return False, ""
    
    attempts, first_attempt, lockout_until = FAILED_LOGINS[email]
    
    # Check if account is currently locked
    if lockout_until and datetime.now() < lockout_until:
        remaining = (lockout_until - datetime.now()).seconds // 60
        return True, f"Too many failed attempts. Try again in {remaining} minutes."
    
    # Reset after 15 minutes of inactivity
    if datetime.now() - first_attempt > timedelta(minutes=15):
        del FAILED_LOGINS[email]
        return False, ""
    
    # Progressive delay for repeated failures
    if attempts >= 3:
        time.sleep(2)  # 2 second delay after 3 failures
    elif attempts >= 2:
        time.sleep(1)  # 1 second delay after 2 failures
    
    return False, ""

def record_failed_login(email: str):
    """Track failed attempts for rate limiting and lockout"""
    now = datetime.now()
    
    if email not in FAILED_LOGINS:
        FAILED_LOGINS[email] = [1, now, None]
    else:
        attempts, first_attempt, _ = FAILED_LOGINS[email]
        attempts += 1
        
        # Lock account after 5 failed attempts within 15 minutes
        if attempts >= 5:
            lockout_until = now + timedelta(minutes=15)
            FAILED_LOGINS[email] = [attempts, first_attempt, lockout_until]
        else:
            FAILED_LOGINS[email] = [attempts, first_attempt, None]

def validate_email(email: str) -> bool:
    """Strict email format validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Enforce strong password requirements
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong ✓"

def login_user(email: str, password: str) -> bool:
    """
    Secure login with rate limiting, account lockout, and timing attack prevention
    """
    # Normalize email to lowercase
    email = email.lower().strip()
    
    # Check rate limiting before any database query
    is_limited, limit_message = is_rate_limited(email)
    if is_limited:
        st.error(limit_message)
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user with account status
        cursor.execute("""
            SELECT user_id, name, email, password, failed_attempts, locked_until 
            FROM users 
            WHERE email = ? AND is_active = 1
        """, (email,))
        user = cursor.fetchone()
        
        # Use timing attack prevention (same response time whether user exists or not)
        if not user:
            time.sleep(2)  # Simulate password check time
            record_failed_login(email)
            st.error("Invalid email or password")
            return False
        
        # Check if account is locked
        if user['locked_until']:
            lock_until = datetime.fromisoformat(user['locked_until'])
            if lock_until > datetime.now():
                remaining = (lock_until - datetime.now()).seconds // 60
                st.error(f"Account temporarily locked. Try again in {remaining} minutes.")
                return False
        
        # Verify password
        if check_password(password, user['password']):
            # Successful login - reset all failure tracking
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = 0, 
                    locked_until = NULL,
                    last_login = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (email,))
            conn.commit()
            
            # Clear rate limiting record
            if email in FAILED_LOGINS:
                del FAILED_LOGINS[email]
            
            # Set secure session state
            st.session_state.clear()  # Clear any existing session data
            st.session_state['user_id'] = user['user_id']
            st.session_state['name'] = user['name']
            st.session_state['email'] = user['email']
            st.session_state['logged_in'] = True
            st.session_state['login_time'] = datetime.now().isoformat()
            return True
        else:
            # Failed password attempt
            failed_attempts = user['failed_attempts'] + 1
            locked_until = None
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                locked_until = (datetime.now() + timedelta(minutes=15)).isoformat()
                st.error("Too many failed attempts. Account locked for 15 minutes.")
            
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = ?, locked_until = ?
                WHERE email = ?
            """, (failed_attempts, locked_until, email))
            conn.commit()
            
            # Track for rate limiting
            record_failed_login(email)
            
            # Generic error message (don't reveal if email exists vs wrong password)
            st.error("Invalid email or password")
            return False
            
    except Exception as e:
        # Log the error but show generic message
        print(f"Login error: {e}")  # In production, use proper logging
        st.error("An error occurred. Please try again later.")
        return False
    finally:
        conn.close()

def register_user(name: str, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Secure user registration with comprehensive validation
    Returns: (success, message)
    """
    # Input validation
    name = name.strip()
    if not name or len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name is too long (max 100 characters)"
    
    email = email.lower().strip()
    if not validate_email(email):
        return False, "Please enter a valid email address"
    
    if len(email) > 255:
        return False, "Email is too long"
    
    if password != confirm_password:
        return False, "Passwords do not match"
    
    is_valid, password_msg = validate_password_strength(password)
    if not is_valid:
        return False, password_msg
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists (but use generic error)
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Registration failed. Please try a different email."
        
        # Create new user
        cursor.execute("""
            INSERT INTO users (name, email, password, failed_attempts, created_at) 
            VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)
        """, (name, email, hash_password(password)))
        conn.commit()
        
        return True, "Registration successful! Please log in."
        
    except sqlite3.IntegrityError:
        # Generic error to prevent email enumeration
        return False, "Registration failed. Please try a different email."
    except Exception as e:
        print(f"Registration error: {e}")  # Log internally
        return False, "Registration failed. Please try again later."
    finally:
        conn.close()

def is_session_valid() -> bool:
    """Check if current session is still valid (not expired)"""
    if not st.session_state.get('logged_in', False):
        return False
    
    # Session timeout after 8 hours
    if 'login_time' in st.session_state:
        login_time = datetime.fromisoformat(st.session_state['login_time'])
        if datetime.now() - login_time > timedelta(hours=8):
            logout()
            return False
    
    return True

def auth_page():
    """Render authentication page with modern UI"""
    
    # Session expiry check
    if st.session_state.get('logged_in', False) and not is_session_valid():
        st.warning("Session expired. Please login again.")
        return

    st.markdown("""
    <style>
    /* Hide sidebar on auth page */
    [data-testid="stSidebar"] { display: none !important; }
    
    .auth-container {
        max-width: 400px;
        margin: 80px auto 0;
        padding: 0 20px;
    }
    .auth-logo {
        text-align: center;
        margin-bottom: 40px;
    }
    .auth-logo-text {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-size: 2.5rem;
        color: #FFFFFF;
        letter-spacing: -1px;
    }
    .auth-logo-sub {
        font-size: 11px;
        color: rgba(255,255,255,0.2);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 4px;
    }
    .auth-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 32px;
        position: relative;
        overflow: hidden;
    }
    .auth-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, 
            rgba(255,255,255,0.15), transparent);
    }
    .auth-title {
        font-family: 'Instrument Serif', serif;
        font-style: italic;
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    .auth-subtitle {
        font-size: 12px;
        color: rgba(255,255,255,0.3);
        margin-bottom: 24px;
    }
    .auth-switch {
        text-align: center;
        font-size: 12px;
        color: rgba(255,255,255,0.3);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Center the auth card
    _, center, _ = st.columns([1, 2, 1])
    
    with center:
        # Logo
        st.markdown("""
        <div class="auth-logo">
            <div class="auth-logo-text">Infera</div>
            <div class="auth-logo-sub">Study AI — Your Productivity OS</div>
        </div>
        """, unsafe_allow_html=True)

        # Tab switcher between Login and Register
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            st.markdown("""
            <div style="margin-bottom:20px;">
                <div class="auth-title">Welcome back</div>
                <div class="auth-subtitle">Sign in to continue your study session</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email address", 
                    placeholder="you@example.com")
                password = st.text_input("Password", 
                    type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In", 
                    use_container_width=True)
                
                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        if login_user(email, password):
                            st.rerun()
        
        with tab2:
            st.markdown("""
            <div style="margin-bottom:20px;">
                <div class="auth-title">Create account</div>
                <div class="auth-subtitle">Start your productivity journey</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form"):
                name = st.text_input("Full name", 
                    placeholder="Your name")
                email = st.text_input("Email address", 
                    placeholder="you@example.com")
                password = st.text_input("Password", 
                    type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm password", 
                    type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account",
                    use_container_width=True)
                
                if submitted:
                    if not all([name, email, password, confirm]):
                        st.error("Please fill in all fields")
                    else:
                        success, message = register_user(name, email, password, confirm)
                        if success:
                            st.success(message)
                            st.info("Please go to the Sign In tab to continue")
                        else:
                            st.error(message)

        # Style the tabs
        st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 8px !important;
            padding: 3px !important;
            gap: 2px !important;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px !important;
            color: rgba(255,255,255,0.4) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 8px 20px !important;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(255,255,255,0.08) !important;
            color: #FFFFFF !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
        }
        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }
        /* Make Sign In button white */
        .stForm [data-testid="stFormSubmitButton"] button {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 12px !important;
            border-radius: 8px !important;
            letter-spacing: 0.02em !important;
            margin-top: 8px !important;
            transition: all 0.15s ease !important;
        }
        .stForm [data-testid="stFormSubmitButton"] button:hover {
            background: rgba(255,255,255,0.9) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
        }
        </style>
        """, unsafe_allow_html=True)

def logout():
    """Secure logout with complete session cleanup"""
    # Clear all session state keys
    keys_to_remove = ['user_id', 'name', 'email', 'logged_in', 'login_time']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear any other session data
    st.session_state.clear()
    
    # Show success message and redirect
    st.success("Logged out successfully!")
    st.rerun()