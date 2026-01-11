# src/main.py（現在のコードのまま）

from modules.text_extraction import extract_text_from_xbrl
from modules.audio_generation import generate_audio
from modules.video_generation import generate_video
from modules.youtube_upload import upload_to_youtube


def main():
    xbrl_path = "../data/sample.xbrl"
    audio_path = "../data/processed/output.mp3"
    video_path = "../data/processed/output.mp4"

    text = extract_text_from_xbrl(xbrl_path)
    generate_audio(text, audio_path)
    generate_video(audio_path, video_path)
    upload_to_youtube(video_path)


if __name__ == "__main__":
    main()