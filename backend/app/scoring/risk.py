import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session
from backend.app.core.models import Event, Score

def calculate_risk_scores(db: Session, case_id: int):
    # 1. Fetch events ordered by time (Timeline Correlation)
    events = db.query(Event).filter(Event.case_id == case_id).order_by(Event.timestamp_utc).all()
    if not events:
        return 0

    # 2. Prepare data for the Isolation Forest Machine Learning model
    feature_list = []
    for event in events:
        feats = json.loads(event.features) if event.features else {}
        feature_list.append({
            "keyword_count": feats.get("keyword_count", 0),
            "entity_count": feats.get("entity_count", 0),
            "is_sensitive_file": feats.get("is_sensitive_file", 0),
            "is_unknown_ip": feats.get("is_unknown_ip", 0)
        })
        
    df = pd.DataFrame(feature_list)
    
    # 3. Train Isolation Forest to find Behavioural Anomalies (A)
    # contamination=0.05 assumes roughly 5% of our logs are the injected attacks
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    X = df[['keyword_count', 'entity_count', 'is_sensitive_file', 'is_unknown_ip']]
    
    # Calculate anomaly score and normalize it between 0 and 1
    decision_scores = iso_forest.fit(X).decision_function(X)
    df['anomaly_score'] = (decision_scores.max() - decision_scores) / (decision_scores.max() - decision_scores.min() + 1e-10)

    # 4. Calculate the Final Risk Score for each event
    for i, event in enumerate(events):
        feats = json.loads(event.features) if event.features else {}
        
        # L - Lexical relevance (0 to 1 based on suspicious NLP keywords found)
        L = min(feats.get("keyword_count", 0) * 0.5, 1.0)
        
        # C - Temporal correlation (Higher if IP is unknown/new for this timeline)
        C = 0.8 if feats.get("is_unknown_ip") else 0.1
        
        # A - Behavioural anomaly (from the Machine Learning model)
        A = float(df.iloc[i]['anomaly_score'])
        
        # Apply the PDF's formula: R = (0.5 * L) + (0.3 * C) + (0.2 * A)
        R = (0.5 * L) + (0.3 * C) + (0.2 * A)
        
        # Rank the evidence
        if R >= 0.66:
            level = "High"
        elif R >= 0.33:
            level = "Medium"
        else:
            level = "Low"
            
        # 5. Save the AI Scores to the database permanently
        existing_score = db.query(Score).filter(Score.event_id == event.id).first()
        if not existing_score:
            new_score = Score(
                event_id=event.id,
                L=float(L), C=float(C), A=float(A), R=float(R),
                level=level, model_prob=float(A)
            )
            db.add(new_score)

    db.commit()
    return len(events)