# uploader/watch_and_upload.py
import os
import re
from .upload_video import upload_to_youtube

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTBOX = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..", "ai-video-generator", "src", "output_clips")
)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def find_video_file(folder_path):
    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mp4")]

    if not mp4_files:
        return None

    def extract_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    mp4_files.sort(key=extract_number)

    return os.path.join(folder_path, mp4_files[0])

def find_script(folder_path):
    for file in os.listdir(folder_path):
        if file.lower().endswith(".txt"):
            return os.path.join(folder_path, file)
    return None


def run():
    print("OUTBOX path:", OUTBOX)
    print("Exists:", os.path.exists(OUTBOX))
    print("Contents:", os.listdir(OUTBOX) if os.path.exists(OUTBOX) else "N/A")

    if not os.path.exists(OUTBOX):
        print(" OUTBOX folder does not exist")
        return

    video_path = find_video_file(OUTBOX)
    script_path = find_script(OUTBOX)

    if not video_path:
        print("No .mp4 file found in OUTBOX")
        return

    print(f"Uploading video: {os.path.basename(video_path)}")
    video_id = upload_to_youtube(video_path,script_path)
    print(f"Uploaded -> video_id={video_id}")

    if video_id:
        os.remove(video_path)
        print(f" Uploaded and deleted: {video_path}")
    else:
        print(f" Failed upload: {video_path}")

if __name__ == "__main__":
    run()
