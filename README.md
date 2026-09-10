# 🚀 AI Career Companion Agent

AI Career Companion Agent is an intelligent full-stack career platform powered by AI agents, Retrieval-Augmented Generation (RAG), and vector search. It analyzes candidate resumes, calculates personalized internship matches, generates role recommendations, and assists with interview preparation.

---

## 🔗 Live Links

- **GitHub Repository**: [AI-Career-Companion-Agent](https://github.com/Aswini005/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation)
- **GitHub Pages Frontend**: [Live Frontend Demo](https://aswini005.github.io/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation/)
- **Render Application & API**: [Render Hosted App](https://ai-career-companion-agent-for-internship-6p0w.onrender.com/)
- **Interactive Swagger Docs**: [FastAPI OpenAPI Docs](https://ai-career-companion-agent-for-internship-6p0w.onrender.com/docs)

---

## 🌟 Key Features

- **👤 User Authentication & Profile Management**: Secure JWT authentication with user registration, login, and profile tracking.
- **📄 Smart Resume Parsing**: Extracts skills, experience, education, and contact details from PDF and DOCX resumes.
- **🔍 Vector-Based RAG Internship Matching**: Embeds candidate profiles using Sentence Transformers and matches them against internship databases using FAISS vector search.
- **🤖 AI Career Agent**: Provides personalized career path advice, interview questions, preparation tips, and tailored application strategies.
- **🎨 Modern React Dashboard**: Sleek, intuitive frontend interface built with React, Vite, and modern styling.
- **⚡ FastAPI Backend**: Asynchronous RESTful API backend equipped with auto-generated Interactive OpenAPI / Swagger documentation.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Python 3.12, FastAPI, Uvicorn
- **Database**: PostgreSQL / SQLite, SQLAlchemy ORM
- **Authentication**: PyJWT, Passlib (Bcrypt hashing)
- **AI / ML & RAG**: Sentence Transformers (`all-MiniLM-L6-v2`), FAISS (`faiss-cpu`), PyMuPDF, `python-docx`

### Frontend
- **Framework**: React 18, Vite, React Router DOM (HashRouter)
- **HTTP Client**: Axios
- **Styling**: Modern CSS3 (Glassmorphism & Dark Mode components)

---

## 📂 Project Architecture

```text
AI-Career-Companion/
├── ai-career-companion/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI application entrypoint
│   │   │   ├── models.py             # SQLAlchemy DB schemas
│   │   │   ├── resume_parser.py      # PDF/DOCX parsing logic
│   │   │   ├── rag.py                # FAISS vector indexing & embeddings
│   │   │   ├── ai_agent.py           # AI Career Agent recommendations
│   │   │   └── routes/               # API Endpoint routes (Auth, Resume, Matches, Career)
│   │   ├── data/                     # Internship data CSVs
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/                      # React Components & App UI
│   │   └── package.json
│   └── run_app.py                    # Unified single-command launcher
├── .gitignore                        # Git exclusion rules
├── DOCUMENTATION.md                  # Comprehensive Project Documentation
└── README.md                         # Project README
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL (Optional; falls back to SQLite)

---

### 1. Database Setup
Create a PostgreSQL database named `ai_career_companion`:
```sql
CREATE DATABASE ai_career_companion;
```

---

### 2. Backend Setup
Navigate to the backend directory and set up a virtual environment:

```powershell
cd ai-career-companion/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `ai-career-companion/backend/`:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/ai_career_companion
SECRET_KEY=supersecretjwtkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Start the backend server:
```powershell
uvicorn app.main:app --reload
```
- Backend API will run at: `http://localhost:8000`
- Interactive Swagger Docs available at: `http://localhost:8000/docs`

---

### 3. Frontend Setup
In a new terminal, navigate to the frontend directory:

```powershell
cd ai-career-companion/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- Frontend application will run at: `http://localhost:5173`

---

### ⚡ Unified One-Command Launch
You can launch both backend and frontend servers simultaneously using the runner script from the project root:

```powershell
python ai-career-companion/run_app.py
```

---

## 📖 Key API Routes

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new candidate account |
| `POST` | `/api/auth/login` | Authenticate user and receive JWT token |
| `POST` | `/api/resume/upload` | Upload & parse PDF/DOCX resume |
| `POST` | `/api/internships/match` | Perform RAG vector matching for internships |
| `POST` | `/api/career/recommend-roles` | Get AI role recommendations based on resume |
| `POST` | `/api/career/interview-prep` | Generate customized interview questions |

---

## 📜 License
Distributed under the MIT License. See [LICENSE](LICENSE) for details.

