def build_timeline(clues):
    """The robot lines up all the clues by the time on the clock."""
    
    # Sort the clues based on the 'time' they happened
    sorted_clues = sorted(clues, key=lambda x: x["time"])
    return sorted_clues

if __name__ == "__main__":
    print("🕰️ Timeline Builder is online!")
    
    # We give the robot three clues, but they are totally out of order!
    mixed_up_clues = [
        {"time": "03:05AM", "user": "badguy99", "action": "File Download"},
        {"time": "02:50AM", "user": "badguy99", "action": "Failed Login"},
        {"time": "03:00AM", "user": "badguy99", "action": "User Login"}
    ]
    
    # The robot sorts them out
    ordered_timeline = build_timeline(mixed_up_clues)
    
    print("\nHere is the true story of the crime:")
    for step, event in enumerate(ordered_timeline, 1):
        print(f"Step {step}: At {event['time']}, {event['user']} did a {event['action']}")