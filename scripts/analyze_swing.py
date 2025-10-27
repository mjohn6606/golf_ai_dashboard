#!/usr/bin/env python3
# analyze_swing.py - OpenCV + MediaPipe pose analyzer
# Usage: python analyze_swing.py --video swing.mp4 --out annotated.mp4 --json out.json
import argparse, json
import cv2, mediapipe as mp, numpy as np
mp_pose = mp.solutions.pose
def angle(a,b,c):
    ba = a - b; bc = c - b
    cosang = np.dot(ba, bc) / (np.linalg.norm(ba)*np.linalg.norm(bc)+1e-8)
    return np.degrees(np.arccos(np.clip(cosang, -1,1)))
def analyze(video_path, out_video, out_json, max_frames=None):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames_out = []
    results_list = []
    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret: break
            idx += 1
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(image)
            h,w,_ = frame.shape
            if res.pose_landmarks:
                lm = res.pose_landmarks.landmark
                left_sh = np.array([lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x*w, lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y*h])
                right_sh = np.array([lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x*w, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y*h])
                left_hip = np.array([lm[mp_pose.PoseLandmark.LEFT_HIP].x*w, lm[mp_pose.PoseLandmark.LEFT_HIP].y*h])
                right_hip = np.array([lm[mp_pose.PoseLandmark.RIGHT_HIP].x*w, lm[mp_pose.PoseLandmark.RIGHT_HIP].y*h])
                shoulder_angle = angle(left_sh, (left_sh+right_sh)/2, right_sh)
                hip_angle = angle(left_hip, (left_hip+right_hip)/2, right_hip)
                results_list.append({'frame': idx, 'shoulder_angle': round(float(shoulder_angle),2), 'hip_angle': round(float(hip_angle),2)})
                for lmpt in res.pose_landmarks.landmark:
                    x = int(lmpt.x * w); y = int(lmpt.y * h)
                    cv2.circle(frame, (x,y), 2, (0,255,0), -1)
                cv2.putText(frame, f"Sh:{shoulder_angle:.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255),2)
            frames_out.append(frame)
            if max_frames and idx>=max_frames: break
    cap.release()
    height, width, _ = frames_out[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_video, fourcc, fps, (width, height))
    for f in frames_out:
        out.write(f)
    out.release()
    arr = np.array([[r['shoulder_angle'], r['hip_angle']] for r in results_list])
    summary = {
        'frames': len(results_list),
        'shoulder_mean': float(np.nanmean(arr[:,0])) if arr.size else None,
        'hip_mean': float(np.nanmean(arr[:,1])) if arr.size else None,
        'raw': results_list[:200],
    }
    with open(out_json, 'w') as jf:
        json.dump(summary, jf, indent=2)
    print('Wrote', out_video, out_json)
if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--video', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--json', required=True)
    p.add_argument('--maxframes', type=int, default=0)
    args = p.parse_args()
    analyze(args.video, args.out, args.json, max_frames=(args.maxframes or None))
