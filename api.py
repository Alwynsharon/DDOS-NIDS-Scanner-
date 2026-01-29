import os
import time
import threading
import joblib
import pandas as pd
import numpy as np
import warnings
import smtplib
from email.mime.text import MIMEText
from collections import defaultdict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from scapy.all import sniff, IP, TCP, UDP
from sklearn.ensemble import IsolationForest


# --- SILENCE WARNINGS ---
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. EMAIL CONFIGURATION ---

EMAIL_SENDER = "nidsddosalert@gmail.com"
EMAIL_PASSWORD = "ottp zcgb wxjx ttdx" 
EMAIL_RECEIVER = "yogeshofficial55@gmail.com"
ALERT_THRESHOLD = 50 

# --- CONFIGURATION ---
MODEL_PATH = "nids_live_final_v3.pkl"

# --- STATE MANAGEMENT ---
class LiveFlowManager:
    def __init__(self):
        self.flows = defaultdict(lambda: {
            "src": "", "dst": "", "dst_port": 0, "proto": "",
            "packet_count": 0, "byte_count": 0,
            "syn_count": 0, "tcp_count": 0,
            "last_check_time": time.time(),
            "last_packet_count": 0,
            "last_byte_count": 0
        })
        self.lock = threading.Lock()
        self.total_packets = 0
        self.is_running = False
        self.graph_cursor = 0 
        self.last_email_time = 0 

    def reset(self):
        with self.lock:
            self.flows.clear()
            self.total_packets = 0
            self.graph_cursor = 0
            self.is_running = True

    def process_packet(self, pkt):
        if IP not in pkt: return
        src = pkt[IP].src
        dst = pkt[IP].dst
        length = len(pkt)
        sport, dport, proto = 0, 0, "OTHER"
        is_syn = False

        if TCP in pkt:
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            proto = "TCP"
            if 'S' in str(pkt[TCP].flags): is_syn = True
        elif UDP in pkt:
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            proto = "UDP"

        key = (src, dst, sport, dport, proto)

        with self.lock:
            f = self.flows[key]
            if f["packet_count"] == 0:
                f["src"] = src
                f["dst"] = dst
                f["dst_port"] = dport
                f["proto"] = proto
                f["last_check_time"] = time.time()

            f["packet_count"] += 1
            f["byte_count"] += length
            if proto == "TCP":
                f["tcp_count"] += 1
                if is_syn: f["syn_count"] += 1
            self.total_packets += 1

    def get_snapshot(self):
        with self.lock:
            data = []
            now = time.time()
            
            for key, f in self.flows.items():
                time_diff = now - f["last_check_time"]
                if time_diff < 0.1: time_diff = 0.1
                
                packets_diff = f["packet_count"] - f["last_packet_count"]
                bytes_diff = f["byte_count"] - f["last_byte_count"]
                
                f["last_packet_count"] = f["packet_count"]
                f["last_byte_count"] = f["byte_count"]
                f["last_check_time"] = now
                
                pps = packets_diff / time_diff
                bps = bytes_diff / time_diff
                
                if pps == 0 and f["packet_count"] > 1: continue

                syn_ratio = 0
                if f["tcp_count"] > 0: syn_ratio = f["syn_count"] / f["tcp_count"]
                avg_len = f["byte_count"] / max(1, f["packet_count"])

                data.append({
                    "src_ip": f["src"], "dest_ip": f["dst"], "proto": f["proto"],
                    "dst_port": f["dst_port"], "pps": pps, "bps": bps,
                    "syn_ratio": syn_ratio, "avg_len": avg_len,
                    "total_packets": f["packet_count"],
                    "features": { "Flow Duration": time_diff, "Total Fwd Packets": f["packet_count"], "Fwd Packet Length Max": avg_len }
                })
            return pd.DataFrame(data)

state = LiveFlowManager()

# --- EMAIL ALERT WORKER ---
def send_email_alert(score, anomalies):
    try:
        msg = MIMEText(f"""
        ⚠️ CRITICAL NIDS ALERT ⚠️
        
        The system has detected abnormal traffic patterns.
        
        - Safety Score: {score}/100 (CRITICAL)
        - Active Anomalies: {anomalies}
        - Timestamp: {time.ctime()}
        
        Immediate investigation required.
        """)
        msg['Subject'] = f"🚨 NIDS ALERT: Safety dropped to {score}%"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("📧 Alert Email Sent Successfully!")
            
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- ML ENGINE ---
def train_model():
    print("✅ Training Live Model...")
    clf = IsolationForest(contamination=0.01, random_state=42)
    X_train = np.random.normal(loc=[10, 500, 0.1], scale=[5, 200, 0.05], size=(100, 3))
    clf.fit(X_train)
    joblib.dump(clf, MODEL_PATH)
    return clf

