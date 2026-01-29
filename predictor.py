
import joblib
import numpy as np

MODEL_PATH = 'iso_forest_model.pkl'


MIN_EXPECTED_SCORE = -0.1  
MAX_EXPECTED_SCORE = 0.1  

try:
    
    ISO_FOREST_MODEL = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print(f"ERROR: Model file {MODEL_PATH} not found. Run data_prep.py first!")
    ISO_FOREST_MODEL = None


def get_safety_score(features_list):
    """
    Takes a list of features, predicts the anomaly score, and converts it to a 0-100 Safety Score.
    
    Returns: (safety_score, raw_anomaly_score)
    """
    if ISO_FOREST_MODEL is None:
        return 0, 0.0

    input_data = np.array(features_list).reshape(1, -1)
    
    
    raw_score = ISO_FOREST_MODEL.decision_function(input_data)[0] 
    
   
    clamped_score = np.clip(raw_score, MIN_EXPECTED_SCORE, MAX_EXPECTED_SCORE)
    
    
    safety_score = ((clamped_score - MIN_EXPECTED_SCORE) / 
                    (MAX_EXPECTED_SCORE - MIN_EXPECTED_SCORE)) * 100
    
    
    safety_score = np.clip(safety_score, 0, 100)
    
    return int(safety_score), raw_score