import spacy
import re

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_entities(file_path):
    print("🧠 NLP Engine activated. Analyzing text...")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    structured_data = []
    
    for line in lines:
        if not line.strip(): 
            continue
            
        # Process the raw text through SpaCy
        doc = nlp(line)
        
        # Use SpaCy to identify Time/Date entities intelligently
        time_entity = "Unknown"
        for ent in doc.ents:
            if ent.label_ in ["TIME", "DATE"]:
                time_entity = ent.text
                break
                
        # Extract explicit cloud log parameters
        user_match = re.search(r'User:\s*([^\s,]+)', line, re.IGNORECASE)
        action_match = re.search(r'Action:\s*([^,]+)', line, re.IGNORECASE)
        
        user = user_match.group(1) if user_match else "Unknown"
        action = action_match.group(1).strip() if action_match else "Unknown"
        
        structured_data.append({"time": time_entity, "user": user, "action": action})
        print(f"   [NLP Extracted] Time: {time_entity:<10} | User: {user:<10} | Action: {action}")
        
    return structured_data