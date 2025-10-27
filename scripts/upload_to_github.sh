#!/usr/bin/env bash
# Simple upload workflow: commit & push all changes (requires git SSH configured)
git add data/*
git commit -m "Update dashboard data" || true
git push origin main
echo "Data pushed. GitHub Pages will update shortly."
