from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

class ProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = None
    address: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None

class ProfileResponse(ProfileRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int

class MatchRequest(BaseModel):
    resume_id: int
    top_k: int = Field(default=5, ge=1, le=20)
    explain: bool = True

class RoleRecommendRequest(BaseModel):
    resume_id: int | None = None
    extracted_data: dict | None = None

class InterviewPrepRequest(BaseModel):
    role_title: str
    resume_id: int | None = None
    company_name: str | None = "Target Tech Company"

class DocumentQARequest(BaseModel):
    doc_id: int
    question: str | None = None

class SkillAnalysisRequest(BaseModel):
    resume_id: int | None = None
    target_role: str | None = "Software Engineer"
    job_description: str | None = None

class CoverLetterRequest(BaseModel):
    resume_id: int | None = None
    job_title: str
    company_name: str
    job_description: str | None = None

class InternshipAssistantRequest(BaseModel):
    role_title: str | None = "Software Engineering Intern"
    user_message: str
    chat_history: list | None = None




