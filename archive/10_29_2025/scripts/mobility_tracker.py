#!/usr/bin/env python3
"""
mobility_tracker.py
-------------------
Imports mobility data and produces a normalized mobility index for the dashboard.

Input options (in priority order):
- data/mobility.csv (columns: date, trunk_rotation_deg, hip_rotation_deg, notes)
- data/mobility_inputs/*.json (optional individual JSON entries)

Output:
- data/mobility_data.json (array of entries with 'date' and 'mobility_index' and raw fields)

Usage:
  python scripts/mobility_tracker.py --input data/mobility.csv --out data

Notes:
- Normalized mobility_index is 0-100 (higher = better flexibility).
- You can extend scoring logic as you gather more measurements (e.g., single-leg balance, reach tests).
"""

import argparse
import json
from pathlib import Path
import csv
import math
from datetime import datetime

def score_from_measures(trunk_deg, hip_deg):
    """
    Simple scoring function:
    - trunk rotation target: 60 deg (score proportionally up to 100)
    - hip rotation target: 60 deg
    Weighted average -> mapped 0..100
    """
    t = float(trunk_deg) if trunk_deg is not None else 0.0
    h = float(hip_deg) if hip_deg is not None else 0.0
    t_score = max(0, min(1, t / 60.0))
    h_score = max(0, min(1, h / 60.0))
    raw = 0.6 * t_score + 0.4 * h_score
    return round(raw * 100, 1)

def read_csv(path: Path):
    entries = []
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # expected headers: date, trunk_rotation_deg, hip_rotation_deg, notes (optional)
            date = row.get("date") or row.get("Date") or row.get("date_str") or row.get("DateUTC") or ""
            # try to normalize date
            try:
                if date:
                    # accept formats like YYYY-MM-DD or MM/DD/YYYY
                    parsed = datetime.fromisoformat(date)
                    date = parsed.date().isoformat()
                else:
                    date = datetime.utcnow().date().isoformat()
            except Exception:
                try:
                    parsed = datetime.strptime(date, "%m/%d/%Y")
                    date = parsed.date().isoformat()
                except Exception:
                    date = datetime.utcnow().date().isoformat()

            trunk = row.get("trunk_rotation_deg") or row.get("Trunk") or row.get("trunk_deg") or row.get("Trunk_Rotation") or row.get("trunkRotation") or ""
            hip = row.get("hip_rotation_deg") or row.get("Hip") or row.get("hip_deg") or row.get("hipRotation") or ""
            notes = row.get("notes") or row.get("Notes") or ""
            try:
                trunk_f = float(trunk) if trunk != "" else None
            except:
                trunk_f = None
            try:
                hip_f = float(hip) if hip != "" else None
            except:
                hip_f = None
            entries.append({
                "date": date,
                "trunk_rotation_deg": trunk_f,
                "hip_rotation_deg": hip_f,
                "notes": notes
            })
    return entries

def read_json_inputs(dir_path: Path):
    entries = []
    if not dir_path.exists():
        return entries
    for j in dir_path.glob("*.json"):
        try:
            obj = json.loads(j.read_text())
            # expect fields date, trunk_rotation_deg, hip_rotation_deg
            date = obj.get("date", datetime.utcnow().date().isoformat())
            trunk = obj.get("trunk_rotation_deg")
            hip = obj.get("hip_rotation_deg")
            notes = obj.get("notes", "")
            entries.append({"date": date, "trunk_rotation_deg": trunk, "hip_rotation_deg": hip, "notes": notes})
        except Exception as e:
            print("Skipping", j, e)
    return entries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="data/mobility.csv", help="CSV file path of mobility records")
    parser.add_argument("--jsondir", type=str, default="data/mobility_inputs", help="Optional folder of single JSON entries")
    parser.add_argument("--out", type=str, default="data", help="Output directory for mobility_data.json")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    csv_path = Path(args.input)
    if csv_path.exists():
        records.extend(read_csv(csv_path))

    # json inputs
    records.extend(read_json_inputs(Path(args.jsondir)))

    # if no records, create a placeholder
    if not records:
        print("No mobility records found. Create data/mobility.csv or data/mobility_inputs/*.json")
        return

    # compute scores
    output = []
    for r in sorted(records, key=lambda x: x["date"]):
        idx = score_from_measures(r.get("trunk_rotation_deg") or 0, r.get("hip_rotation_deg") or 0)
        out = {
            "date": r["date"],
            "trunk_rotation_deg": r.get("trunk_rotation_deg"),
            "hip_rotation_deg": r.get("hip_rotation_deg"),
            "mobility_index": idx,
            "notes": r.get("notes", "")
        }
        output.append(out)

    out_path = out_dir / "mobility_data.json"
    with open(out_path, "w") as jf:
        json.dump({"generated_at": datetime.utcnow().isoformat() + "Z", "records": output}, jf, indent=2)

    print("Wrote mobility data to", out_path)

if __name__ == "__main__":
    main()
