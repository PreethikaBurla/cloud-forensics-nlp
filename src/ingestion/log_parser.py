import json

def normalize_log(raw_clue):
    """The robot takes a messy clue and puts it in a neat, labeled box."""
    
    # This is the neat empty box
    clean_clue = {
        "time": "Unknown",
        "user": "Unknown",
        "action": "Unknown",
        "messy_original": raw_clue
    }
    
    # A super simple test to see if the robot can spot a user
    if "badguy99" in raw_clue:
        clean_clue["user"] = "badguy99"
        
    return clean_clue

if __name__ == "__main__":
    print("🤖 Sorting Room is online!")
    
    # We feed the robot a fake, messy cloud log
    test_clue = "T: 03:00AM - ID: badguy99 - did a weird download"
    
    # The robot sorts it
    result = normalize_log(test_clue)
    
    # We print out the neat box
    print("Here is the neatly sorted clue:")
    print(json.dumps(result, indent=2))