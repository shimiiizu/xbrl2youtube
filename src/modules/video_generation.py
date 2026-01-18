from moviepy import (
    AudioFileClip,
    ColorClip,
    TextClip,
    CompositeVideoClip
)
from pathlib import Path
import os


def generate_video(audio_path: str, output_path: str, text_content: str = None) -> None:
    print(f"[INFO] Reading audio from: {audio_path}")

    if os.path.exists(output_path):
        os.remove(output_path)

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    background = ColorClip(
        size=(1280, 720),
        color=(0, 0, 0),
        duration=duration
    )

    clips = [background]

    if text_content:
        # タイトル
        title_clip = TextClip(
            text="決算サマリー",
            font="IPAexMincho",
            font_size=40,
            color="white",
            size=(1280, 80),
            method="caption"
        ).with_position(("center", 20)).with_duration(duration)

        clips.append(title_clip)

        # 本文（縦に長いテキスト）
        body_clip = TextClip(
            text=text_content,
            font="IPAexMincho",
            font_size=26,
            color="white",
            size=(1200, 2000),
            method="caption",
            align="West"
        ).with_duration(duration)

        # ★ 自前スクロール（最重要）
        start_y = 720
        end_y = 120

        body_clip = body_clip.with_position(
            lambda t: ("center", start_y - (start_y - end_y) * (t / duration))
        )

        clips.append(body_clip)

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

    video.close()
    audio.close()
    background.close()

    print(f"[INFO] Video saved to: {output_path}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    test_audio = project_root / "data" / "processed" / "output.mp3"
    test_text = project_root / "data" / "processed" / "extracted_text.txt"
    test_output = project_root / "data" / "processed" / "output.mp4"

    text_content = None
    if test_text.exists():
        with open(test_text, "r", encoding="utf-8") as f:
            text_content = f.read()

    generate_video(
        audio_path=str(test_audio),
        output_path=str(test_output),
        text_content=text_content
    )
