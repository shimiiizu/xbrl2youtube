# src/main.py

from modules.text_extraction import extract_text_from_xbrl, save_text
from modules.audio_generation import generate_audio
from modules.video_generation import generate_video
from modules.youtube_upload import upload_to_youtube


def main():
    xbrl_path = "../data/qualitative.htm"
    text_path = "../data/processed/extracted_text.txt"
    audio_path = "../data/processed/output.mp3"
    video_path = "../data/processed/output.mp4"

    # 1. XBRL → テキスト抽出
    text = extract_text_from_xbrl(xbrl_path)

    # 2. テキストをファイルに保存
    save_text(text, text_path)

    # 3. テキストファイル → 音声
    generate_audio(text_path, audio_path)

    # 4. 音声 → 動画
    generate_video(audio_path, video_path)

    # 5. YouTubeへアップロード
    upload_to_youtube(video_path)


if __name__ == "__main__":
    main()