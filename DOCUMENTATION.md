# AI Career Companion Agent - Project Documentation

## Executive Overview
**AI Career Companion Agent** is an end-to-end web application combining a modern **React (Vite)** frontend with a robust **FastAPI (Python)** backend. It provides automated resume analysis, intelligent internship matching powered by semantic vector search, custom career path recommendations, AI-assisted interview preparation, and RAG-driven document Q&A.

---

## Architecture Overview

```text
                          ┌──────────────────────────┐
                          │   React (Vite) Frontend   │
                          │   (Tailwind, HashRouter) │
                          └─────────────┬────────────┘
                                        │ REST API (JWT Header)
                                        ▼
                          ┌──────────────────────────┐
                          │     FastAPI Backend      │
                          └──────┬─────────────┬─────┘
                                 │             │
                    ┌────────────┴──┐       ┌──┴───────────────┐
                    │  SQLAlchemy   │       │   RAG Engine     │
                    │  (PostgreSQL/ │       │ (SentenceTrans-  │
                    │   SQLite)     │       │  formers + FAISS)│
                    └───────────────┘       └──────────────────┘
```

### System Stack
- **Frontend**: React 18, Vite, React Router DOM (HashRouter), Tailwind CSS, Lucide Icons, Axios
- **Backend Framework**: FastAPI, Uvicorn, Pydantic v2
- **Database / ORM**: PostgreSQL / SQLite with SQLAlchemy
- **Vector Search / RAG**: `sentence-transformers` (`all-MiniLM-L6-v2`), FAISS (`faiss-cpu`), PyPDF / python-docx
- **Authentication**: OAuth2 Password Flow, JWT (HS256), Passlib (Bcrypt)
- **Deployment**: Render (FastAPI + Backend API), GitHub Pages (Static Frontend via Actions)

---

## Directory Structure

```text
ai-career-companion/
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry point, middleware, static frontend mount
│   │   ├── config.py           # Pydantic BaseSettings environment configurations
│   │   ├── database.py         # SQLAlchemy engine setup and DB sessions
│   │   ├── models.py           # DB models (User, Profile, Resume, Internship, etc.)
│   │   ├── schemas.py          # Request / Response validation schemas
│   │   ├── security.py         # JWT tokens & password hash utilities
│   │   ├── rag.py              # Embedding generation, FAISS indexing & semantic search
│   │   ├── resume_parser.py    # Rule-based PDF and DOCX text & skill parsing
│   │   └── routes/             # Modular API Route Handlers
│   │       ├── auth.py         # Registration, Login, Token validation
│   │       ├── profile.py      # Profile management
│   │       ├── resume.py       # Resume file upload, parsing, and listing
│   │       ├── internships.py  # Seeding, searching, and vector matching
│   │       ├── career.py       # Career recommendations & interview prep generator
│   │       └── documents.py    # Document parsing and RAG Q&A
│   ├── data/
│   │   └── internships.csv     # Seed dataset for internships
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # Reusable UI Components (Navbar, ProtectedRoute, etc.)
│   │   ├── pages/              # View pages (Login, Dashboard, Resume, Internships, etc.)
│   │   ├── context/            # React Contexts (AuthContext)
│   │   ├── services/           # Axios API client setup
│   │   ├── App.jsx             # Main Application Routing
│   │   └── main.jsx            # Application entry point
│   ├── package.json          # Frontend Node dependencies
│   └── vite.config.js        # Vite config & base path settings
├── .github/workflows/
│   └── deploy-pages.yml      # CI/CD workflow for GitHub Pages static deployment
├── run_app.py               # Local single-command runner script
└── package.json             # Root monorepo management scripts
```

---

## Core Features & Workflow

### 1. Authentication & Security
- User registration, login, and token refresh using JSON Web Tokens (JWT).
- Secure password hashing using Bcrypt algorithm.
- Protected frontend routes and API dependencies.

### 2. Resume Parsing & Extraction
- Supports `.pdf` and `.docx` format parsing.
- Extracts structured details including email, phone, location, skills, education, and work experience using heuristic rule-based pattern matching.

### 3. Vector Matching & Internship Recommendation
- Pre-loaded or user-seeded dataset of internships.
- Converts resume text and job descriptions into vector embeddings using `all-MiniLM-L6-v2`.
- Computes high-performance similarity scores using **FAISS** vector search.

### 4. Career Guidance & AI Agent Features
- Skill gap analysis based on target career paths.
- Generates structured, step-by-step interview preparation roadmaps.
- **RAG Q&A System**: Upload custom PDF/DOCX domain documents and perform semantic queries directly against document chunks.

---

## Database Models & Schema

```text
  ┌──────────────┐          ┌────────────────┐
  │     USER     │1───────0..1│  USER_PROFILE  │
  └──────┬───────┘          └────────────────┘
         │
         ├───0..* ┌──────────┐
         │        │  RESUME  │
         │        └──────────┘
         │
         └───0..* ┌──────────┐
                  │ DOCUMENT │
                  └──────────┘
```

---

## API Reference Summary

| Group | Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- | :---: |
| **Auth** | `POST` | `/api/auth/register` | Create a new user account | No |
| **Auth** | `POST` | `/api/auth/login` | Login and retrieve JWT access token | No |
| **Profile** | `GET` | `/api/profile/` | Fetch current user profile | Yes |
| **Profile** | `PUT` | `/api/profile/` | Update user profile details | Yes |
| **Resume** | `POST` | `/api/resume/upload` | Upload & parse a PDF/DOCX resume | Yes |
| **Resume** | `GET` | `/api/resume/` | List user uploaded resumes | Yes |
| **Internships**| `POST` | `/api/internships/seed` | Seed default internship data | Yes |
| **Internships**| `GET` | `/api/internships/` | List available internships | Yes |
| **Internships**| `POST` | `/api/internships/match` | Perform FAISS vector match against resume | Yes |
| **Career** | `POST` | `/api/career/recommend` | Get recommendations & gap analysis | Yes |
| **Career** | `POST` | `/api/career/prep-plan` | Generate interview preparation roadmap | Yes |
| **Documents** | `POST` | `/api/documents/upload` | Upload document for RAG indexing | Yes |
| **Documents** | `POST` | `/api/documents/query` | Perform vector search query on document | Yes |

---

## Deployment & Execution Guide

### Local Development Setup

#### Prerequisites
- Node.js 20+
- Python 3.12+
- PostgreSQL (Optional, fallback to SQLite)

#### Running Backend & Frontend Together
From the root workspace directory:

```powershell
npm install
npm run dev
```
- Frontend will be hosted on: `http://localhost:5173`
- Backend API docs available on: `http://localhost:8000/docs`

---

## Key Live Links

- **Frontend Live URL (GitHub Pages)**: [Live Demo](https://aswini005.github.io/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation/)
- **Backend API & Swagger (Render)**: [FastAPI Docs](https://ai-career-companion-agent-for-internship-6p0w.onrender.com/docs)
- **Source Code Repository**: [GitHub Repo](https://github.com/Aswini005/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation)
