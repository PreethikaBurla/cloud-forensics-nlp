import json
import random
from datetime import datetime, timedelta
import os

# Save the logs to the synthetic data folder
OUTPUT_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "synthetic", "test_logs.json"))

users = ["alice@company.com", "bob@company.com", "charlie@company.com"]
actions = ["User Login", "File Read", "File Upload"]
ips = ["192.168.1.10", "192.168.1.15", "192.168.1.20"]

logs = []
start_time = datetime.utcnow() - timedelta(days=1)

# 1. Generate 100 Normal Events
for i in range(100):
    user = random.choice(users)
    action = random.choice(actions)
    ip = random.choice(ips)
    timestamp = (start_time + timedelta(minutes=i*5)).isoformat() + "Z"
    
    # The raw log text that the NLP engine will parse later
    raw_text = f"At {timestamp}, the system recorded that User: {user} performed Action: {action} from IP: {ip}."
    
    logs.append({
        "timestamp_utc": timestamp,
        "source": "aws",
        "user": user,
        "action": action,
        "resource": "financial_report.pdf",
        "ip": ip,
        "location": "India",
        "raw_text": raw_text,
        "is_malicious": 0  # Ground truth label for your Random Forest
    })

# 2. Inject 5 Malicious Attack Events (The Anomaly)
malicious_user = "badguy99"
malicious_ip = "203.0.113.50"

for i in range(5):
    action = "Mass Delete" if i > 0 else "Failed Login"
    timestamp = (start_time + timedelta(minutes=400 + i)).isoformat() + "Z"
    
    raw_text = f"ALERT: At {timestamp}, User: {malicious_user} performed Action: {action} on confidential files originating from unknown device at {malicious_ip}."
    
    logs.append({
        "timestamp_utc": timestamp,
        "source": "aws",
        "user": malicious_user,
        "action": action,
        "resource": "confidential_data.zip",
        "ip": malicious_ip,
        "location": "Unknown",
        "raw_text": raw_text,
        "is_malicious": 1  # Ground truth label
    })

# 3. Save the JSON File
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    json.dump(logs, f, indent=4)

print(f"✅ Generated {len(logs)} synthetic cloud logs at: {OUTPUT_FILE}")