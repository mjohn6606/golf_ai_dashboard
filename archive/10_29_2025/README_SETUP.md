
Project Scratch — GitHub Pages Golf AI Dashboard (Download Package)
=================================================================

Contents in this package (copy into a new GitHub repo):
- index.html
- assets/style.css
- assets/dashboard.js
- data/sample_rapsodo.json
- data/sample_swing_analysis.json
- data/sample_mobility.json
- scripts/analyze_swing.py  (run locally to analyze swing video)
- scripts/upload_to_github.sh (simple git push script using SSH)
- .github/workflows/auto_update.yml (optional GH Action to auto-run analyzer when new videos added)

Quick start (step-by-step)
--------------------------

1) Create a new GitHub repo (public) named e.g. golf-ai-dashboard.
   - On your computer: git clone git@github.com:YOUR_USERNAME/golf-ai-dashboard.git
   - Copy the files from this package into the repo folder.

2) Set up SSH (if not already):
   - Generate: ssh-keygen -t ed25519 -C "your_email@example.com"
   - Add to ssh-agent: eval "$(ssh-agent -s)"; ssh-add ~/.ssh/id_ed25519
   - Copy public key and add to GitHub (Settings -> SSH and GPG keys)

3) Push files to GitHub via SSH:
   git add .
   git commit -m "Initial dashboard"
   git push origin main

4) Enable GitHub Pages:
   - Repo -> Settings -> Pages -> Source: main branch, folder: / (root)
   - Save. Wait ~1–2 minutes.
   - Visit: https://YOUR_USERNAME.github.io/golf-ai-dashboard/

5) Provide real data:
   - Replace data/sample_rapsodo.json with your exported Rapsodo JSON (array of shot objects)
   - Run the swing analyzer locally:
     pip install opencv-python mediapipe numpy moviepy
     python scripts/analyze_swing.py --video path/to/swing.mp4 --out annotated.mp4 --json data/sample_swing_analysis.json
   - Edit data/sample_mobility.json with mobility logs (date, trunk_rotation_deg, hip_rotation_deg)
   - Commit & push updated data (git add data/* && git commit && git push) or use scripts/upload_to_github.sh

6) Automations (optional):
   - Use the included GitHub Action to run analysis when you push files to /videos (customize path and file names)
   - Or run the analyzer locally and push outputs.

7) AI Insights:
   - Right now dashboard uses simple rule-based insight. For LLM insights, deploy a Vercel serverless endpoint and modify assets/dashboard.js to call it.

Security notes
--------------
- Do not commit API keys or secret tokens to the repo.
- If you automate uploads via GitHub API, use GitHub Actions secrets or a small server to avoid exposing tokens in the repo.

If you want, I can:
- Prepare the repository contents as a ZIP file (done) and give you the download link.
- Provide exact SSH & git commands tailored to your OS (macOS/Linux/Windows WSL).
- Customize the dashboard visuals or add more charts (heatmaps, dispersion, carry consistency).

