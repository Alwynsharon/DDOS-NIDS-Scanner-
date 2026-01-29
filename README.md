# DDOS-NIDS-Scanner-
🛡️ Sentinel:

AI-Powered Real-Time Network Intrusion Detection System (NIDS)Sentinel is a lightweight, hybrid Network Intrusion Detection System designed to monitor live network traffic, detect volumetric attacks (DDoS), and identify zero-day anomalies in real-time.Unlike traditional systems that rely on static PCAP files or delayed log analysis, Sentinel captures traffic directly from the network interface (NIC) and processes it with sub-second latency. It features a unique Hybrid Detection Engine that solves the "False Positive Paradox," distinguishing between malicious floods and legitimate high-bandwidth tasks like 4K video streaming.

🚀 Key Features⚡ 

Live-Only Architecture: Eliminates dependency on static datasets. Captures and analyzes packets directly from Wi-Fi/Ethernet in real-time.

🧠 Hybrid Detection Engine: Combines Unsupervised Machine Learning (Isolation Forest) for unknown threats with Deterministic Rules for known signatures (SYN/UDP Floods).

✅ Behavioral Whitelisting: intelligently identifies safe high-load traffic (e.g., YouTube/Netflix) by analyzing Packet Size vs. Throughput ratios, achieving a 0% False Positive Rate on video streaming.

📊 Low-Latency Dashboard: A React-based frontend providing a live telemetry graph, instantaneous "Safety Score," and active flow matrices with <500ms polling.

🚨 Automated Response: Triggers immediate SMTP Email Alerts when the network Safety Score drops below critical thresholds.

📂 Forensic Export: One-click export of captured session data to JSON/CSV for offline auditing and legal compliance.

🛠️ System ArchitectureThe system operates on a differential processing pipeline to ensure zero-lag detection:
Ingestion: Scapy sniffer captures raw packets in promiscuous mode.

Feature Extraction: Calculates instantaneous velocity (PPS/BPS) and protocol distribution.Analysis:

The Hybrid Engine applies Whitelisting Rule Checks ML Anomaly Detection.Action: Updates the Dashboard and triggers Email Alerts if risk is detected.


💻 Tech StackBackend (Python)FastAPI: 

High-performance async API for data streaming.Scapy: For low-level packet sniffing and manipulation.Scikit-Learn:

Implementation of the Isolation Forest algorithm.Pandas/NumPy: Real-time data aggregation and statistical analysis.

Frontend (React)Vite: Fast build tool and development server.Recharts: Dynamic, responsive charting for live telemetry.

Tailwind CSS: Modern utility-first styling for the dashboard UI.


⚙️ Installation & SetupPrerequisites

Python 3.9+Node.js & npmWindows Users: Install Npcap (Ensure "Install in API-compatible Mode" is checked).

Linux Users: Ensure libpcap is installed (sudo apt-get install libpcap-dev).
