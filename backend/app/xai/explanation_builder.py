import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from lime.lime_tabular import LimeTabularExplainer
from sqlalchemy.orm import Session
from backend.app.core.models import Event, Score, Explanation

def generate_explanations(db: Session, case_id: int):
    # 1. Fetch events and their AI risk scores
    events = db.query(Event).filter(Event.case_id == case_id).order_by(Event.id).all()
    scores = db.query(Score).join(Event).filter(Event.case_id == case_id).order_by(Event.id).all()
    
    if not events or not scores:
        return 0
        
    feature_names = ['keyword_count', 'entity_count', 'is_sensitive_file', 'is_unknown_ip']
    X_data, y_data = [], []
    event_map = {}
    
    for event, score in zip(events, scores):
        feats = json.loads(event.features) if event.features else {}
        row = [
            feats.get("keyword_count", 0),
            feats.get("entity_count", 0),
            feats.get("is_sensitive_file", 0),
            feats.get("is_unknown_ip", 0)
        ]
        X_data.append(row)
        # Class 1 for Suspicious (High/Medium), Class 0 for Normal (Low)
        y_data.append(1 if score.level in ["High", "Medium"] else 0)
        event_map[event.id] = {"row": row, "level": score.level}
        
    X = np.array(X_data)
    y = np.array(y_data)
    
    # 2. Train a surrogate Random Forest model for LIME to explain
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    if len(set(y)) > 1:
        clf.fit(X, y)
    else:
        return 0 # Skip if there are no suspicious events to explain
        
    # 3. Initialize the LIME Explainer
    explainer = LimeTabularExplainer(
        training_data=X,
        feature_names=feature_names,
        class_names=['Normal', 'Suspicious'],
        mode='classification'
    )
    
    explanations_created = 0
    for event_id, data in event_map.items():
        # Skip if already explained
        if db.query(Explanation).filter(Explanation.event_id == event_id).first():
            continue
            
        # Low risk events get a short, standard summary to save processing time
        if data["level"] == "Low":
            plain_text = "This event exhibits normal behavior patterns with no significant risk indicators."
            exp = Explanation(event_id=event_id, method="Rule-based", feature_weights="{}", plain_text=plain_text)
            db.add(exp)
            explanations_created += 1
            continue
            
        # 4. Explain High/Medium events using LIME
        lime_exp = explainer.explain_instance(np.array(data["row"]), clf.predict_proba, num_features=3)
        weights = lime_exp.as_list()
            
        # 5. Build the Plain-English Court Sentence
        reasons = []
        for feature, weight in weights:
            if weight > 0: # Only look at features that pushed the score higher
                if "keyword_count" in feature: reasons.append("suspicious keywords were detected")
                if "is_unknown_ip" in feature: reasons.append("the action originated from an unrecognized IP address")
                if "is_sensitive_file" in feature: reasons.append("it involved a confidential file")
                if "entity_count" in feature: reasons.append("multiple sensitive entities were accessed")
        
        reason_str = " and ".join(reasons) if reasons else "anomalous access patterns were detected"
        plain_text = f"This event was ranked {data['level'].upper()} mainly because {reason_str}."
        
        weight_dict = {f[0]: f[1] for f in weights}
        
        # Save to database
        exp = Explanation(
            event_id=event_id,
            method="LIME",
            feature_weights=json.dumps(weight_dict),
            plain_text=plain_text
        )
        db.add(exp)
        explanations_created += 1
        
    db.commit()
    return explanations_created