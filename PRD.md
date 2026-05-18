# Project Requirements Document (PRD): Infera Study AI

## 1. Product Overview
**Infera Study AI** is a comprehensive, AI-driven study productivity web application designed to help students track study sessions, manage academic tasks, utilize time management techniques, and receive personalized AI academic mentoring and planning. 

## 2. Key Features

### 2.1 User Authentication
* Secure login and registration.
* User-specific isolated data (tasks, sessions, plans).

### 2.2 Analytics Dashboard (`pages/dashboard.py`)
* Dynamic KPI cards displaying: Total Study Hours, Tasks Done, Active Tasks, and Day Streak.
* Visual analytics powered by Altair:
  * 7-day rolling study hours (Bar chart).
  * Top 5 subjects by study duration (Horizontal bar chart).
* Overview of recent pending tasks.

### 2.3 Task Management (`pages/tasks.py`)
* Add, edit, delete, and track academic tasks.
* Status tracking (e.g., Pending, Done).
* Priority levels and deadlines.

### 2.4 Study Sessions & Pomodoro (`pages/sessions.py` & `pages/pomodoro.py`)
* Manual logging of study sessions (date, duration, subject, type).
* Integrated Pomodoro timer functionality to encourage focused study blocks.

### 2.5 AI Study Planner (`pages/planner.py`)
* Inputs user's syllabus/topics, available days, and hours per day.
* Interacts with Meta's Llama-3.1-8b-instruct (via Hugging Face API) to generate a realistic, structured, day-by-day schedule.
* Saves generated plans to the database for future reference.

### 2.6 AI Study Assistant Chat (`pages/chat.py`)
* A conversational UI interacting with "Infera", a dedicated academic study mentor.
* Context-aware chat using the last 10 messages of conversation history.
* Powered by Llama-3.1-8b-instruct (Hugging Face API).

## 3. Technology Stack
* **Frontend/Framework:** Streamlit
* **Backend Logic:** Python
* **Database:** SQLite (`infera.db`) using standard `sqlite3` driver.
* **Data Visualization:** Pandas, Altair
* **AI/LLM Provider:** Hugging Face `InferenceClient` (model: `meta-llama/llama-3.1-8b-instruct` via novita provider).
* **Environment Management:** `python-dotenv` for managing `HF_API_KEY`.

## 4. Design Guidelines
* **Theme:** Strict Dark Mode.
* **Colors:** Background `#0E1117`, Cards/Containers `#161B22`, Borders `#2A2F36`.
* **Typography & Accents:** All text must be White (`#FFFFFF`) or light gray (`#A0A0A0`). No bright colors.

## 5. Security & Deployment
* Passwords hashed via `bcrypt` before database insertion.
* Database connections opened and closed on a per-query/action basis to prevent locks.
* API Keys stored strictly in `.env` and excluded from version control.
