from src.fetchVideo import fetchVideo
from src.clipShorts import process_video

def main():
    try:
        videoId, listPath = fetchVideo()
        process_video()
        with open(listPath, "a") as f:
            f.write(videoId + "\n")
        print("Done!")
        
    except Exception as e:
        print("Pipeline crashed:", str(e))


if __name__ == "__main__":
    main()