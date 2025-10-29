import cv2
import mediapipe as mp
import numpy as np
import os
from supabase import create_client, Client
from datetime import datetime
import json

# ========== SUPABASE SETUP ==========
SUPABASE_URL = "https://cqlsovoiowdtfukotgdu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxbHNvdm9pb3dkdGZ1a290Z2R1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3MzMxOTYsImV4cCI6MjA3NzMwOTE5Nn0.5G4tUhd8f0M_L5Xmtknw222VTMsfAh-O4sQ0VnVXFyk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========== MEDIAPIPE POSE SETUP ==========
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """Helper to calculate angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def analyze_swing(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_data = []

    with mp_pose.Pose(static_image_mode=False, model_complexity=2) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                # Extract key joints
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                shoulder_angle = calculate_angle(left_shoulder, right_shoulder, right_hip)
                hip_angle = calculate_angle(left_hip, right_hip, right_knee) if 'right_knee' in locals() else 0

                frame_data.append({
                    "shoulder_angle": shoulder_angle,
                    "left_wrist": left_wrist,
                    "right_wrist": right_wrist
                })
        cap.release()

    # Compute aggregates
    shoulder_mean = np.mean([f["shoulder_angle"] for f in frame_data])
    shoulder_std = np.std([f["shoulder_angle"] for f in frame_data])
    left_wrist_path = json.dumps([f["left_wrist"] for f in frame_data])
    right_wrist_path = json.dumps([f["right_wrist"] for f in frame_data])

    return {
        "frames_analyzed": len(frame_data),
        "fps": fps,
        "shoulder_mean": shoulder_mean,
        "shoulder_std": shoulder_std,
        "left_wrist_path": left_wrist_path,
        "right_wrist_path": right_wrist_path
    }

def update_supabase(video_filename, metrics):
    date_str = datetime.now().strftime("%Y-%m-%d")
    supabase.table("swing_analysis").insert({
        "date": date_str,
        "video": video_filename,
        "frames_analyzed": metrics["frames_analyzed"],
        "fps": metrics["fps"],
        "shoulder_mean": metrics["shoulder_mean"],
        "shoulder_std": metrics["shoulder_std"],
        "left_wrist_path": metrics["left_wrist_path"],
        "right_wrist_path": metrics["right_wrist_path"]
    }).execute()

if __name__ == "__main__":
    video_folder = "videos_to_process"
    for video_file in os.listdir(video_folder):
        if video_file.endswith(".mp4"):
            print(f"Analyzing {video_file} ...")
            metrics = analyze_swing(os.path.join(video_folder, video_file))
            update_supabase(video_file, metrics)
            print(f"✅ Uploaded results for {video_file}")
