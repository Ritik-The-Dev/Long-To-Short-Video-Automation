import os
import time
import yt_dlp
from pytubefix import YouTube

CHANNEL_URL = "https://www.youtube.com/@AnokhiFilms10/videos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data")
output_path = os.path.join(BASE_DIR, "output_clips")
video_path = os.path.join(BASE_DIR, "videos")

os.makedirs(folder_path, exist_ok=True)
os.makedirs(video_path, exist_ok=True)
os.makedirs(output_path, exist_ok=True)


# -----------------------------
# 🔹 Downloader 1: pytubefix
# -----------------------------
def download_pytube(video_url, vid):
    try:
        yt = YouTube(video_url)

        stream = yt.streams.filter(
            progressive=True, file_extension="mp4"
        ).order_by("resolution").desc().first()

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
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)

        return True, {
            "title": info.get("title", "no_title"),
            "description": info.get("description", "")
        }

    except Exception as e:
        return False, str(e)


# -----------------------------
# 🔹 Main pipeline
# -----------------------------
def fetchVideo():

    fetchedList = set()
    listPath = os.path.join(folder_path, "fetchedList.txt")

    if os.path.exists(listPath):
        with open(listPath, "r") as f:
            fetchedList = set(f.read().splitlines())

    # 🔹 use yt-dlp ONLY for listing
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)

    videos = info.get("entries", [])

    videos = sorted(
        videos,
        key=lambda x: int(x.get("upload_date") or 0),
        reverse=True
    )

    for v in videos:
        vid = v.get("id")
        title = v.get("title", vid)

        if not vid or vid in fetchedList:
            continue

        video_url = f"https://www.youtube.com/watch?v={vid}"
        print(f"\nProcessing: {title}")

        # -----------------------------
        # 🔥 STEP 1: pytube attempt
        # -----------------------------
        success, result = download_pytube(video_url, vid)

        if success:
            print(" Downloaded via pytubefix")

        else:
            print(" pytubefix failed:", result)

            # -----------------------------
            # 🔥 STEP 2: yt-dlp fallback
            # -----------------------------
            success, result = download_ytdlp(video_url, vid)

            if success:
                print(" Downloaded via yt-dlp fallback")
            else:
                print(" Both downloaders failed → skipping")
                continue  # 🔥 KEY: skip instead of crash

        # -----------------------------
        # Save metadata
        # -----------------------------
        meta_path = os.path.join(output_path, "metaData.txt")

        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE:\n{result['title']}\n\n")
            f.write(f"DESCRIPTION:\n{result['description']}\n")

        # mark as processed
        with open(listPath, "a") as f:
            f.write(vid + "\n")

        return vid, listPath

    print(" No usable videos found")
    return None, listPath