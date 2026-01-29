import pandas as pd
import os

DATA_FOLDER = "data"
OUTPUT_FILE = "network_traffic_data.csv"

print("  Looking for CSV files...")

if not os.path.exists(DATA_FOLDER):
    print(" 'data' folder not found")
    exit()

csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

if not csv_files:
    print("No CSV files found inside 'data' folder")
    exit()

df_list = []

for file in csv_files:
    file_path = os.path.join(DATA_FOLDER, file)
    print(f" Loading: {file}")
    try:
        df = pd.read_csv(file_path, low_memory=False)
        df_list.append(df)
    except Exception as e:
        print(f"  Failed to load {file}: {e}")

combined_df = pd.concat(df_list, ignore_index=True)

combined_df.to_csv(OUTPUT_FILE, index=False)

print("\n  DATA COMBINATION COMPLETE")
print(f"Files combined : {len(csv_files)}")
print(f"Total rows     : {len(combined_df)}")
print(f"Saved as       : {OUTPUT_FILE}")
