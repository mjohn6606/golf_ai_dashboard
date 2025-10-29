import pandas as pd
import json
import glob
import os

def process_latest_rapsodo(data_dir="./data/rapsodo_uploads"):
    # Get most recent CSV
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        raise FileNotFoundError("No Rapsodo CSVs found in /data folder.")
    latest_file = max(csv_files, key=os.path.getctime)

    df = pd.read_csv(latest_file)

    # Clean up columns
    df.columns = df.columns.str.strip()

    # Compute per-club summaries
    summary = df.groupby("Club Type").agg({
        "Carry Distance": ["mean", "std"],
        "Total Distance": "mean",
        "Ball Speed": "mean",
        "Launch Angle": "mean",
        "Club Speed": "mean",
        "Smash Factor": "mean"
    }).round(2)

    summary.columns = ["_".join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    # Create dispersion data (side carry spread)
    dispersion = df.groupby("Club Type")["Side Carry"].apply(list).to_dict()

    # Merge everything
    output = {
        "clubs": summary.to_dict(orient="records"),
        "dispersion": dispersion
    }

    # Save as JSON for dashboard
    current_directory = os.getcwd()
    output_path = os.path.join(current_directory, "./data/rapsodo.json")

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Processed {latest_file} → {output_path}")

if __name__ == "__main__":
    process_latest_rapsodo()
