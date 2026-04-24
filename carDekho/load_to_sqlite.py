import kagglehub
import pandas as pd
import sqlite3
import os
import glob

path = kagglehub.dataset_download("manishkr1754/cardekho-used-car-data")
print("Downloaded to:", path)

csv_files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
if not csv_files:
    csv_files = glob.glob(os.path.join(path, "*.csv"))

print(f"Found {len(csv_files)} CSV file(s): {csv_files}")

db_path = os.path.join(os.path.dirname(__file__), "cardekho.db")
conn = sqlite3.connect(db_path)

for csv_file in csv_files:
    table_name = os.path.splitext(os.path.basename(csv_file))[0]
    table_name = table_name.replace(" ", "_").replace("-", "_").lower()
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded '{csv_file}' -> table '{table_name}' ({len(df)} rows, {len(df.columns)} columns)")

conn.close()
print(f"\nDone. Database saved to: {db_path}")
