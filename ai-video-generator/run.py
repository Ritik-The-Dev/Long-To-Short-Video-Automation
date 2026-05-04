import os
from src.fetchVideo import fetch_or_resume_video
from src.clipShorts import process_next_clip


def main():
    try:
        # 🔹 Step 1: Get video (resume OR new)
        video_id, _ = fetch_or_resume_video()

        if not video_id:
            print("⚠️ No video available")
            return

        # 🔹 Step 2: Process next 60-sec clip
        done = process_next_clip(video_id)

        if done:
            print("🎉 Video completed, ready for next")

    except Exception as e:
        print("💥 Pipeline crashed:", str(e))


if __name__ == "__main__":
    main()