# src/modules/video_generation.py

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from pathlib import Path
import os

FONT_PATH = r"C:\Windows\Fonts\ipam.ttf"


def generate_thumbnail(output_path: str, company_name: str | None = None) -> None:
    """動画用のカスタムサムネイルを生成"""

    print("[INFO] Generating thumbnail...")

    # タイトルテキスト作成
    if company_name:
        title_text = f"{company_name}\n決算サマリー"
    else:
        title_text = "決算サマリー"

    # サムネイルのサイズ（YouTube推奨: 1280x720）
    thumb_size = (1280, 720)

    # 背景（グラデーション風に濃いめの色）
    background = ColorClip(size=thumb_size, color=(20, 30, 50)).with_duration(1)

    # タイトル（大きく中央に）
    title_clip = (
        TextClip(
            text=title_text,
            font=FONT_PATH,
            font_size=90,  # かなり大きく
            color="white",
            size=(1100, None),
            method="caption"
        )
        .with_duration(1)
        .with_position("center")
    )

    # 合成
    thumbnail = CompositeVideoClip([background, title_clip])

    # 最初のフレームを画像として保存
    thumbnail_path = output_path.replace(".mp4", "_thumbnail.png")
    thumbnail.save_frame(thumbnail_path, t=0)

    print(f"[INFO] Thumbnail saved to: {thumbnail_path}")


def generate_video(audio_path: str, output_path: str, text_content: str | None = None,
                   company_name: str | None = None) -> None:
    print(f"[INFO] Reading audio from: {audio_path}")

    # ===== フォント存在チェック（重要）=====
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    print(f"[INFO] Audio duration: {duration:.2f} seconds")
    print("[INFO] Adding title and body text (simultaneous)")

    # ===== 背景 =====
    background = (
        ColorClip(size=(1280, 720), color=(0, 0, 0))
        .with_duration(duration)
    )

    clips = [background]

    # ===== タイトル（即時表示）=====
    # タイトルテキスト作成
    if company_name:
        title_text = f"{company_name} 決算サマリー"
    else:
        title_text = "決算サマリー"

    title_clip = (
        TextClip(
            text=title_text,
            font=FONT_PATH,
            font_size=48,
            color="white",
            size=(1200, None),
            method="caption"
        )
        .with_start(0)
        .with_duration(duration)
        .with_position(("center", 20))
    )

    clips.append(title_clip)

    # ===== 本文（即時表示）=====
    if text_content:
        body_clip = (
            TextClip(
                text=text_content,
                font=FONT_PATH,
                font_size=13,
                color="white",
                size=(1100, None),
                method="caption"
            )
            .with_start(0)
            .with_duration(duration)
            .with_position((90, 120))
        )

        clips.append(body_clip)

    # ===== 合成 & 音声 =====
    video = CompositeVideoClip(clips).with_audio(audio)

    print("[INFO] Writing video file...")

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    print(f"[INFO] Video saved to: {output_path}")

    # ===== サムネイル生成 =====
    generate_thumbnail(output_path, company_name=company_name)


# ===== デバッグ実行 =====
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent

    test_audio = project_root / "data" / "processed" / "output.mp3"
    test_text = project_root / "data" / "processed" / "extracted_text.txt"
    test_output = project_root / "data" / "processed" / "output.mp4"

    print("=" * 50)
    print("動画生成テスト開始")
    print("=" * 50)

    text_content = None
    if test_text.exists():
        text_content = test_text.read_text(encoding="utf-8")
        print(f"[INFO] テキスト読み込み: {len(text_content)} 文字")

    generate_video(
        audio_path=str(test_audio),
        output_path=str(test_output),
        text_content=text_content,
        company_name="トヨタ自動車"  # テスト用の企業名
    )

    print("=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)