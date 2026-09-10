from pathlib import Path
import json
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Internship

_model = None

def model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def internship_text(x: Internship) -> str:
    return f"""
Title: {x.title}
Company: {x.company}
Description: {x.description}
Required Skills: {', '.join(x.required_skills or [])}
Preferred Skills: {', '.join(x.preferred_skills or [])}
Education: {x.education or ''}
Experience: {x.experience or ''}
Location: {x.location or ''}
Work Mode: {x.work_mode or ''}
Duration: {x.duration or ''}
""".strip()

def candidate_text(data: dict) -> str:
    fields = [
        ("Name", data.get("full_name")),
        ("Summary", data.get("professional_summary")),
        ("Skills", ", ".join(data.get("skills", []))),
        ("Technical Skills", ", ".join(data.get("technical_skills", []))),
        ("Education", data.get("education")),
        ("Experience", data.get("work_experience")),
        ("Projects", data.get("projects")),
        ("Certifications", data.get("certifications")),
        ("Internships", data.get("internships")),
        ("Languages", data.get("languages")),
        ("Achievements", data.get("achievements")),
    ]
    return "\n".join(f"{k}: {v or ''}" for k, v in fields)

def build_index(db: Session):
    import faiss
    import numpy as np

    internships = db.query(Internship).all()
    if not internships:
        raise ValueError("No internships found. Load the internship dataset first.")
    texts = [internship_text(x) for x in internships]
    vectors = model().encode(texts, normalize_embeddings=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(np.asarray(vectors, dtype="float32"))
    Path(settings.vector_dir).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(Path(settings.vector_dir) / "internships.faiss"))
    (Path(settings.vector_dir) / "ids.json").write_text(json.dumps([x.id for x in internships]))
    return len(internships)

def search(db: Session, candidate: dict, top_k: int):
    import faiss
    import numpy as np

    path = Path(settings.vector_dir)
    index_path = path / "internships.faiss"
    ids_path = path / "ids.json"
    if not index_path.exists() or not ids_path.exists():
        build_index(db)
    index = faiss.read_index(str(index_path))
    ids = json.loads(ids_path.read_text())
    vector = model().encode([candidate_text(candidate)], normalize_embeddings=True)
    scores, positions = index.search(np.asarray(vector, dtype="float32"), min(top_k, len(ids)))
    results = []
    for score, pos in zip(scores[0], positions[0]):
        internship = db.get(Internship, ids[int(pos)])
        if internship:
            results.append({
                "internship_id": internship.id,
                "title": internship.title,
                "company": internship.company,
                "description": internship.description,
                "required_skills": internship.required_skills,
                "preferred_skills": internship.preferred_skills,
                "education": internship.education,
                "experience": internship.experience,
                "location": internship.location,
                "work_mode": internship.work_mode,
                "duration": internship.duration,
                "similarity_score": round(float(score), 4)
            })
    return results

def explain_with_llm(candidate: dict, matches: list[dict]):
    if not settings.openai_api_key:
        return {"explanation": "LLM explanation is disabled. Set OPENAI_API_KEY to enable it."}
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = f"""You are an internship matching assistant.
Use ONLY the candidate data and retrieved internships below.
Do not invent companies, titles, skills, requirements, locations, or other facts.
For each internship, explain matching skills, missing skills when explicitly inferable,
and why it is relevant.

Candidate:
{json.dumps(candidate, ensure_ascii=False)}

Retrieved internships:
{json.dumps(matches, ensure_ascii=False)}
"""
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"explanation": response.choices[0].message.content}
