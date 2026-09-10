from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Resume
from app.security import get_current_user, get_current_user_optional
from app.schemas import (
    RoleRecommendRequest,
    InterviewPrepRequest,
    SkillAnalysisRequest,
    CoverLetterRequest,
    InternshipAssistantRequest
)
from app.ai_agent import recommend_roles, generate_interview_prep, chat_mock_interview

router = APIRouter()

def get_candidate_data(resume_id: int | None, user: User | None, db: Session, fallback_data: dict = None) -> dict:
    if resume_id:
        resume = db.get(Resume, resume_id)
        if resume:
            return resume.extracted_data
    if user:
        latest_resume = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).first()
        if latest_resume:
            return latest_resume.extracted_data
    latest_any = db.query(Resume).order_by(Resume.created_at.desc()).first()
    if latest_any:
        return latest_any.extracted_data
    if fallback_data:
        return fallback_data
    return {
        "full_name": user.profile.full_name if (user and user.profile) else "Candidate",
        "skills": ["Python", "FastAPI", "SQL", "React", "Docker", "Git"],
        "technical_skills": ["REST API", "Database Design", "System Architecture"],
        "education": "B.Tech Computer Science",
        "work_experience": "Software Engineering Projects",
        "projects": "AI Career Companion Workspace"
    }

@router.post("/recommend-roles")
def get_role_recommendations(
    req: RoleRecommendRequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cand_data = get_candidate_data(req.resume_id, user, db, req.extracted_data)
    recommendation_res = recommend_roles(cand_data)
    return recommendation_res

@router.post("/interview-prep")
def get_interview_prep(
    req: InterviewPrepRequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cand_data = get_candidate_data(req.resume_id, user, db)
    prep_res = generate_interview_prep(
        role_title=req.role_title,
        resume_data=cand_data,
        company_name=req.company_name or "Target Tech Company"
    )
    return prep_res

@router.post("/skill-analysis")
def get_skill_analysis(
    req: SkillAnalysisRequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cand_data = get_candidate_data(req.resume_id, user, db)
    cand_skills = cand_data.get("skills", []) + cand_data.get("technical_skills", [])
    if not cand_skills:
        cand_skills = ["Python", "SQL", "Git", "Problem Solving"]
    
    role = req.target_role or "Software Engineer"
    
    # Generic requirements for analysis
    target_skills = ["Python", "REST API", "SQL", "Docker", "System Design", "Git", "Testing"]
    matched = [s for s in target_skills if any(s.lower() in cs.lower() for cs in cand_skills)]
    missing = [s for s in target_skills if s not in matched]
    
    score = int((len(matched) / len(target_skills)) * 100)
    
    return {
        "target_role": role,
        "match_score": max(65, score),
        "candidate_skills": cand_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendation": f"Focus on acquiring proficiency in {', '.join(missing[:3])} to maximize compatibility for {role} roles."
    }

@router.post("/cover-letter")
def generate_cover_letter_api(
    req: CoverLetterRequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cand_data = get_candidate_data(req.resume_id, user, db)
    name = cand_data.get("full_name") or (user.profile.full_name if (user and user.profile) else "Applicant")
    email = user.email if user else "aswini@gmail.com"
    skills = cand_data.get("skills", ["Python", "SQL", "React"])
    skills_str = ", ".join(skills[:5])
    education = cand_data.get("education") or "Computer Science"
    
    letter = f"""Dear Hiring Manager at {req.company_name},

I am writing to express my strong interest in the {req.job_title} role at {req.company_name}. With an academic background in {education} and hands-on technical proficiency in {skills_str}, I am confident in my ability to make an immediate impact on your team.

Throughout my practical projects, I have developed expertise in building scalable applications, writing efficient code, and collaborating on software solutions. I am particularly drawn to {req.company_name}'s focus on innovation and product excellence.

Thank you for considering my application. I welcome the opportunity to discuss how my technical skills and enthusiasm align with your team's current goals.

Sincerely,
{name}
{email}"""

    return {
        "job_title": req.job_title,
        "company_name": req.company_name,
        "cover_letter": letter
    }



@router.post("/internship-assistant", summary="Internship Assistant Chat")
def internship_assistant_chat(
    req: InternshipAssistantRequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cand_data = get_candidate_data(None, user, db) if user else {
        "full_name": "Candidate",
        "skills": ["Python", "FastAPI", "SQL", "React", "Docker", "Git"],
        "technical_skills": ["REST API", "Database Design", "System Architecture"]
    }
    res = chat_mock_interview(
        role_title=req.role_title or "General Career Assistant",
        user_message=req.user_message,
        chat_history=req.chat_history,
        resume_data=cand_data
    )
    return res



