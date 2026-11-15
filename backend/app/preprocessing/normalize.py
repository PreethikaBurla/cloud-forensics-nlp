import json
from sqlalchemy.orm import Session
from backend.app.core.models import Event, Evidence

def parse_and_normalize_json(db: Session, evidence: Evidence):
    # Read the read-only evidence file
    with open(evidence.storage_path, 'r') as f:
        data = json.load(f)
    
    normalized_events = []
    for item in data:
        # Map the incoming data to the standard forensic schema
        event = Event(
            case_id=evidence.case_id,
            evidence_id=evidence.id,
            timestamp_utc=item.get("timestamp_utc"),
            source=item.get("source", "unknown"),
            user=item.get("user", "unknown"),
            action=item.get("action", "unknown"),
            resource=item.get("resource", "unknown"),
            ip=item.get("ip", "unknown"),
            location=item.get("location", "unknown"),
            raw_text=item.get("raw_text", "")
        )
        db.add(event)
        normalized_events.append(event)
    
    db.commit()
    return len(normalized_events)