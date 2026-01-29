import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

DATA_FILE = "network_traffic_data.csv"
MODEL_FILE = "iso_forest_model.pkl"

FEATURES = [
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
    'Total Length of Fwd Packets',
    'Fwd Packet Length Max',
    'Flow IAT Mean',
    'Fwd IAT Total',
    'Fwd IAT Mean',
    'Fwd PSH Flags',
    'FIN Flag Count'
]

CHUNK_SIZE = 100_000        # rows per chunk
MAX_SAMPLES = 300_000       # total rows to train on

print(" Training using chunk-based loading (low memory mode)...")

chunks = []
total_rows = 0

for chunk in pd.read_csv(DATA_FILE, low_memory=False, chunksize=CHUNK_SIZE):
    chunk.columns = chunk.columns.str.strip()

    # Keep only required features
    if not all(col in chunk.columns for col in FEATURES):
        continue

    chunk = chunk[FEATURES]
    chunk = chunk.replace([np.inf, -np.inf], np.nan)
    chunk = chunk.dropna()

    chunks.append(chunk)
    total_rows += len(chunk)

    print(f"Loaded rows so far: {total_rows}")

    if total_rows >= MAX_SAMPLES:
        break

# Combine sampled chunks
X = pd.concat(chunks, ignore_index=True)

print(f"\nFinal training samples: {len(X)}")

print(" Training Isolation Forest model...")

model = IsolationForest(
    n_estimators=100,
    contamination=0.01,
    random_state=42,
    n_jobs=-1
)

model.fit(X)

joblib.dump(model, MODEL_FILE)

print(f"\n Model trained successfully!")
print(f"📁 Saved as: {MODEL_FILE}")
