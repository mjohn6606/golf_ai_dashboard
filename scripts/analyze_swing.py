import cv2, mediapipe as mp, json
from pathlib import Path

data_dir = Path(__file__).resolve().parents[1] / "data"
video_dir = data_dir / "swing_videos"
output_json = data_dir / "sample_swing_analysis.json"
output_viz_dir = data_dir / "swing_analysis_visuals"
output_viz_dir.mkdir(exist_ok=True)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

all_swing_data = []

for video_path in video_dir.glob("*.mp4"):
    cap = cv2.VideoCapture(str(video_path))
    frame_count, total_frames = 0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        frame_count += 1
        if frame_count % 5 != 0: continue  # analyze every 5th frame

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        if results.pose_landmarks:
            landmarks = [{lm.name: (lm.x, lm.y, lm.z)} for lm in mp_pose.PoseLandmark]
            all_swing_data.append({
                "video": video_path.name,
                "frame": frame_count,
                "landmarks": landmarks
            })
    cap.release()

with open(output_json, "w") as f:
    json.dump(all_swing_data, f, indent=2)

print(f"✅ Swing data extracted for {len(all_swing_data)} frames.")
