# src/modules/video_generation.py

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from pathlib import Path
import os

FONT_PATH = r"C:\Windows\Fonts\YuGothB.ttc"


def generate_thumbnail(output_path: str, company_name: str = None, date_str: str = None,
                       duration: float = 3.0, stock_info: dict = None) -> str:
    """動画用のオープニング映像（サムネイル）を生成

    Args:
        output_path: 出力動画ファイルのパス
        company_name: 企業名
        date_str: 日付文字列
        duration: オープニングの長さ（秒）
        stock_info: 株情報 {"per": "25.3", "pbr": "3.2"}

    Returns:
        オープニング動画クリップ
    """

    print(f"[INFO] Generating opening thumbnail ({duration}s)...")

    # サムネイルのサイズ（YouTube推奨: 1280x720）
    thumb_size = (1280, 720)

    # グラデーション背景（濃紺→黒）
    from moviepy import ImageClip
    import numpy as np

    # グラデーション作成
    gradient = np.zeros((720, 1280, 3), dtype=np.uint8)
    for y in range(720):
        # 上から下へ濃紺→黒のグラデーション
        ratio = y / 720
        r = int(10 * (1 - ratio))
        g = int(30 * (1 - ratio))
        b = int(80 * (1 - ratio))
        gradient[y, :] = [r, g, b]

    background = ImageClip(gradient).with_duration(duration)

    clips = [background]

    # ===== 「決算速報」バッジ（左上） =====
    badge_clip = (
        TextClip(
            text="決算速報",
            font=FONT_PATH,
            font_size=36,
            color="white",
            bg_color="#FF4444",
            size=(160, 50),
            method="caption"
        )
        .with_duration(duration)
        .with_position((40, 40))
    )
    clips.append(badge_clip)

    # ===== 日付（右上） =====
    if date_str:
        date_clip = (
            TextClip(
                text=date_str,
                font=FONT_PATH,
                font_size=32,
                color="#CCCCCC",
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((920, 50))
        )
        clips.append(date_clip)

    # ===== 企業名（超特大・中央上） =====
    if company_name:
        # 株価コードがあれば追加
        display_name = f"{company_name} ({stock_info.get('code')})" if stock_info and stock_info.get(
            'code') else company_name

        company_clip = (
            TextClip(
                text=display_name,
                font=FONT_PATH,
                font_size=140,
                color="#FFD700",  # ゴールド
                stroke_color="#000000",  # 黒縁取り
                stroke_width=3,
                size=(1100, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position(("center", 140))
        )
        clips.append(company_clip)

    # ===== 装飾線 =====
    line_clip = (
        ColorClip(size=(800, 4), color=(255, 215, 0))  # ゴールド
        .with_duration(duration)
        .with_position(("center", 300))
    )
    clips.append(line_clip)

    # ===== PER・PBR（大きく・中央） =====
    if stock_info and stock_info.get("per") and stock_info.get("pbr"):
        per_value = stock_info['per']
        pbr_value = stock_info['pbr']

        # PER（左）
        per_clip = (
            TextClip(
                text=f"PER\n{per_value}",
                font=FONT_PATH,
                font_size=70,
                color="#00FF00",  # 緑
                stroke_color="#000000",
                stroke_width=2,
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((340, 360))
        )
        clips.append(per_clip)

        # PBR（右）
        pbr_clip = (
            TextClip(
                text=f"PBR\n{pbr_value}",
                font=FONT_PATH,
                font_size=70,
                color="#00BFFF",  # 水色
                stroke_color="#000000",
                stroke_width=2,
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((740, 360))
        )
        clips.append(pbr_clip)

    # ===== ROE（あれば） =====
    if stock_info and stock_info.get("roe"):
        roe_text = f"ROE {stock_info['roe']}%"
        roe_clip = (
            TextClip(
                text=roe_text,
                font=FONT_PATH,
                font_size=40,
                color="#FFFF00",  # 黄色
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((100, 520))
        )
        clips.append(roe_clip)

    # ===== 配当利回り（あれば） =====
    if stock_info and stock_info.get("dividend_yield"):
        div_text = f"配当 {stock_info['dividend_yield']}%"
        div_clip = (
            TextClip(
                text=div_text,
                font=FONT_PATH,
                font_size=40,
                color="#FF69B4",  # ピンク
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((400, 520))
        )
        clips.append(div_clip)

    # ===== 時価総額（あれば） =====
    if stock_info and stock_info.get("market_cap"):
        cap_text = f"💰 {stock_info['market_cap']}"
        cap_clip = (
            TextClip(
                text=cap_text,
                font=FONT_PATH,
                font_size=40,
                color="#FFFFFF",
                size=(500, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((700, 520))
        )
        clips.append(cap_clip)

    # ===== 「さくっと決算」（下端・控えめ） =====
    tagline_clip = (
        TextClip(
            text="さくっと決算",
            font=FONT_PATH,
            font_size=28,
            color="#888888",
            size=(600, None),
            method="caption"
        )
        .with_duration(duration)
        .with_position(("center", 650))
    )
    clips.append(tagline_clip)

    # 合成
    thumbnail = CompositeVideoClip(clips)

    # 静止画像として保存（YouTubeサムネイル用）
    thumbnail_path = output_path.replace(".mp4", "_thumbnail.png")
    thumbnail.save_frame(thumbnail_path, t=0)

    print(f"[INFO] Thumbnail image saved to: {thumbnail_path}")

    # オープニング動画クリップを返す
    return thumbnail


def generate_video(audio_path: str, output_path: str, text_content: str = None,
                   company_name: str = None, date_str: str = None, stock_info: dict = None) -> None:
    print(f"[INFO] Reading audio from: {audio_path}")

    # ===== フォント存在チェック（重要）=====
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")

    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    print(f"[INFO] Audio duration: {audio_duration:.2f} seconds")
    print("[INFO] Creating video with opening and scrolling text")

    # ===== オープニング（3秒）=====
    opening_duration = 3.0
    opening_clip = generate_thumbnail(output_path, company_name=company_name, date_str=date_str,
                                      duration=opening_duration, stock_info=stock_info)

    # ===== 本編部分（音声と同期）=====
    # 背景
    background = (
        ColorClip(size=(1280, 720), color=(0, 0, 0))
        .with_duration(audio_duration)
    )

    clips = [background]

    # タイトル（固定表示）
    if company_name and date_str:
        title_text = f"{company_name} {date_str} さくっと決算"
    elif company_name:
        title_text = f"{company_name} さくっと決算"
    else:
        title_text = "さくっと決算"

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
        .with_duration(audio_duration)
        .with_position(("center", 20))
    )

    clips.append(title_clip)

    # 本文（スクロール表示）
    if text_content:
        body_clip = (
            TextClip(
                text=text_content,
                font=FONT_PATH,
                font_size=30,
                color="white",
                size=(1100, None),
                method="caption"
            )
            .with_start(0)
            .with_duration(audio_duration)
        )

        # テキストの高さを取得
        text_height = body_clip.h
        screen_height = 720
        scroll_area_top = 100
        scroll_area_bottom = 720
        start_y = 360  # 画面中央から開始（720の半分）
        end_y = scroll_area_top - text_height
        scroll_distance = start_y - end_y

        # スクロール関数
        def scroll_position(t):
            progress = t / audio_duration
            current_y = start_y - (scroll_distance * progress)
            return ("center", current_y)

        body_clip = body_clip.with_position(scroll_position)
        clips.append(body_clip)

        print(f"[INFO] Text height: {text_height}px")
        print(f"[INFO] Scroll distance: {scroll_distance}px")
        print(f"[INFO] Scroll speed: {scroll_distance / audio_duration:.2f}px/sec")

    # 本編を合成
    main_video = CompositeVideoClip(clips).with_audio(audio)

    # ===== オープニング + 本編を結合 =====
    from moviepy import concatenate_videoclips

    print(f"[INFO] Concatenating opening ({opening_duration}s) + main video ({audio_duration}s)")
    final_video = concatenate_videoclips([opening_clip, main_video])

    print("[INFO] Writing video file...")

    total_frames = int(final_video.duration * 24)
    print(f"[INFO] Total frames: {total_frames} (duration: {final_video.duration:.2f}s, fps: 24)")

    try:
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger="bar"
        )
    except TypeError:
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac"
        )

    print(f"[INFO] Video saved to: {output_path}")
    print(f"[INFO] Total duration: {final_video.duration:.2f} seconds")

    # リソースのクリーンアップ
    audio.close()
    opening_clip.close()
    main_video.close()
    final_video.close()


# ===== デバッグ実行 =====
if __name__ == "__main__":
    # ===== ここを変更するだけで企業を切り替え可能 =====
    COMPANY_NAME = "ヒガシＨＤ"
    DATE_STR = "2026年1月23日"
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
        company_name=COMPANY_NAME,
        date_str=DATE_STR
    )

    print("=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)