import os
import math
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def convert_to_portrait(clip):
    w, h = clip.size
    target_ratio = 9 / 16

    new_width = min(int(h * target_ratio), w)

    x_center = w // 2
    x1 = max(0, x_center - new_width // 2)
    x2 = min(w, x_center + new_width // 2)

    cropped = clip.crop(x1=x1, x2=x2)
    return cropped.resize((720, 1280))


def add_title(clip, part_no):
    txt = TextClip(
        f"Part {part_no}",
        fontsize=60,
        color="white",
        method="caption",
        size=(720, 100)
    ).set_position(("center", "top")).set_duration(clip.duration)

    return CompositeVideoClip([clip, txt])


def process_video():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    VIDEO_DIR = os.path.join(BASE_DIR, "videos")
    OUTPUT_DIR = os.path.join(BASE_DIR, "output_clips")

    mp4_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
    if not mp4_files:
        raise Exception("No MP4 video found in src/videos")

    mp4_paths = [os.path.join(VIDEO_DIR, f) for f in mp4_files]
    INPUT_VIDEO = max(mp4_paths, key=os.path.getmtime)

    CLIP_DURATION = 60

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    video = VideoFileClip(INPUT_VIDEO)

    total_duration = video.duration
    num_clips = math.ceil(total_duration / CLIP_DURATION)

    for i in range(num_clips):
        start = i * CLIP_DURATION
        end = min((i + 1) * CLIP_DURATION, total_duration)

        subclip = video.subclip(start, end)
        subclip = convert_to_portrait(subclip)
        subclip = add_title(subclip, i + 1)

        output_path = os.path.join(OUTPUT_DIR, f"{i+1}.mp4")

        subclip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=video.fps
        )

        subclip.close()

    video.close()

    # cleanup videos folder
    for file in os.listdir(VIDEO_DIR):
        file_path = os.path.join(VIDEO_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    print("Done! Clips created successfully.")


if __name__ == "__main__":
    process_video()