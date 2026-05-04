import yt_dlp
import os
import time

CHANNEL_URL = "https://www.youtube.com/@AnokhiFilms10/videos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data")
output_path = os.path.join(BASE_DIR, "output_clips")
video_path = os.path.join(BASE_DIR, "videos")

os.makedirs(folder_path, exist_ok=True)
os.makedirs(video_path, exist_ok=True)
os.makedirs(output_path, exist_ok=True)

def fetchVideo():

    fetchedList = set()

    listPath = os.path.join(folder_path, "fetchedList.txt")
    if os.path.exists(listPath):
        with open(listPath, "r") as f:
            fetchedList = set(f.read().splitlines())

    # ✅ STEP 1: get video list (no extract_flat → ensures timestamp exists)
    ydl_options = {
        "quiet": True,
        "extract_flat": True 
    }

    with yt_dlp.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(CHANNEL_URL, download=False)

    videos = info.get("entries", [])

    # ✅ Sort latest → oldest (robust, not relying on YouTube order)
    videos = sorted(
        videos,
        key=lambda x: int(x.get("upload_date") or 0),
        reverse=True
    )

    next_video = None
    for v in videos:
        vid = v.get("id")
        title = v.get("title", vid)

        if vid and vid not in fetchedList:
            next_video = (title, vid)
            break

    if not next_video:
        print("✅ No new videos left")
        return None, listPath

    title, vid = next_video
    print("🎬 Processing Video:", title)

    # ✅ STEP 2: yt-dlp options (highest quality, stable merging)
    ydl_opts = {
        "outtmpl": os.path.join(video_path, "%(id)s.%(ext)s"),

        # safer format (less suspicious than bv*+ba sometimes)
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",

        "merge_output_format": "mp4",

        # subtitles
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["hi"],
        "subtitlesformat": "srt",

        # mimic real browser
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        },

        # VERY IMPORTANT
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },

        # reduce bot suspicion
        "sleep_interval": 5,
        "max_sleep_interval": 10,
        "retries": 3,
        "fragment_retries": 3,

        # stability
        "noplaylist": True,
    }
    # 🍪 Use cookies if available
    cookie_path = os.path.join(BASE_DIR, "data", "cookies.txt")
    
    print("Cookie exists:", os.path.exists(cookie_path))
    
    if os.path.exists(cookie_path):
        ydl_opts["cookies"] = cookie_path
        ydl_opts["cookiefile"] = cookie_path
        print("🍪 Using cookies")

    # ✅ STEP 3: retry logic
    for attempt in range(3):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={vid}",
                    download=True
                )

            # ✅ Get full metadata
            title = info.get("title", "no_title")
            description = info.get("description", "")

            print("✅ Video downloaded:", vid)
            print("📌 Title:", title)

            # ✅ Save metadata to file
            meta_path = os.path.join(output_path, f"metaData.txt")
            with open(meta_path, "w", encoding="utf-8") as f:
                f.write(f"TITLE:\n{title}\n\n")
                f.write(f"DESCRIPTION:\n{description}\n")

            # ✅ Save to fetched list
            with open(listPath, "a") as f:
                f.write(vid + "\n")

            return vid, listPath

        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed:", str(e))

            if attempt < 2:
                print("⏳ Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("🚫 Failed after retries")
                raise