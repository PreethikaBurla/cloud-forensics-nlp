from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from backend.app.db.session import SessionLocal
from backend.app.core.models import Case, Event, Score, Explanation

router = APIRouter()

# Point to the templates folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/{case_id}")
def view_dashboard(request: Request, case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    events = db.query(Event).filter(Event.case_id == case_id).order_by(Event.id).all()
    
    timeline = []
    high_count = medium_count = low_count = 0
    
    for event in events:
        score = db.query(Score).filter(Score.event_id == event.id).first()
        explanation = db.query(Explanation).filter(Explanation.event_id == event.id).first()
        
        if score:
            if score.level == "High": high_count += 1
            elif score.level == "Medium": medium_count += 1
            else: low_count += 1
            
        timeline.append({
            "event": event,
            "score": score,
            "explanation": explanation
        })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "case": case,
            "timeline": timeline,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count
        }
    )   