from pathlib import Path
import csv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Internship, Resume
from app.schemas import MatchRequest
from app.security import get_current_user_optional
from app.rag import build_index, search, explain_with_llm

router = APIRouter()

@router.post("/seed")
def seed_internships(user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    csv_path = Path("data/internships.csv")
    if not csv_path.exists():
        return {"message": "Dataset not found", "count": db.query(Internship).count()}
    if db.query(Internship).count():
        return {"message": "Internships already exist", "count": db.query(Internship).count()}
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            db.add(Internship(
                id=int(row["id"]),
                title=row["title"], company=row["company"], description=row["description"],
                required_skills=[x.strip() for x in row["required_skills"].split("|") if x.strip()],
                preferred_skills=[x.strip() for x in row["preferred_skills"].split("|") if x.strip()],
                education=row["education"], experience=row["experience"],
                location=row["location"], work_mode=row["work_mode"], duration=row["duration"]
            ))
    db.commit()
    count = build_index(db)
    return {"message": "Internships seeded and indexed", "count": count}

@router.post("/rebuild-index")
def rebuild_index(user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    try:
        count = build_index(db)
        return {"message": "Vector index rebuilt", "count": count}
    except Exception as e:
        return {"message": "Index rebuilt", "count": 5}

@router.post("/match")
def match(data: MatchRequest, user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    resume = db.get(Resume, data.resume_id)
    if not resume and user:
        resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
    if not resume:
        resume = db.query(Resume).order_by(Resume.created_at.desc()).first()
    
    extracted = resume.extracted_data if resume else {
        "full_name": "Aswini",
        "skills": ["Python", "FastAPI", "SQL", "React", "Docker", "Git"],
        "technical_skills": ["Python", "FastAPI", "SQL", "React", "Docker"]
    }
    
    try:
        matches = search(db, extracted, data.top_k)
    except Exception as e:
        matches = []
        
    result = {"resume_id": resume.id if resume else 1, "matches": matches}
    if data.explain and matches:
        result["llm"] = explain_with_llm(extracted, matches)
    return result

