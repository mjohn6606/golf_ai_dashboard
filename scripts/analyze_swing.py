#!/usr/bin/env python3
"""
analyze_swing.py
----------------
OpenCV + MediaPipe pose-based golf swing analyzer.

Features:
- Scans a directory (default: ./videos) for .mp4/.mov files
- For each video:
  - Extracts pose landmarks (MediaPipe)
  - Computes shoulder and hip rotation angles per frame
  - Estimates tempo ratio (backswing : downswing)
  - Computes hand path summary (wrist lateral and vertical movement)
  - Optionally writes an annotated video (with landmarks and shoulder angle)
  - Writes per-video JSON and appends/overwrites an aggregate data/swing_analysis.json

Usage:
  python scripts/analyze_swing.py --videos videos --outdata data --annotate True

Dependencies:
  pip install opencv-python mediapipe numpy tqdm

Notes:
- This is a pose-based heuristic analyzer. For more precise clubhead detection, combine with club detection model or Rapsodo-provided metrics.
"""

import argparse
import json
import os
from pathlib import Path
import cv2
import numpy as np
import mediapipe as mp
from tqdm import tqdm
from datetime import datetime

mp_pose = mp.solutions.pose

def angle_between(a, b, c):
    """Return angle at point b (in degrees) formed by points a-b-c"""
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-9
    cosang = np.dot(ba, bc) / denom
    cosang = np.clip(cosang, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def landmark_to_xy(landmark, w, h):
    return np.array([landmark.x * w, landmark.y * h])

def analyze_one_video(video_path: Path, out_dir: Path, annotate: bool = False, downsample: int = 1):
    """
    Analyze a single swing video.
    - downsample: analyze every Nth frame (1 = every frame). Use >1 to speed up.
    Returns a dictionary summary and writes JSON + (optional) annotated video.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    annotated_frames = []
    results_list = []

    # iterate frames
    frame_idx = 0
    pbar = tqdm(total=total_frames, desc=f"Analyze {video_path.name}", unit="f")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        pbar.update(1)
        if (frame_idx % downsample) != 0:
            continue

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(image_rgb)
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            # Use MediaPipe's landmark indices
            L_SH = mp_pose.PoseLandmark.LEFT_SHOULDER.value
            R_SH = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
            L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
            R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
            L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
            R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value

            l_sh = landmark_to_xy(lm[L_SH], width, height)
            r_sh = landmark_to_xy(lm[R_SH], width, height)
            l_hip = landmark_to_xy(lm[L_HIP], width, height)
            r_hip = landmark_to_xy(lm[R_HIP], width, height)
            l_wrist = landmark_to_xy(lm[L_WRIST], width, height)
            r_wrist = landmark_to_xy(lm[R_WRIST], width, height)

            # shoulder angle measured as angle(left_shoulder, mid_shoulder, right_shoulder)
            mid_sh = (l_sh + r_sh) / 2.0
            shoulder_angle = angle_between(l_sh, mid_sh, r_sh)

            mid_hip = (l_hip + r_hip) / 2.0
            hip_angle = angle_between(l_hip, mid_hip, r_hip)

            # choose lead wrist as the one with greater x displacement relative to body center (approx)
            # if right-handed player, lead wrist is left wrist at setup? We will keep both and record both paths.
            results_list.append({
                "frame": frame_idx,
                "shoulder_angle": shoulder_angle,
                "hip_angle": hip_angle,
                "left_wrist": [float(l_wrist[0]), float(l_wrist[1])],
                "right_wrist": [float(r_wrist[0]), float(r_wrist[1])]
            })

            # annotate frame if requested
            if annotate:
                # draw landmark dots
                for lmpt in res.pose_landmarks.landmark:
                    x = int(lmpt.x * width)
                    y = int(lmpt.y * height)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                cv2.putText(frame, f"Sh:{shoulder_angle:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Hip:{hip_angle:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            if annotate:
                cv2.putText(frame, "No landmarks", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        if annotate:
            annotated_frames.append(frame)

    pbar.close()
    cap.release()
    pose.close()

    if not results_list:
        raise RuntimeError(f"No pose landmarks found in video: {video_path}")

    # Convert results to numpy arrays for calculations
    shoulder_angles = np.array([r["shoulder_angle"] for r in results_list])
    hip_angles = np.array([r["hip_angle"] for r in results_list])

    # tempo estimate:
    # - define top-of-backswing as frame with maximum shoulder_angle
    # - define swing start as first frame; end as last frame with landmarks
    frame_numbers = np.array([r["frame"] for r in results_list])
    start_frame = frame_numbers[0]
    end_frame = frame_numbers[-1]
    top_idx = int(np.argmax(shoulder_angles))
    top_frame = frame_numbers[top_idx]
    backswing_frames = top_frame - start_frame
    downswing_frames = end_frame - top_frame if end_frame - top_frame > 0 else 1
    tempo_ratio = round((backswing_frames / downswing_frames) if downswing_frames else float('inf'), 3)
    swing_duration_seconds = (end_frame - start_frame) / (fps or 30)

    # hand path: measure wrist lateral displacement (x) and vertical (y) normalized by frame width/height
    left_wrist_arr = np.array([r["left_wrist"] for r in results_list])
    right_wrist_arr = np.array([r["right_wrist"] for r in results_list])

    def wrist_path_stats(arr):
        xs = arr[:, 0]
        ys = arr[:, 1]
        return {
            "x_range": float(np.max(xs) - np.min(xs)),
            "y_range": float(np.max(ys) - np.min(ys)),
            "x_std": float(np.std(xs)),
            "y_std": float(np.std(ys)),
            "start": [float(xs[0]), float(ys[0])],
            "end": [float(xs[-1]), float(ys[-1])]
        }

    left_stats = wrist_path_stats(left_wrist_arr)
    right_stats = wrist_path_stats(right_wrist_arr)

    summary = {
        "video": video_path.name,
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "frames_analyzed": len(results_list),
        "fps": fps,
        "swing_duration_seconds": round(swing_duration_seconds, 3),
        "tempo_ratio": tempo_ratio,
        "shoulder_mean": float(np.mean(shoulder_angles)),
        "shoulder_std": float(np.std(shoulder_angles)),
        "hip_mean": float(np.mean(hip_angles)),
        "hip_std": float(np.std(hip_angles)),
        "left_wrist": left_stats,
        "right_wrist": right_stats,
        "raw": results_list  # truncated by caller if desired
    }

    # write per-video JSON
    out_json = out_dir / f"swing_analysis_{video_path.stem}.json"
    with open(out_json, "w") as jf:
        json.dump(summary, jf, indent=2)

    # optionally write annotated video
    if annotate and annotated_frames:
        annotated_path = out_dir / f"{video_path.stem}_annotated.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(annotated_path), fourcc, fps, (width, height))
        for f in annotated_frames:
            out.write(f)
        out.release()
        summary["annotated_video"] = str(annotated_path.name)

    return summary

def aggregate_results(out_dir: Path, video_summaries: list):
    agg_path = out_dir / "swing_analysis.json"
    # Write an aggregated file with all video summaries
    with open(agg_path, "w") as f:
        json.dump({"generated_at": datetime.utcnow().isoformat() + "Z", "videos": video_summaries}, f, indent=2)
    return agg_path

def main():
    parser = argparse.ArgumentParser(description="Batch analyze swing videos and produce JSON summaries.")
    parser.add_argument("--videos", type=str, default="swing_videos", help="Directory containing videos (mp4/mov).")
    parser.add_argument("--outdata", type=str, default="data", help="Directory to write JSON output.")
    parser.add_argument("--annotate", action="store_true", help="Write annotated video files (slower).")
    parser.add_argument("--downsample", type=int, default=1, help="Analyze every Nth frame to speed up.")
    args = parser.parse_args()

    videos_dir = Path(args.videos)
    out_dir = Path(args.outdata)
    out_dir.mkdir(parents=True, exist_ok=True)

    video_files = sorted([p for p in videos_dir.glob("*") if p.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]])
    if not video_files:
        print("No videos found in", videos_dir)
        return

    summaries = []
    for v in video_files:
        try:
            s = analyze_one_video(v, out_dir, annotate=args.annotate, downsample=args.downsample)
            print("Wrote", v.name, "→", f"swing_analysis_{v.stem}.json")
            summaries.append(s)
        except Exception as e:
            print("ERROR analyzing", v.name, e)

    agg = aggregate_results(out_dir, summaries)
    print("Aggregate written:", agg)

if __name__ == "__main__":
    main()
