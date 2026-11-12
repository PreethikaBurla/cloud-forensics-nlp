import re

def extract_details(messy_text):
    """The speed reader looks for specific times and actions in the text."""
    
    details = {
        "time": "Unknown",
        "action": "Unknown"
    }
    
    # 1. Look for a time pattern (like 03:00AM) using regular expressions (re)
    time_pattern = r'\d{2}:\d{2}[AMPM]*'
    found_time = re.search(time_pattern, messy_text)
    if found_time:
        details["time"] = found_time.group()
        
    # 2. Look for action words
    if "download" in messy_text.lower():
        details["action"] = "File Download"
    elif "login" in messy_text.lower():
        details["action"] = "User Login"
        
    return details

if __name__ == "__main__":
    print("🔍 Speed Reader is online!")
    
    # We feed the reader the same messy clue
    test_clue = "T: 03:00AM - ID: badguy99 - did a weird download"
    
    # The reader scans it
    result = extract_details(test_clue)
    
    # We print out what it found
    print(f"I scanned the text and found these details: {result}")