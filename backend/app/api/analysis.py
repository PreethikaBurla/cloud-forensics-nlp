from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import hashlib

from backend.app.db.session import SessionLocal
from backend.app.core.models import Case, Evidence, CustodyLog
from backend.app.preprocessing.normalize import parse_and_normalize_json
from backend.app.nlp.extractor import process_events_nlp
from backend.app.scoring.risk import calculate_risk_scores
from backend.app.xai.explanation_builder import generate_explanations

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{case_id}/analyze")
def run_analysis_pipeline(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    evidences = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    if not evidences:
        raise HTTPException(status_code=404, detail="No evidence found for this case")
    
    # Phase 1: Integrity Check & Normalization
    for evidence in evidences:
        sha256_hash = hashlib.sha256()
        with open(evidence.storage_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                
        current_hash = sha256_hash.hexdigest()
        if current_hash != evidence.sha256:
            raise HTTPException(status_code=400, detail=f"TAMPER ALERT: {evidence.filename} hash mismatch!")
        
    # Phase 2: NLP Entity & Feature Extraction
    process_events_nlp(db, case_id)
    
    # Phase 3: Machine Learning & Risk Scoring
    calculate_risk_scores(db, case_id)
    
    # Phase 4: XAI Plain-English Explanations
    explanations_count = generate_explanations(db, case_id)

    return {
        "message": "Pipeline Phase 4 Complete: XAI Explanations Generated", 
        "explanations_created": explanations_count
    }