from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import hashlib
import os
import shutil
from datetime import datetime, timezone

from backend.app.db.session import SessionLocal
from backend.app.core.models import Case, Evidence, CustodyLog

router = APIRouter()

# Directory to store read-only raw evidence
RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "raw"))
os.makedirs(RAW_DATA_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class CaseCreate(BaseModel):
    case_number: str
    title: str
    description: str

@router.post("/")
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    new_case = Case(
        case_number=case.case_number,
        title=case.title,
        description=case.description,
        created_by=1 # Hardcoding user ID 1 for testing
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return {"message": "Case created successfully", "case_id": new_case.id}

@router.post("/{case_id}/evidence")
def upload_evidence(case_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Verify Case Exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # 2. Save Evidence to Read-Only Storage
    file_path = os.path.join(RAW_DATA_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 3. Compute SHA-256 Hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    
    file_size = os.path.getsize(file_path)
    
    # 4. Save Evidence Database Record
    new_evidence = Evidence(
        case_id=case_id,
        filename=file.filename,
        source="Upload",
        size=file_size,
        sha256=file_hash,
        collected_by=1, # Hardcoding user ID 1 for testing
        collected_at=datetime.now(timezone.utc),
        storage_path=file_path
    )
    db.add(new_evidence)
    db.commit()
    db.refresh(new_evidence)
    
    # 5. Write Chain of Custody Entry
    custody_entry = CustodyLog(
        evidence_id=new_evidence.id,
        action="Collected and Hashed",
        user_id=1,
        hash_at_time=file_hash,
        result="Match"
    )
    db.add(custody_entry)
    db.commit()
    
    return {
        "message": "Evidence secured and hashed",
        "evidence_id": new_evidence.id,
        "sha256": file_hash
    }
    