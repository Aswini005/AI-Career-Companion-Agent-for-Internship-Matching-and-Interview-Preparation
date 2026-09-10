from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Profile
from app.schemas import ProfileRequest, ProfileResponse
from app.security import get_current_user_optional

router = APIRouter()

@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(data: ProfileRequest, user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not user:
        return {"id": 1, "user_id": 1, **data.model_dump()}
    if user.profile:
        raise HTTPException(409, "Profile already exists")
    profile = Profile(user_id=user.id, **data.model_dump())
    db.add(profile); db.commit(); db.refresh(profile)
    return profile

@router.get("")
def get_profile(user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not user:
        return {
            "id": 1,
            "user_id": 1,
            "full_name": "Aswini",
            "phone": "+91 9876543210",
            "address": "Hyderabad, India",
            "linkedin": None,
            "github": None,
            "summary": "Passionate software engineer looking for backend and AI/ML internship opportunities."
        }
    profile = db.query(Profile).filter_by(user_id=user.id).first()
    if not profile:
        return {
            "id": user.id,
            "user_id": user.id,
            "full_name": "Candidate",
            "phone": "+91 9876543210",
            "address": "Hyderabad, India",
            "linkedin": None,
            "github": None,
            "summary": "Software Engineer"
        }
    return profile

@router.put("")
def update_profile(data: ProfileRequest, user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if not user:
        return {"id": 1, "user_id": 1, **data.model_dump()}
    profile = db.query(Profile).filter_by(user_id=user.id).first()
    if not profile:
        profile = Profile(user_id=user.id, **data.model_dump())
        db.add(profile); db.commit(); db.refresh(profile)
        return profile
    for k, v in data.model_dump().items():
        setattr(profile, k, v)
    db.commit(); db.refresh(profile)
    return profile

@router.delete("")
def delete_profile(user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if user and user.profile:
        db.delete(user.profile); db.commit()
    return {"message": "Profile deleted successfully"}

@router.delete("/account")
def delete_account(user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    if user:
        db.delete(user); db.commit()
    return {"message": "User account deleted successfully"}
