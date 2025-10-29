import time
import os
from supabase import create_client, Client
from process_swing_videos import analyze_swing, update_supabase
from analyze_mobility import fetch_swing_data, compute_mobility_metrics, update_mobility_summary

SUPABASE_URL = "https://cqlsovoiowdtfukotgdu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxbHNvdm9pb3dkdGZ1a290Z2R1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE3MzMxOTYsImV4cCI6MjA3NzMwOTE5Nn0.5G4tUhd8f0M_L5Xmtknw222VTMsfAh-O4sQ0VnVXFyk"  # service role key allows RLS bypass for backend automation
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_new_videos():
    """Check Supabase storage for unprocessed videos"""
    result = supabase.table("swing_videos").select("*").eq("processed", False).execute()
    return result.data

def mark_video_processed(video_id):
    supabase.table("swing_videos").update({"processed": True}).eq("id", video_id).execute()

def main():
    print("🔁 Supabase Listener started...")
    while True:
        videos = check_new_videos()
        if videos:
            for vid in videos:
                video_file = vid["video"]
                video_path = os.path.join("data/videos_to_process", video_file)

                # If not downloaded yet, pull from Supabase Storage
                if not os.path.exists(video_path):
                    storage_file = supabase.storage.from_("videos").download(video_file)
                    with open(video_path, "wb") as f:
                        f.write(storage_file)

                print(f"🎥 Processing {video_file} ...")
                metrics = analyze_swing(video_path)
                update_supabase(video_file, metrics)
                mark_video_processed(vid["id"])
                print(f"✅ Completed {video_file}")

            # Update mobility summary after each batch
            df = fetch_swing_data()
            summary = compute_mobility_metrics(df)
            update_mobility_summary(summary)
            print("📊 Mobility summary updated.")
        else:
            print("⏸️ No new videos detected.")

        time.sleep(60)  # check every minute

if __name__ == "__main__":
    main()