if not os.path.exists(MODEL_PATH):
    model = train_model()
else:
    try:
        model = joblib.load(MODEL_PATH)
        if not hasattr(model, "n_features_in_") or model.n_features_in_ != 3:
            model = train_model()
    except:
        model = train_model()

# --- DETECTION LOGIC ---
def analyze_traffic(df):
    if df.empty: return df
    df["label"] = "Normal Traffic"
    df["raw_score"] = 0.1 

    mask_syn = (df["proto"] == "TCP") & (df["syn_ratio"] > 0.8) & (df["pps"] > 50)
    df.loc[mask_syn, "label"] = "SYN Flood Attack"
    df.loc[mask_syn, "raw_score"] = -0.5 

    mask_udp = (df["proto"] == "UDP") & (df["pps"] > 100)
    df.loc[mask_udp, "label"] = "UDP Flood Attack"
    df.loc[mask_udp, "raw_score"] = -0.5 

    mask_http = (df["dst_port"].isin([80, 443, 8080])) & (df["pps"] > 50) & (df["avg_len"] < 200)
    df.loc[mask_http, "label"] = "HTTP/Web DoS Attack"
    df.loc[mask_http, "raw_score"] = -0.5 

    mask_safe = (df["avg_len"] > 800)
    df.loc[mask_safe, "label"] = "Normal Traffic"
    df.loc[mask_safe, "raw_score"] = 0.1

    unknown_mask = (df["label"] == "Normal Traffic")
    if unknown_mask.any():
        features = df.loc[unknown_mask, ["pps", "bps", "syn_ratio"]].fillna(0).values
        try:
            preds = model.predict(features)
            anom_idx = df.index[unknown_mask][preds == -1]
            df.loc[anom_idx, "label"] = "Unknown Anomaly"
            df.loc[anom_idx, "raw_score"] = -0.2 
        except: pass
    return df

# --- BACKGROUND SNIFFER ---
def sniffer_loop():
    while True:
        if state.is_running:
            sniff(prn=state.process_packet, count=10, timeout=0.5, store=0)
        else:
            time.sleep(0.5)

t = threading.Thread(target=sniffer_loop, daemon=True)
t.start()

# --- API ENDPOINTS ---
@app.post("/start_capture")
def start_capture():
    state.reset()
    return {"status": "started"}

@app.post("/stop_capture")
def stop_capture():
    state.is_running = False
    return {"status": "stopped"}

@app.get("/live_feed")
def live_feed():
    df = state.get_snapshot()
    df_analyzed = analyze_traffic(df)
    
    if df_analyzed.empty:
        state.graph_cursor += 1
        return {
            "data": [{"id": state.graph_cursor, "raw_score": 0.1, "pps": 0, "label": "Waiting...", "src_ip": "-", "dest_ip": "-"}],
            "current_safety": 100,
            "total_count": state.total_packets,
            "anomaly_count": 0
        }

    ui_data = df_analyzed[["src_ip", "dest_ip", "raw_score", "label", "pps", "features"]].tail(50).to_dict(orient="records")
    
    start_id = state.graph_cursor
    for i, row in enumerate(ui_data):
        row["id"] = start_id + i
    state.graph_cursor += len(ui_data)
    
    total = len(df_analyzed)
    bad_count = len(df_analyzed[df_analyzed["raw_score"] < 0])
    
    safety_index = 100
    if total > 0:
        ratio = bad_count / total
        penalty = int(ratio * 100)
        safety_index = max(0, 100 - penalty)
        
    # --- EMAIL TRIGGER LOGIC ---
    if safety_index < ALERT_THRESHOLD:
        now = time.time()
        # Cooldown: Send email only once every 60 seconds
        if now - state.last_email_time > 60:
            email_thread = threading.Thread(target=send_email_alert, args=(safety_index, bad_count))
            email_thread.start()
            state.last_email_time = now

    return {
        "data": ui_data,
        "current_safety": safety_index,
        "total_count": state.total_packets,
        "anomaly_count": bad_count
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)