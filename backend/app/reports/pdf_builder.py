import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy.orm import Session

from backend.app.core.models import Case, Evidence, Event, Score, Explanation

def generate_pdf_report(db: Session, case_id: int):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
        
    # Set up the output directory
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports_out"))
    os.makedirs(reports_dir, exist_ok=True)
    
    file_name = f"Report_{case.case_number}.pdf"
    pdf_path = os.path.join(reports_dir, file_name)
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # 1. Cover & Summary
    elements.append(Paragraph(f"Digital Forensics XAI Report", styles['Title']))
    elements.append(Paragraph(f"Case Number: {case.case_number}", styles['Heading2']))
    elements.append(Paragraph(f"Title: {case.title}", styles['Normal']))
    elements.append(Paragraph(f"Generated At: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # 2. Evidence Inventory & Chain of Custody
    elements.append(Paragraph("Evidence Inventory (Chain of Custody)", styles['Heading2']))
    evidences = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    for ev in evidences:
        elements.append(Paragraph(f"• File: {ev.filename} | Size: {ev.size} bytes", styles['Normal']))
        elements.append(Paragraph(f"  SHA-256: {ev.sha256}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # 3. Flagged Anomalies (XAI Explanations)
    elements.append(Paragraph("Flagged Anomalies (High & Medium Risk)", styles['Heading2']))
    
    events = db.query(Event).filter(Event.case_id == case_id).all()
    
    table_data = [["Time", "User", "Risk", "XAI Explanation"]]
    
    for event in events:
        score = db.query(Score).filter(Score.event_id == event.id).first()
        if score and score.level in ["High", "Medium"]:
            exp = db.query(Explanation).filter(Explanation.event_id == event.id).first()
            reason_text = exp.plain_text if exp else "Pending explanation."
            
            # Clean up the long timestamp so it fits in the column
            clean_time = event.timestamp_utc[:19].replace("T", "\n") 
            
            # Use Paragraphs inside the table so long text wraps properly
            user_para = Paragraph(f"{event.user}<br/>({event.action})", styles['Normal'])
            reason_para = Paragraph(reason_text, styles['Normal'])
            
            table_data.append([clean_time, user_para, score.level, reason_para])
            
    if len(table_data) > 1:
        # Widen the Time column from 90 to 110, and adjust the others
        table = Table(table_data, colWidths=[110, 80, 50, 230])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No High or Medium risk events detected.", styles['Normal']))
        
    # Build PDF
    doc.build(elements)
    return pdf_path