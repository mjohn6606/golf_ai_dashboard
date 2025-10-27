import pandas as pd
import json
from pathlib import Path

data_dir = Path(__file__).resolve().parents[1] / "data"
input_dir = data_dir / "rapsodo_uploads"
output_file = data_dir / "sample_rapsodo.json"

all_data = []

for file in input_dir.glob("*.xlsx"):
    df = pd.read_excel(file)
    df.fillna("", inplace=True)
    data = df.to_dict(orient="records")
    all_data.extend(data)

with open(output_file, "w") as f:
    json.dump(all_data, f, indent=2)

print(f"✅ Updated {output_file} with {len(all_data)} entries from Excel files.")
