import os
import json
import yt_dlp
from pytubefix import YouTube

CHANNEL_URL = "https://www.youtube.com/@AnokhiFilms10/videos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data")
output_path = os.path.join(BASE_DIR, "output_clips")
video_path = os.path.join(BASE_DIR, "videos")

PROGRESS_FILE = os.path.join(folder_path, "video_progress.json")

os.makedirs(folder_path, exist_ok=True)
os.makedirs(video_path, exist_ok=True)
os.makedirs(output_path, exist_ok=True)


# -----------------------------
# 🔹 Downloader 1: pytubefix
# -----------------------------
def download_pytube(video_url, vid):
    try:
        yt = YouTube(video_url, 'WEB')

        stream = yt.streams.get_highest_resolution()

        if not stream:
            return False, "No progressive stream"

        file_path = stream.download(output_path=video_path, filename=f"{vid}.mp4")

        return True, {
            "title": yt.title,
            "description": yt.description,
            "file_path": file_path
        }

    except Exception as e:
        return False, str(e)


# -----------------------------
# 🔹 Downloader 2: yt-dlp fallback
# -----------------------------
def download_ytdlp(video_url, vid):
    try:
        ydl_opts = {
            "outtmpl": os.path.join(video_path, f"{vid}.%(ext)s"),
            "format": "best[ext=mp4]/mp4",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
              # 🔥 CRITICAL
            "cookiefile": os.path.join(BASE_DIR, "data", "cookies.txt"),

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },

            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

        return True, {
            "title": info.get("title", "no_title"),
            "description": info.get("description", ""),
            "file_path": os.path.join(video_path, f"{vid}.mp4")
        }

    except Exception as e:
        return False, str(e)


# -----------------------------
# 🔥 MAIN FUNCTION
# -----------------------------
def fetch_or_resume_video():

    listPath = os.path.join(folder_path, "fetchedList.txt")

    # 🔁 Resume existing video
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)

        vid = progress["video_id"]
        print(f" Resuming video: {vid}")

        return vid, listPath

    # 🔹 Load fetched list
    fetchedList = set()
    if os.path.exists(listPath):
        with open(listPath, "r") as f:
            fetchedList = set(f.read().splitlines())

    # 🔹 Fetch channel videos
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)

    videos = sorted(
        info.get("entries", []),
        key=lambda x: int(x.get("upload_date") or 0),
        reverse=True
    )

    # 🔥 Find next usable video
    for v in videos:
        vid = v.get("id")
        title = v.get("title", vid)

        if not vid or vid in fetchedList:
            continue

        video_url = f"https://www.youtube.com/watch?v={vid}"
        print(f"\ Fetching NEW video: {title}")

        # 🔥 Try pytube first
        success, result = download_pytube(video_url, vid)

        if success:
            print(" Downloaded via pytubefix")
        else:
            print("pytubefix failed:", result)

            # fallback
            success, result = download_ytdlp(video_url, vid)

            if success:
                print(" Downloaded via yt-dlp fallback")
            else:
                print("Both downloaders failed → skipping")
                break

        # ✅ Save metadata
        meta_path = os.path.join(output_path, "metaData.txt")

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE:\n{result['title']}\n\n")
            f.write(f"DESCRIPTION:\n{result['description']}\n")

        # 🔥 Initialize progress
        progress = {
            "video_id": vid,
            "current_time": 0,
            "duration": None
        }

        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f)

        return vid, listPath

    print(" No usable videos found")
    return None, listPath