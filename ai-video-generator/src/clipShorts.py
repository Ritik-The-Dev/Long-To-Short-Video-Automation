import os
import json
from moviepy.editor import VideoFileClip

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_clips")
DATA_DIR = os.path.join(BASE_DIR, "data")

PROGRESS_FILE = os.path.join(DATA_DIR, "video_progress.json")
FETCHED_LIST = os.path.join(DATA_DIR, "fetchedList.txt")

CLIP_DURATION = 60


def convert_to_portrait(clip):
    w, h = clip.size
    target_ratio = 9 / 16

    new_width = min(int(h * target_ratio), w)

    x_center = w // 2
    x1 = max(0, x_center - new_width // 2)
    x2 = min(w, x_center + new_width // 2)

    cropped = clip.crop(x1=x1, x2=x2)
    return cropped.resize((720, 1280))


# 🔥 REMOVED TextClip → no ImageMagick dependency


def process_next_clip(video_id):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(PROGRESS_FILE):
        raise Exception("No progress file found")

    with open(PROGRESS_FILE, "r") as f:
        progress = json.load(f)

    video_path = os.path.join(VIDEO_DIR, f"{video_id}.mp4")

    # 🔥 Graceful handling instead of crash
    if not os.path.exists(video_path):
        raise Exception("Video not found → fetch step failed")

    video = VideoFileClip(video_path)

    # initialize duration once
    if progress["duration"] is None:
        progress["duration"] = video.duration

    start = progress["current_time"]
    remaining = video.duration - start

    if remaining <= 0:
        print("⚠️ No remaining content")
        return True

    end = min(start + CLIP_DURATION, video.duration)

    part_no = int(start / CLIP_DURATION) + 1

    print(f"✂️ Creating clip {part_no}: {start} → {end}")

    subclip = video.subclip(start, end)
    subclip = convert_to_portrait(subclip)

    output_path = os.path.join(OUTPUT_DIR, "1.mp4")

    subclip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        logger=None  # cleaner logs
    )

    subclip.close()
    video.close()

    # 🔁 update progress
    progress["current_time"] = end  # 🔥 FIX (not += 60 blindly)

    # 🔥 FINISHED VIDEO
    if progress["current_time"] >= progress["duration"]:
        print("✅ Video fully processed")

        # mark as completed
        with open(FETCHED_LIST, "a") as f:
            f.write(video_id + "\n")

        # cleanup
        if os.path.exists(video_path):
            os.remove(video_path)

        os.remove(PROGRESS_FILE)

        return True

    # save progress
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

    return False