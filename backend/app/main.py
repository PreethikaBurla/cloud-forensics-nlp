from fastapi import FastAPI
from backend.app.api import auth, cases, analysis, dashboard, reports

app = FastAPI(title="Cloud Forensics XAI API")

# Register all endpoints
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cases.router, prefix="/cases", tags=["cases"])
app.include_router(analysis.router, prefix="/cases", tags=["analysis"])
app.include_router(reports.router, prefix="/cases", tags=["reports"])
app.include_router(dashboard.router, tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI! The Cloud Forensics XAI system is running."}