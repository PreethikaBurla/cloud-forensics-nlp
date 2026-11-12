def generate_final_report(timeline, explanation):
    """The robot types up the final official forensic report."""
    
    report = "====================================\n"
    report += "      OFFICIAL FORENSIC REPORT      \n"
    report += "====================================\n\n"
    
    report += "TIMELINE OF EVENTS:\n"
    for step, event in enumerate(timeline, 1):
        report += f"  {step}. {event['time']} - User: {event['user']} - Action: {event['action']}\n"
        
    report += "\nEXPERT SYSTEM (XAI) ANALYSIS:\n"
    for reason in explanation:
        report += f"  {reason}\n"
        
    report += "\n====================================\n"
    report += " STATUS: READY FOR AUTOPSY REVIEW   \n"
    report += "====================================\n"
    
    return report

if __name__ == "__main__":
    print("📄 Report Generator is online!\n")
    
    # We grab the timeline from Step 3
    ordered_timeline = [
        {"time": "02:50AM", "user": "badguy99", "action": "Failed Login"},
        {"time": "03:00AM", "user": "badguy99", "action": "User Login"},
        {"time": "03:05AM", "user": "badguy99", "action": "File Download"}
    ]
    
    # We grab the explanation from Step 4
    xai_explanations = [
        "⚠️ XAI ALERT: badguy99 is flagged.\n  Reason: The system prioritized this event because the user had a 'Failed Login', but shortly after successfully logged in and performed a 'File Download'. This pattern suggests a password guessing attack followed by data theft."
    ]
    
    # The robot types up the final document
    final_document = generate_final_report(ordered_timeline, xai_explanations)
    
    # Print the final report!
    print(final_document)