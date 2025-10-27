#!/bin/bash
cd "$(dirname "$0")/.."
git add .
git commit -m "Auto-update: Rapsodo + Swing data"
git push origin main
