import spacy
import re
import json
from sqlalchemy.orm import Session
from backend.app.core.models import Event

# Load the spaCy English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

SUSPICIOUS_KEYWORDS = ["delete", "mass delete", "failed login", "unknown device", "confidential", "wipe", "download all", "ransom"]

def process_events_nlp(db: Session, case_id: int):
    events = db.query(Event).filter(Event.case_id == case_id).all()
    
    for event in events:
        text = event.raw_text
        doc = nlp(text)
        
        # 1. Extract Entities using spaCy NER and Regex
        entities = {"persons": [], "ips": [], "dates": [], "files": []}
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ in ["DATE", "TIME"]:
                entities["dates"].append(ent.text)
                
        # Regex for IP addresses and basic file extensions
        entities["ips"] = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
        entities["files"] = re.findall(r'[\w\-]+\.(?:pdf|zip|txt|csv|docx)', text.lower())
        
        # 2. Keyword Detection
        found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in text.lower()]
        
        # 3. Build the Feature Vector for the XAI Engine
        features = {
            "keyword_count": len(found_keywords),
            "entity_count": len(entities["persons"]) + len(entities["ips"]) + len(entities["files"]),
            "is_sensitive_file": 1 if "confidential" in text.lower() else 0,
            "is_unknown_ip": 1 if "unknown" in event.location.lower() else 0
        }
        
        # Update the SQLite database record permanently
        event.entities = json.dumps(entities)
        event.features = json.dumps(features)
    
    db.commit()
    return len(events)