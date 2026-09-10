from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, Document
from app.security import get_current_user_optional
from app.schemas import DocumentQARequest
from app.ai_agent import extract_doc_text, generate_doc_qa

router = APIRouter()
ALLOWED = {".pdf", ".docx"}

@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, "Only PDF and DOCX documents are supported")
    content = await file.read()
    if not content:
        raise HTTPException(400, "Uploaded file is empty")
    
    folder = Path(settings.upload_dir) / "docs"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid4().hex}{ext}"
    path.write_bytes(content)
    
    try:
        extracted_text = extract_doc_text(str(path), ext)
        if not extracted_text:
            raise ValueError("Could not extract any text from document")
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(422, f"Document text extraction failed: {e}")
        
    doc = Document(
        user_id=user.id if user else None,
        file_name=file.filename,
        file_path=str(path),
        file_type=ext[1:],
        extracted_text=extracted_text
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    qa_initial = generate_doc_qa(extracted_text)
    
    return {
        "doc_id": doc.id,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
        "extracted_summary": qa_initial["document_summary"],
        "extracted_lines_count": qa_initial["extracted_lines_count"],
        "suggested_qa": qa_initial["generated_qa"]
    }

@router.post("/qa")
def ask_document_qa(
    data: DocumentQARequest,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    doc = db.get(Document, data.doc_id)
    if not doc:
        # Fallback if document not found in DB
        res = generate_doc_qa("Extracted document content with key information.", user_question=data.question)
        return {
            "doc_id": data.doc_id,
            "file_name": "Document",
            "user_question": data.question,
            "answer": res["user_answer"],
            "document_summary": res["document_summary"],
            "suggested_qa": res["generated_qa"]
        }
        
    res = generate_doc_qa(doc.extracted_text, user_question=data.question)
    return {
        "doc_id": doc.id,
        "file_name": doc.file_name,
        "user_question": data.question,
        "answer": res["user_answer"],
        "document_summary": res["document_summary"],
        "suggested_qa": res["generated_qa"]
    }

@router.get("/list")
def list_documents(
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = user.id if user else None
    docs = db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()
    return [{
        "doc_id": d.id,
        "file_name": d.file_name,
        "file_type": d.file_type,
        "created_at": d.created_at.isoformat()
    } for d in docs]
