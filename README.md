# AI Career Companion Agent

Complete starter implementation for:
- FastAPI REST APIs
- JWT authentication
- PostgreSQL + SQLAlchemy
- User profile management
- PDF/DOCX resume parsing
- Resume data storage
- Sentence Transformer embeddings
- FAISS vector search
- RAG internship matching
- Optional LLM explanations
- React + Vite demonstration frontend
- Swagger/OpenAPI

## 1. PostgreSQL

Create a database:

```sql
CREATE DATABASE ai_career_companion;
```

## 2. Backend

```powershell
cd backend
python -m venv venv
.env\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set your PostgreSQL username/password.

Run:

```powershell
uvicorn app.main:app --reload
```

Swagger:
`http://localhost:8000/docs`

## 3. First API calls

Register:
POST `/api/auth/register`

Login:
POST `/api/auth/login`

Copy the returned access token and use Swagger's Authorize button.

Create/load internships:
POST `/api/internships/seed`

Upload:
POST `/api/resume/upload`

Match:
POST `/api/internships/match`

## 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## Important

The forgot-password endpoint returns a reset token only for demonstration. In production, send the token through an email service and never return it directly.

The first embedding/index operation downloads the Sentence Transformer model, so the first RAG request can take longer.

This is a complete assignment starter, but resume section extraction is intentionally rule-based. For production-quality parsing, add a dedicated NLP/LLM extraction layer and stronger validation.
