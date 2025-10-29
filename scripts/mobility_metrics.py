from supabase import create_client, Client
import pandas as pd
import numpy as np
from datetime import datetime

SUPABASE_URL = "https://cqlsovoiowdtfukotgdu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxbHNvdm9pb3dkdGZ1a290Z2R1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3MzMxOTYsImV4cCI6MjA3NzMwOTE5Nn0.5G4tUhd8f0M_L5Xmtknw222VTMsfAh-O4sQ0VnVXFyk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_swing_data():
    res = supabase.table("swing_analysis").select("*").execute()
    df = pd.DataFrame(res.data)
    return df

def compute_mobility_metrics(df):
    df["shoulder_range"] = df["shoulder_std"] * 2
    df["stability_score"] = 100 - (df["shoulder_std"] * 10)
    summary = {
        "avg_stability": np.mean(df["stability_score"]),
        "avg_shoulder_range": np.mean(df["shoulder_range"]),
        "mobility_index": np.mean(df["shoulder_range"]) * np.mean(df["stability_score"]) / 100
    }
    return summary

def update_mobility_summary(summary):
    supabase.table("mobility_analysis").insert({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "avg_stability": summary["avg_stability"],
        "avg_shoulder_range": summary["avg_shoulder_range"],
        "mobility_index": summary["mobility_index"]
    }).execute()

if __name__ == "__main__":
    df = fetch_swing_data()
    if not df.empty:
        summary = compute_mobility_metrics(df)
        update_mobility_summary(summary)
        print("✅ Mobility summary updated in Supabase.")
    else:
        print("⚠️ No swing data found.")
