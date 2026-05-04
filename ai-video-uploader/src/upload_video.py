from googleapiclient.http import MediaFileUpload
from .auth import get_youtube_client


def parse_script_txt(script_path):
    title = None
    description_lines = []

    with open(script_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    mode = None

    for line in lines:
        line = line.strip()

        if line.upper().startswith("TITLE:"):
            mode = "title"
            continue
        elif line.upper().startswith("DESCRIPTION:"):
            mode = "description"
            continue

        if mode == "title" and line:
            # first non-empty line after TITLE:
            if not title:
                title = line

        elif mode == "description":
            description_lines.append(line)

    description = "\n".join(description_lines).strip()

    return title, description


def upload_to_youtube(video_path: str, script_path: str) -> str:
    youtube = get_youtube_client()

    title, description = parse_script_txt(script_path)

    # fallback safety
    if not title:
        title = "Amazing Food Stories"
    if not description:
        description = "Amazing Food Stories || Story Behind Foods #shorts"

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            video_path,
            resumable=True,
            chunksize=-1
        ),
    )

    response = request.execute()
    return response["id"]