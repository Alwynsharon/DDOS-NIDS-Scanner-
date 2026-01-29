import streamlit as st
import pandas as pd
import numpy as np
from predictor import get_safety_score
from data_prep import FEATURES


NORMAL_FEATURES = [64, 3, 4, 160, 37, 21.33, 64, 21.33, 0, 0] 
ATTACK_FEATURES = [1000000, 100, 100, 10000, 100, 9900.5, 1000000, 9900.5, 1, 0]



def get_color(score):
    if score >= 80:
        return 'green'
    elif score >= 50:
        return 'orange'
    else:
        return 'red'

def display_status(score):
    if score >= 80:
        st.success(" SYSTEM STATUS: SAFE (Normal Traffic Baseline)")
    elif score >= 50:
        st.warning("⚠️ ALERT: Elevated Risk. Anomalous Traffic Detected.")
    else:
        st.error(" CRITICAL ANOMALY DETECTED! Potential DoS/DDoS Attack.")


st.set_page_config(layout="wide")
st.title("🛡️ Real-Time Network Anomaly Detector")
st.caption("Using Isolation Forest for unsupervised DDoS/DoS detection.")


with st.sidebar:
    st.header("1. Choose Scenario")
    scenario = st.selectbox(
        "Select Traffic Scenario to Simulate:",
        ("Normal Traffic (Safe Baseline)", "DDoS Attack (High Anomaly)")
    )
    
    st.header("2. Model Details")
    st.info(f"Model: Isolation Forest")
    st.info(f"Anomaly Contamination Rate: 1%")

    st.header("3. Key Features Used")
    st.code('\n'.join(FEATURES[:5]) + '\n...')


if scenario == "Normal Traffic (Safe Baseline)":
    input_features = NORMAL_FEATURES
    st.subheader(f"Simulating: {scenario}")
elif scenario == "DDoS Attack (High Anomaly)":
    input_features = ATTACK_FEATURES
    st.subheader(f"Simulating: {scenario}")


safety_score, raw_score = get_safety_score(input_features)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Current Network Safety Score")
    
    st.markdown(
        f"""
        <div style='
            background-color: {get_color(safety_score)}; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            color: white;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        '>
            <h1 style='font-size: 80px; margin: 0;'>{safety_score}</h1>
            <p style='margin: 0;'>/ 100 Safety</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    display_status(safety_score)
    st.metric(label="Raw Isolation Forest Score (Negative = Anomaly)", value=f"{raw_score:.4f}")

with col2:
    st.markdown("### Network Feature Input (Simulated Data Snapshot)")
    
    
    feature_df = pd.DataFrame({
        'Feature Name': FEATURES, 
        'Current Value': input_features,
        'Description': ["Duration of the flow in microseconds", "Total packets flowing forward", "Total packets flowing backward", 
                        "Total size of forward packets", "Max length of a forward packet", 
                        "Mean time between two consecutive packets", "Total time spent for forward IAT", "Mean time between forward packets", 
                        "Number of PSH flags set in forward direction", "Number of FIN flags set"]
    })
    
    st.dataframe(feature_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.info("The model is based on these 10 features extracted from network flow data. An anomalous value in any of these features can drastically drop the Safety Score.")