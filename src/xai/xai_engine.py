def explain_suspicious_activity(timeline):
    """The robot explains why it thinks a sequence of events is suspicious."""
    
    explanation_report = []
    
    # We make a list of just the actions the user took
    actions = [event["action"] for event in timeline]
    user = timeline[0]["user"] 
    
    # The XAI Rule: If we see a Failed Login followed by a File Download, flag it!
    if "Failed Login" in actions and "File Download" in actions:
        reason = (
            f"⚠️ XAI ALERT: {user} is flagged.\n"
            f"Reason: The system prioritized this event because the user had a 'Failed Login', "
            f"but shortly after successfully logged in and performed a 'File Download'. "
            f"This pattern suggests a password guessing attack followed by data theft."
        )
        explanation_report.append(reason)
    else:
        explanation_report.append(f"✅ User {user} behavior looks normal. No explanation needed.")
        
    return explanation_report

if __name__ == "__main__":
    print("🧠 Explainable AI (XAI) Room is online!")
    
    # We feed the XAI engine the ordered timeline you just generated
    ordered_timeline = [
        {"time": "02:50AM", "user": "badguy99", "action": "Failed Login"},
        {"time": "03:00AM", "user": "badguy99", "action": "User Login"},
        {"time": "03:05AM", "user": "badguy99", "action": "File Download"}
    ]
    
    # The robot generates the human-readable explanation
    explanations = explain_suspicious_activity(ordered_timeline)
    
    print("\nRobot's Official Explanation:")
    for explanation in explanations:
        print(explanation)