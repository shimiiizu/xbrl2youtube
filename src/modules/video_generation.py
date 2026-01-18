from moviepy import (
    AudioFileClip,
    ColorClip,
    TextClip,
    CompositeVideoClip
)
from pathlib import Path
import os

# ===== 日本語フォント（Pillow確実対応）=====
FONT_PATH = r"C:\Windows\Fonts\ipam.ttf"


def generate_video(audio_path: str, output_path: str, text_content: str = None) -> None:
    """
    音声ファイルから動画ファイルを生成する
    （黒背景 + 音声 + 日本語タイトル + 日本語本文スクロール）
    """

    print(f"[INFO] Reading audio from: {audio_path}")

    # Windows対策：既存ファイル削除
    if os.path.exists(output_path):
        os.remove(output_path)

    # 音声読み込み
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    print(f"[INFO] Audio duration: {duration:.2f} seconds")

    # 背景
    background = ColorClip(
        size=(1280, 720),
        color=(0, 0, 0),
        duration=duration
    )

    clips = [background]

    if text_content:
        print("[INFO] Adding title and scrolling text...")

        # ===== タイトル（固定）=====
        title_clip = TextClip(
            text="決算サマリー",
            font=FONT_PATH,
            font_size=40,
            color="white",
            size=(1280, 80),
            method="caption"
        ).with_position(("center", 20)).with_duration(duration)

        clips.append(title_clip)

        # ===== 本文（縦に長いテキスト）=====
        body_clip = TextClip(
            text=text_content,
            font=FONT_PATH,
            font_size=26,
            color="white",
            size=(1200, 2000),  # 縦長に取る
            method="caption"
        ).with_duration(duration)

        # ===== 自前スクロール（MoviePy互換・最安定）=====
        start_y = 720
        end_y = 120

        body_clip = body_clip.with_position(
            lambda t: (
                "center",
                start_y - (start_y - end_y) * (t / duration)
            )
        )

        clips.append(body_clip)

    # 合成 + 音声
    video = CompositeVideoClip(clips).with_audio(audio)

    print("[INFO] Writing video file...")
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )

    # ===== 後処理（超重要）=====
    video.close()
    audio.close()
    background.close()

    print(f"[INFO] Video saved to: {output_path}")


if __name__ == "__main__":
    # ===== デバッグ実行用 =====
    project_root = Path(__file__).parent.parent.parent

    test_audio = project_root / "data" / "processed" / "output.mp3"
    test_text = project_root / "data" / "processed" / "extracted_text.txt"
    test_output = project_root / "data" / "processed" / "output.mp4"

    print("=" * 50)
    print("動画生成テスト開始")
    print("=" * 50)

    text_content = None
    if test_text.exists():
        with open(test_text, "r", encoding="utf-8") as f:
            text_content = f.read()
        print(f"[INFO] テキスト読み込み: {len(text_content)} 文字")

    generate_video(
        audio_path=str(test_audio),
        output_path=str(test_output),
        text_content=text_content
    )

    print("=" * 50)
    print("動画生成完了")
    print(f"出力ファイル: {test_output}")
    print("=" * 50)
