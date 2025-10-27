#!/bin/bash
echo "🚀 Running full Golf AI pipeline..."
python3 scripts/process_rapsodo_excel.py
python3 scripts/analyze_swing.py
bash scripts/upload_to_github.sh
echo "✅ All data processed and uploaded!"
