from moviepy import (
    AudioFileClip,
    ColorClip,
    TextClip,
    CompositeVideoClip
)
from moviepy.video.fx import scroll
from pathlib import Path
import os


def generate_video(audio_path: str, output_path: str, text_content: str = None) -> None:
    """
    音声ファイルから動画ファイルを生成する（静止画 + 音声 + 日本語テキスト）

    Args:
        audio_path: 音声ファイルのパス（MP3）
        output_path: 出力する動画ファイルのパス（MP4）
        text_content: 表示するテキスト
    """

    print(f"[INFO] Reading audio from: {audio_path}")

    # 既存ファイルがあれば削除（Windows対策）
    if os.path.exists(output_path):
        os.remove(output_path)

    # 音声読み込み
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    print(f"[INFO] Audio duration: {duration:.2f} seconds")

    # 背景（黒）
    background = ColorClip(
        size=(1280, 720),
        color=(0, 0, 0),
        duration=duration
    )

    clips = [background]

    if text_content:
        print("[INFO] Adding title and scrolling text...")

        # ========= タイトル（固定表示） =========
        title_clip = TextClip(
            text="決算サマリー",
            font="IPAexMincho",   # ← ipaexm.ttf
            font_size=40,
            color="white",
            size=(1280, 80),
            method="caption"
        ).with_position(("center", 20)).with_duration(duration)

        clips.append(title_clip)

        # ========= 本文（スクロール表示） =========
        body_clip = TextClip(
            text=text_content,
            font="IPAexMincho",
            font_size=26,
            color="white",
            size=(1200, 2000),    # 縦に長く取る
            method="caption",
            align="West"
        ).with_duration(duration)

        body_clip = body_clip.fx(
            scroll,
            w=1200,
            h=520,
            x_center=640,
            y_start=720,
            y_end=120,
            duration=duration
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

    # ===== close（超重要）=====
    video.close()
    audio.close()
    background.close()

    print(f"[INFO] Video saved to: {output_path}")


if __name__ == "__main__":
    # ===== デバッグ用 =====
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
