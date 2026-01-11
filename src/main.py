# src/main.py

from text_extraction import extract_text_from_xbrl
from audio_generation import generate_audio
from video_generation import generate_video
from youtube_upload import upload_to_youtube


def main():
    # 入出力パス
    xbrl_path = "../data/sample.xbrl"
    audio_path = "../data/processed/output.mp3"
    video_path = "../data/processed/output.mp4"

    # 1. XBRL → テキスト
    text = extract_text_from_xbrl(xbrl_path)

    # 2. テキスト → 音声
    generate_audio(text, audio_path)

    # 3. 音声 → 動画
    generate_video(audio_path, video_path)

    # 4. YouTubeへアップロード
    upload_to_youtube(video_path)


if __name__ == "__main__":
    main()
