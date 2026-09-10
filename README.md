# AI Career Companion Agent

AI Career Companion is a React and FastAPI application for resume analysis, internship matching, career recommendations, interview preparation, and document question answering.

## Live Links

- GitHub repository: https://github.com/Aswini005/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation
- GitHub Pages frontend: https://aswini005.github.io/AI-Career-Companion-Agent-for-Internship-Matching-and-Interview-Preparation/
- Render application and API: https://ai-career-companion-agent-for-internship-6p0w.onrender.com/
- Swagger API documentation: https://ai-career-companion-agent-for-internship-6p0w.onrender.com/docs

The GitHub Pages site hosts the React frontend. The Render service hosts the FastAPI backend and also serves the production frontend when its assets are built there.

## Features

- JWT registration, login, password reset, and protected API requests
- User profile management
- PDF and DOCX resume upload and rule-based extraction
- Resume data storage with SQLAlchemy
- Internship dataset seeding and matching
- Sentence Transformer embeddings and FAISS similarity search
- Career role recommendations and interview preparation plans
- Document upload and question answering
- Optional OpenAI-powered explanations
- Swagger/OpenAPI documentation

## Project Structure

```text
backend/
	app/
		main.py             FastAPI application and static frontend serving
		config.py           Environment-backed settings
		database.py         SQLAlchemy engine and sessions
		models.py           Database models
		schemas.py          Request and response schemas
		security.py         Password hashing and JWT helpers
		rag.py              Embedding, FAISS indexing, and matching
		resume_parser.py    PDF/DOCX parsing
		routes/             Auth, profile, resume, internship, career, and document APIs
	data/internships.csv  Internship seed data
	requirements.txt      Python dependencies
frontend/
	src/                  React application source
	package.json          Frontend dependencies and scripts
	vite.config.js        Vite and GitHub Pages configuration
.github/workflows/
	deploy-pages.yml      GitHub Pages build and deployment workflow
run_app.py               Unified local runner
package.json             Root development and production scripts
```

## Prerequisites

- Python 3.12 or newer
- Node.js 20 or newer
- PostgreSQL for a persistent local database, or SQLite for a simple demo
- Git

## Local Setup

From the project root:

```powershell
cd D:\AI-Career-Companion\AI-Career-Companion\ai-career-companion
npm install
```

Create and activate the backend environment:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` with values such as:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/ai_career_companion
JWT_SECRET=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_MINUTES=60
FRONTEND_ORIGIN=http://localhost:5173
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

Create the PostgreSQL database if needed:

```sql
CREATE DATABASE ai_career_companion;
```

## Run Locally

Run backend and frontend together from the project root:

```powershell
npm run dev
```

Open the frontend at http://localhost:5173.

Other root commands:

```powershell
npm run build          # Build frontend assets
npm start              # Build frontend, then run FastAPI
npm run start:backend  # Run only the backend
```

Manual startup commands:

```powershell
# Terminal 1
cd backend
..\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm run dev
```

The local API documentation is available at http://localhost:8000/docs.

## Main API Flow

Use Swagger or an API client for this workflow:

1. Register with `POST /api/auth/register`.
2. Login with `POST /api/auth/login`.
3. Copy the returned JWT and use the Swagger **Authorize** button.
4. Seed internships with `POST /api/internships/seed`.
5. Upload a PDF or DOCX resume with `POST /api/resume/upload`.
6. Match the resume with `POST /api/internships/match`.
7. Use career recommendations, interview preparation, and document endpoints as needed.

Health check:

```text
GET /health
```

## GitHub Pages Deployment

The workflow in `.github/workflows/deploy-pages.yml` runs when changes are pushed to `main`:

```powershell
git add .
git commit -m "Describe the change"
git push origin main
```

The workflow installs frontend dependencies, builds `frontend/dist`, and deploys it to GitHub Pages. Vite uses the repository subpath only in the Pages workflow. Hash routing keeps frontend navigation compatible with Pages refreshes.

In the GitHub repository, enable Pages under **Settings -> Pages** and select **GitHub Actions** as the source if it is not already enabled.

## Render Deployment

Render should use a Web Service connected to the `main` branch.

Build command:

```bash
pip install -r backend/requirements.txt && cd frontend && npm install && node node_modules/vite/bin/vite.js build
```

Start command:

```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
DATABASE_URL=sqlite:///./backend/app.db
JWT_SECRET=your-long-random-secret
```

For production data persistence, use a managed PostgreSQL database instead of SQLite. The free Render instance can take time to wake and has limited memory. Heavy RAG libraries are imported lazily, but embedding and FAISS operations can still require additional memory.

## Troubleshooting

### Git push says `src refspec main does not match any`

Check the current branch and push the branch that exists:

```powershell
git branch --show-current
git push -u origin main
```

### GitHub Pages shows the README

The repository root is documentation. Open the GitHub Pages URL to view the frontend, and check the Actions tab for the `Deploy frontend to GitHub Pages` workflow.

### Render shows a loading page or 503

Check the latest deploy logs. Confirm the build command, start command, and `DATABASE_URL` and `JWT_SECRET` variables. Free instances may also need time to wake up.

### Frontend asset MIME error

The Render build must use `/` as the Vite base path. The GitHub Pages workflow sets the repository subpath separately through `VITE_BASE_PATH`.

### First matching request is slow

The first embedding operation may download the Sentence Transformer model and build the FAISS index. Later requests are faster when the instance and generated files remain available.

## Security Notes

- Never commit `.env`, passwords, API keys, or JWT secrets.
- Replace demo reset-token behavior with an email delivery service in production.
- Use PostgreSQL and persistent storage for production data.
- Review CORS settings before exposing the API publicly.
- Uploaded files and generated vector data should use persistent, access-controlled storage in production.

