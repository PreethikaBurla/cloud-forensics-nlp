import pandas as pd
from sklearn.ensemble import IsolationForest
import warnings

# Suppress sklearn warnings for a clean terminal output
warnings.filterwarnings('ignore')

def analyze_events(parsed_data):
    print("\n🤖 XAI Engine activated. Analyzing behavior patterns...")
    
    # Convert the NLP extracted dictionary into a Pandas DataFrame
    df = pd.DataFrame(parsed_data)
    
    # 1. Feature Engineering: Convert text actions into numerical risk weights
    risk_mapping = {"Failed Login": 10, "User Login": 1, "File Download": 5, "Unknown": 2}
    df['risk_score'] = df['action'].map(risk_mapping).fillna(2)
    X_live = df[['risk_score']]
    
    # 2. Baseline Data: Simulating standard, normal server traffic for the ML model to learn from
    normal_traffic = pd.DataFrame({'risk_score': [1, 1, 1, 2, 1, 1, 1, 1, 1, 1]})
    X_train = pd.concat([X_live, normal_traffic], ignore_index=True)
    
    # 3. AI Anomaly Detection: Train the Isolation Forest
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train)
    
    # 4. Predict on the live incoming log (-1 means anomaly/threat, 1 means normal)
    df['is_anomaly'] = model.predict(X_live)
    
    # 5. Output the Explainable AI (XAI) Alert
    for index, row in df.iterrows():
        if row['is_anomaly'] == -1:
            print(f"   ⚠️ XAI ALERT: {row['user']} is flagged!")
            print(f"      Explainability: Action '{row['action']}' heavily deviates from baseline risk norms.")
        else:
            print(f"   ✅ CLEAR: {row['user']} - {row['action']} (Normal pattern)")
            
    return df