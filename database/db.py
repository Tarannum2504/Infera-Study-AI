import sqlite3

DB_PATH = 'infera.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        failed_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP NULL,
        last_login TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locked_until ON users(locked_until)')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        subject TEXT,
        deadline DATE,
        priority TEXT,
        status TEXT DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date DATE,
        duration_minutes INTEGER,
        subject TEXT,
        session_type TEXT DEFAULT 'free',
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ai_plans (
        plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        input_text TEXT,
        generated_plan TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_message TEXT,
        ai_response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_tasks(user_id, subject_filter=None, status_filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]
    
    if subject_filter and subject_filter != "All":
        query += " AND subject = ?"
        params.append(subject_filter)
        
    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
        
    query += " ORDER BY deadline ASC, CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END"
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return [dict(row) for row in tasks]

def add_task(user_id, title, subject, deadline, priority, progress=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (user_id, title, subject, deadline, priority, status, progress)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    ''', (user_id, title, subject, deadline, priority, progress))
    conn.commit()
    conn.close()

def update_task_status(task_id, status, progress):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks SET status = ?, progress = ? WHERE task_id = ?
    ''', (status, progress, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
    conn.commit()
    conn.close()

def log_session(user_id, date, duration_minutes, subject, session_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO study_sessions (user_id, date, duration_minutes, subject, session_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, date, duration_minutes, subject, session_type))
    conn.commit()
    conn.close()

def get_recent_sessions(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, subject, duration_minutes, session_type 
        FROM study_sessions 
        WHERE user_id = ? 
        ORDER BY date DESC 
        LIMIT ?
    ''', (user_id, limit))
    sessions = cursor.fetchall()
    conn.close()
    return [dict(row) for row in sessions]

def get_session_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total_sessions, SUM(duration_minutes) as total_duration FROM study_sessions WHERE user_id = ?', (user_id,))
    totals = cursor.fetchone()
    
    cursor.execute('''
        SELECT subject, COUNT(*) as count 
        FROM study_sessions 
        WHERE user_id = ? 
        GROUP BY subject 
        ORDER BY count DESC 
        LIMIT 1
    ''', (user_id,))
    top_subject_row = cursor.fetchone()
    
    conn.close()
    
    total_sessions = totals['total_sessions'] if totals['total_sessions'] else 0
    total_duration = totals['total_duration'] if totals['total_duration'] else 0
    total_hours = round(total_duration / 60, 1)
    top_subject = top_subject_row['subject'] if top_subject_row else "None"
    
    return {
        'total_sessions': total_sessions,
        'total_hours': total_hours,
        'top_subject': top_subject
    }

def get_all_sessions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM study_sessions WHERE user_id = ? ORDER BY date ASC
    ''', (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return [dict(row) for row in sessions]

def add_ai_plan(user_id, input_text, generated_plan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ai_plans (user_id, input_text, generated_plan)
        VALUES (?, ?, ?)
    ''', (user_id, input_text, generated_plan))
    conn.commit()
    conn.close()

def save_chat(user_id, user_message, ai_response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, user_message, ai_response)
        VALUES (?, ?, ?)
    ''', (user_id, user_message, ai_response))
    conn.commit()
    conn.close()


def get_dashboard_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(duration_minutes)/60.0 as total_hours FROM study_sessions WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    total_hours = row['total_hours'] if row and row['total_hours'] else 0.0
    
    cursor.execute("SELECT COUNT(*) as tasks_done FROM tasks WHERE user_id=? AND status='done'", (user_id,))
    tasks_done = cursor.fetchone()['tasks_done']
    
    cursor.execute("SELECT COUNT(*) as active_tasks FROM tasks WHERE user_id=? AND status != 'done'", (user_id,))
    active_tasks = cursor.fetchone()['active_tasks']
    
    conn.close()
    return {
        'total_hours': total_hours,
        'tasks_done': tasks_done,
        'active_tasks': active_tasks
    }

def get_weekly_hours(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, SUM(duration_minutes)/60.0 as hours 
        FROM study_sessions
        WHERE user_id=? AND date >= date('now', '-7 days')
        GROUP BY date 
        ORDER BY date
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_subject_breakdown(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subject, SUM(duration_minutes)/60.0 as hours 
        FROM study_sessions
        WHERE user_id=? 
        GROUP BY subject 
        ORDER BY hours DESC 
        LIMIT 5
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_pending_tasks(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, subject, deadline, priority 
        FROM tasks
        WHERE user_id=? AND status != 'done'
        ORDER BY deadline ASC 
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_streak(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT date(date) as d 
        FROM study_sessions 
        WHERE user_id=? 
        ORDER BY d DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 0
        
    from datetime import datetime, timedelta
    streak = 0
    current_date = datetime.now().date()
    
    dates = [datetime.strptime(r['d'], '%Y-%m-%d').date() for r in rows if r['d']]
    if not dates:
        return 0
        
    if current_date not in dates and (current_date - timedelta(days=1)) not in dates:
        return 0
        
    check_date = dates[0]
    for d in dates:
        if d == check_date:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
            
    return streak

def update_user_profile(user_id, name, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET name=?, email=? WHERE user_id=?
    ''', (name, email, user_id))
    conn.commit()
    conn.close()

def update_user_password(user_id, new_hashed_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET password=? WHERE user_id=?
    ''', (new_hashed_password, user_id))
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_profile_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT created_at FROM users WHERE user_id=?', (user_id,))
    user_row = cursor.fetchone()
    member_since = user_row['created_at'] if user_row else None
    
    cursor.execute('SELECT COUNT(*) as count FROM study_sessions WHERE user_id=?', (user_id,))
    sessions_row = cursor.fetchone()
    total_sessions = sessions_row['count'] if sessions_row else 0
    
    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id=?', (user_id,))
    tasks_row = cursor.fetchone()
    tasks_created = tasks_row['count'] if tasks_row else 0
    
    conn.close()
    
    return {
        'member_since': member_since[:10] if member_since else 'N/A',
        'total_sessions': total_sessions,
        'tasks_created': tasks_created
    }

def update_task_progress(task_id, progress, status):
    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET progress=?, status=? WHERE task_id=?",
        (progress, status, task_id)
    )
    conn.commit()
    conn.close()
