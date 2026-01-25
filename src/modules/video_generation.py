# src/modules/video_generation.py

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from pathlib import Path
import os

FONT_PATH = r"C:\Windows\Fonts\ipam.ttf"


def generate_thumbnail(output_path: str, company_name: str = None) -> None:
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
            font_size=90,
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


def generate_video(audio_path: str, output_path: str, text_content: str = None,
                   company_name: str = None) -> None:
    print(f"[INFO] Reading audio from: {audio_path}")

    # ===== フォント存在チェック（重要）=====
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    print(f"[INFO] Audio duration: {duration:.2f} seconds")
    print("[INFO] Creating video with scrolling text")

    # ===== 背景 =====
    background = (
        ColorClip(size=(1280, 720), color=(0, 0, 0))
        .with_duration(duration)
    )

    clips = [background]

    # ===== タイトル（固定表示）=====
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

    # ===== 本文（スクロール表示）=====
    if text_content:
        # フォントサイズを大きく（13 → 24）
        body_clip = (
            TextClip(
                text=text_content,
                font=FONT_PATH,
                font_size=30,  # フォントサイズを大きく
                color="white",
                size=(1100, None),
                method="caption"
            )
            .with_start(0)
            .with_duration(duration)
        )

        # テキストの高さを取得
        text_height = body_clip.h
        screen_height = 720
        scroll_area_top = 100  # タイトルの下
        scroll_area_bottom = 720  # 画面下端
        scroll_area_height = scroll_area_bottom - scroll_area_top

        # スクロール速度を計算（画面外から画面外まで移動）
        # 開始位置: 画面下端、終了位置: テキスト全体が画面上に消える位置
        start_y = screen_height-100
        end_y = scroll_area_top - text_height

        # スクロール距離
        scroll_distance = start_y - end_y

        # スクロール関数: 時間に応じてY座標を変化
        def scroll_position(t):
            # t: 現在の時間（0 ~ duration）
            # 線形にスクロール
            progress = t / duration  # 0.0 ~ 1.0
            current_y = start_y - (scroll_distance * progress)
            return ("center", current_y)

        # スクロール適用
        body_clip = body_clip.with_position(scroll_position)

        clips.append(body_clip)

        print(f"[INFO] Text height: {text_height}px")
        print(f"[INFO] Scroll distance: {scroll_distance}px")
        print(f"[INFO] Scroll speed: {scroll_distance / duration:.2f}px/sec")

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

    # リソースのクリーンアップ
    audio.close()
    video.close()


# ===== デバッグ実行 =====
if __name__ == "__main__":
    # ===== ここを変更するだけで企業を切り替え可能 =====
    COMPANY_NAME = "ヒガシＨＤ"
    # =============================================

    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data" / "processed"

    # 企業名から各ファイルパスを自動生成
    test_audio = processed_dir / f"{COMPANY_NAME}_audio.mp3"
    test_text = processed_dir / f"{COMPANY_NAME}_extracted_text.txt"
    test_subtitle = processed_dir / f"{COMPANY_NAME}_subtitle.srt"
    test_output = processed_dir / f"{COMPANY_NAME}_video.mp4"

    print("=" * 50)
    print(f"動画生成テスト開始: {COMPANY_NAME}")
    print("=" * 50)

    # ファイル存在確認
    print(f"[CHECK] 音声ファイル: {test_audio.exists()}")
    print(f"[CHECK] テキストファイル: {test_text.exists()}")
    print(f"[CHECK] 字幕ファイル: {test_subtitle.exists()}")

    text_content = None
    if test_text.exists():
        text_content = test_text.read_text(encoding="utf-8")
        print(f"[INFO] テキスト読み込み: {len(text_content)} 文字")
    else:
        print(f"[WARNING] テキストファイルが見つかりません: {test_text}")

    # 字幕ファイルの確認
    if test_subtitle.exists():
        print(f"[INFO] 字幕ファイル検出: {test_subtitle}")
    else:
        print(f"[INFO] 字幕ファイルなし（スクロールテキストのみ）")

    generate_video(
        audio_path=str(test_audio),
        output_path=str(test_output),
        text_content=text_content,
        company_name=COMPANY_NAME
    )

    print("=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)