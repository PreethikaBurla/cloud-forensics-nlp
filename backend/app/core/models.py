from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # Admin, Investigator, Legal Reviewer

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=func.now())

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    filename = Column(String)
    source = Column(String)
    size = Column(Integer)
    sha256 = Column(String)
    collected_by = Column(Integer, ForeignKey("users.id"))
    collected_at = Column(DateTime)
    storage_path = Column(String)

class CustodyLog(Base):
    __tablename__ = "custody_log"
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    action = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=func.now())
    hash_at_time = Column(String)
    result = Column(String)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    timestamp_utc = Column(String)
    source = Column(String)
    user = Column(String)
    action = Column(String)
    resource = Column(String)
    ip = Column(String)
    location = Column(String)
    raw_text = Column(Text)
    entities = Column(Text) # Stored as JSON string
    features = Column(Text) # Stored as JSON string

class Score(Base):
    __tablename__ = "scores"
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    L = Column(Float)
    C = Column(Float)
    A = Column(Float)
    R = Column(Float)
    level = Column(String) # Low, Medium, High
    model_prob = Column(Float)

class Explanation(Base):
    __tablename__ = "explanations"
    event_id = Column(Integer, ForeignKey("events.id"), primary_key=True)
    method = Column(String) # LIME or SHAP
    feature_weights = Column(Text) # Stored as JSON string
    plain_text = Column(Text)

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    path = Column(String)
    sha256 = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=func.now())