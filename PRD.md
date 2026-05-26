# Project Requirements Document (PRD): Infera Study AI

## 1. Product Overview
**Infera Study AI** is a comprehensive, AI-driven study productivity web application designed to help students track study sessions, manage academic tasks, utilize time management techniques, and receive personalized AI academic mentoring and planning. The app is crafted with a highly refined, premium, and minimal dark theme to provide a state-of-the-art visual experience.

---

## 2. Key Features

### 2.1 User Authentication
* Secure login and registration.
* Passwords securely hashed with `bcrypt`.
* User-specific isolated data (tasks, sessions, plans).

### 2.2 Minimalist Dashboard (`pages/dashboard.py`)
* Designed with a clean, high-performance, and minimalist layout.
* **KPI Metrics** (displayed side-by-side using `st.columns(3)` & `st.metric`):
  * **Study Hours**: Total accumulated study duration (`SUM(duration_minutes)/60.0` from `study_sessions`).
  * **Focus Score**: Dynamically computed overall focus percentage.
  * **Tasks Completed**: Count of completed tasks (`status='done'`).
* **High Priority & Upcoming**: Table displaying the top 5 high-priority pending tasks, sorted by deadline.
* **Upcoming Deadlines**: Table displaying the top 5 pending tasks with a deadline on or after today, sorted by deadline.
* No charts, no streak metrics, no active task count to keep the home screen clean.

### 2.3 Task Manager (`pages/tasks.py`)
* Add, edit, delete, and track academic tasks.
* Status tracking (Pending vs. Done).
* Priority levels and deadlines.

### 2.4 Infera Flow (`pages/infera_flow.py`)
* Replaced the standard Pomodoro timer with a custom "Infera Flow" focused study module.
* Live countdown timer with 25-minute study blocks.
* Four essential actions arranged in a row: **Start Flow**, **Pause Flow**, **Reset Flow**, and **Complete Flow**.
* **Complete Flow Logic**:
  * Stops the timer immediately.
  * Calculates actual elapsed study time (minimum of 1 minute).
  * Automatically logs the study session to the database with a user-defined subject (defaults to "General").
  * Displays a success notification and resets the timer to 25:00.
* Counts and displays completed study blocks for the current day.

### 2.5 Analytics (`pages/analytics.py`)
* Merged and consolidated all study logs and historical metrics into a single high-performance analytics terminal.
* **KPI Summaries** (`st.columns(4)`):
  * Total Study Hours.
  * Focus Score (0–100).
  * Completed Tasks.
  * Productivity % (`completed_tasks / total_tasks * 100`).
* **Greyscale Data Visualizations** (Altair-powered):
  * *Weekly Study Hours*: 7-day rolling study duration (Bar Chart).
  * *Subject Distribution*: Study hours broken down by subject (Horizontal Bar Chart).
  * *Productivity Trend*: Daily focus score tracking over time (Line Chart).
* **Recent Sessions**: High-fidelity table displaying the last 20 study sessions (Date, Subject, Duration) with status marked as `"Complete"` (duration >= 25 mins) or `"Partial"`.
* **AI Productivity Insight**: Leverages Meta's Llama-3.1-8b-instruct model to analyze the user's historical study sessions and tasks and generate highly personalized actionable productivity recommendations.

### 2.6 AI Study Planner (`pages/planner.py`)
* User inputs syllabus topics, available days, and study hours per day.
* Interacts with Meta's Llama-3.1-8b-instruct to generate a detailed, structured, day-by-day study roadmap.
* Saves generated plans to the database for future reference.

### 2.7 AI Study Assistant Chat (`pages/chat.py`)
* Conversational UI interacting with "Infera", a dedicated academic mentor.
* Context-aware chat using the last 10 messages of conversation history.
* Powered by Llama-3.1-8b-instruct.

### 2.8 Profile Settings (`pages/profile.py`)
* **Account Information**: Supports updating the user's Full Name and Email Address.
* **Change Password**: Custom module verifying the current password via `bcrypt` and updating it securely in the database.
* **Account Stats**: Read-only dashboard metrics:
  * *Member Since*: Account creation date.
  * *Total Sessions*: Number of logged study sessions.
  * *Tasks Created*: Total number of created tasks.

---

## 3. Sidebar Navigation & Layout (`app.py`)
* Completely redesigned minimalist sidebar navigation using a solid `#0E1117` background.
* Custom routing defined programmatically via `st.navigation(pages, position="hidden")` and custom buttons.
* Navigation buttons rendered as clean white text links with transparent backgrounds and no borders or rounded corners.
* The active page is highlighted with a vertical white left border indicator (`2px solid #FFFFFF`) using inline HTML/markdown.
* **Sidebar Bottom Section**:
  * Cleanly separated by a thin `#2A2F36` divider.
  * Displays a small `"Welcome back,"` greeting and the user's name in bold white.
  * Contains a small, custom-styled, minimal **Logout** button fixed at the bottom.
* **Routing Order**:
  1. Dashboard
  2. Planner
  3. Task Manager
  4. Infera Flow
  5. Analytics
  6. AI Assistant
  7. Profile

---

## 4. Technology Stack
* **Frontend/Framework:** Streamlit (utilizing new standard layout parameters like `width='stretch'` to eliminate deprecation warnings).
* **Backend Logic:** Python
* **Database:** SQLite (`infera.db`) using the standard `sqlite3` driver.
* **Data Visualization:** Pandas, Altair
* **AI/LLM Provider:** Hugging Face `InferenceClient` (model: `meta-llama/llama-3.1-8b-instruct` via novita provider).
* **Environment Management:** `python-dotenv` for managing `HF_API_KEY`.

---

## 5. Design & Security Guidelines
* **Strict Dark Mode Theme**: Background `#0E1117`, Cards/Containers `#161B22`, Borders `#2A2F36`.
* **Aesthetics**: High-contrast minimalist design. Texts must be White (`#FFFFFF`) or light gray (`#A0A0A0`). Absolutely no bright colors, rounded buttons in main navigations, emojis, or heavy image assets.
* **Database Security**: Database connections opened and closed on a per-query/action basis to prevent locks.
* **Credential Protection**: Passwords securely hashed using standard `bcrypt` cost factor rounds (12).
