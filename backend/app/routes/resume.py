from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, Resume
from app.security import get_current_user_optional
from app.resume_parser import extract_text, parse_resume

router = APIRouter()
ALLOWED = {".pdf", ".docx"}

@router.post("/upload", status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, "Only PDF and DOCX resumes are supported")
    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty")
    folder = Path(settings.upload_dir)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid4().hex}{ext}"
    path.write_bytes(content)
    try:
        text = extract_text(str(path), ext)
        if not text.strip():
            raise ValueError("No text could be extracted from the resume")
        data = parse_resume(text)
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(422, f"Resume parsing failed: {e}")
    user_id = user.id if user else None
    if not user_id:
        default_user = db.query(User).first()
        if default_user:
            user_id = default_user.id
        else:
            from app.security import hash_password
            default_user = User(email="aswini@gmail.com", password_hash=hash_password("password123"))
            db.add(default_user); db.commit(); db.refresh(default_user)
            user_id = default_user.id

    resume = Resume(user_id=user_id, file_name=file.filename, file_path=str(path), file_type=ext[1:], extracted_data=data)
    db.add(resume); db.commit(); db.refresh(resume)
    return {"resume_id": resume.id, "file_name": resume.file_name, "extracted_data": data}

@router.get("/{resume_id}")
def get_resume(resume_id: int, user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(404, "Resume not found")
    return {"resume_id": resume.id, "file_name": resume.file_name, "extracted_data": resume.extracted_data}
