import subprocess
import os
from sendTelegramNotification import send_telegram
# from dotenv import load_dotenv
# load_dotenv()

print(" STARTING PIPELINE")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTBOX = os.path.abspath(
    os.path.join(BASE_DIR,"ai-video-generator", "src", "output_clips")
)


def has_videos(folder):
    if not os.path.exists(folder):
        return False
    return any(f.lower().endswith(".mp4") for f in os.listdir(folder))


def run_once():
    try:
        send_telegram("🚀 GitHub pipeline started")

        print(" Step 1: Generating video")
        
        result = subprocess.run(
            ["python", "run.py"],
            cwd="ai-video-generator",
            capture_output=True,
            text=True,
        )

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        # 👉 Always upload ONE video (your uploader handles 1-by-1)
        print(" Step 2: Uploading video")

        result2 = subprocess.run(
            ["python", "-m", "src.watch_and_upload"],
            cwd="ai-video-uploader",
            capture_output=True,
            text=True,
        )

        print("STDOUT:", result2.stdout)
        print("STDERR:", result2.stderr)

        if result2.returncode != 0:
            raise Exception("Upload failed")

        print("Upload step completed")
        send_telegram("✅ Video uploaded successfully!")

    except Exception as e:
        print("")
        send_telegram(f"❌ PIPELINE FAILED\n\n{str(e)[:1000]}")


if __name__ == "__main__":
    run_once()