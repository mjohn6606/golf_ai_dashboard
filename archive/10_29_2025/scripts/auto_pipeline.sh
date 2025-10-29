#!/bin/bash
echo "🚀 Running full Golf AI pipeline..."
python3 scripts/process_rapsodo_excel.py
python3 scripts/analyze_swing.py --videos data/swing_videos --outdata data --annotate --downsample 2
python3 scripts/mobility_tracker.py --input data/mobility.csv --out data
bash scripts/upload_to_github.sh
echo "✅ All data processed and uploaded!"
