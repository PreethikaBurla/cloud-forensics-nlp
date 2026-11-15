from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from backend.app.db.session import SessionLocal
from backend.app.core.models import Case
from backend.app.reports.pdf_builder import generate_pdf_report

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{case_id}/report")
def create_report(case_id: int, db: Session = Depends(get_db)):
    pdf_path = generate_pdf_report(db, case_id)
    if not pdf_path:
        raise HTTPException(status_code=404, detail="Case not found")
        
    return {"message": "PDF Report generated successfully", "path": pdf_path}

@router.get("/{case_id}/report/download")
def download_report(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports_out"))
    pdf_path = os.path.join(reports_dir, f"Report_{case.case_number}.pdf")
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not generated yet. Call POST /report first.")
        
    return FileResponse(pdf_path, filename=f"Report_{case.case_number}.pdf", media_type="application/pdf")