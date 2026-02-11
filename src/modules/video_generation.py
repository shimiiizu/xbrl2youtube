# src/modules/video_generation.py

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from pathlib import Path
import os
from config import VideoConfig as VC  # VCと略記して使いやすく

# 後方互換性のため（他のファイルから参照されている可能性）
FONT_PATH = VC.FONT_PATH


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
            font=VC.FONT_PATH,
            font_size=VC.FONT_SIZE_BADGE,
            color=VC.COLOR_WHITE,
            bg_color=VC.COLOR_RED,
            size=VC.SIZE_BADGE,
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
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_DATE,
                color=VC.COLOR_LIGHT_GRAY,
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((920, 50))
        )
        clips.append(date_clip)

    # ===== 企業名（大きく・中央上） =====
    if company_name:
        company_clip = (
            TextClip(
                text=company_name,
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_COMPANY,
                color=VC.COLOR_GOLD,
                stroke_color=VC.COLOR_BLACK,
                stroke_width=VC.STROKE_WIDTH_COMPANY,
                size=VC.SIZE_COMPANY,
                method="caption"
            )
            .with_duration(duration)
            .with_position(("center", VC.POS_Y_COMPANY))
        )
        clips.append(company_clip)

    # ===== 株価コード（企業名の下に小さく） =====
    if stock_info and stock_info.get('code'):
        code_clip = (
            TextClip(
                text=f"({stock_info.get('code')})",
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_CODE,
                color=VC.COLOR_GOLD,
                stroke_color=VC.COLOR_BLACK,
                stroke_width=VC.STROKE_WIDTH_CODE,
                size=VC.SIZE_CODE,
                method="caption"
            )
            .with_duration(duration)
            .with_position(("center", VC.POS_Y_CODE))
        )
        clips.append(code_clip)

    # ===== 装飾線 =====
    line_clip = (
        ColorClip(size=(VC.LINE_WIDTH, VC.LINE_HEIGHT), color=VC.LINE_COLOR)
        .with_duration(duration)
        .with_position(("center", VC.POS_Y_LINE))
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
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_PER_PBR,
                color=VC.COLOR_GREEN,
                stroke_color=VC.COLOR_BLACK,
                stroke_width=VC.STROKE_WIDTH_PER_PBR,
                size=VC.SIZE_PER_PBR,
                method="caption"
            )
            .with_duration(duration)
            .with_position((VC.POS_X_PER, VC.POS_Y_PER_PBR))
        )
        clips.append(per_clip)

        # PBR（右）
        pbr_clip = (
            TextClip(
                text=f"PBR\n{pbr_value}",
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_PER_PBR,
                color=VC.COLOR_BLUE,
                stroke_color=VC.COLOR_BLACK,
                stroke_width=VC.STROKE_WIDTH_PER_PBR,
                size=VC.SIZE_PER_PBR,
                method="caption"
            )
            .with_duration(duration)
            .with_position((VC.POS_X_PBR, VC.POS_Y_PER_PBR))
        )
        clips.append(pbr_clip)

    # ===== ROE（あれば） =====
    if stock_info and stock_info.get("roe"):
        roe_text = f"ROE {stock_info['roe']}%"
        roe_clip = (
            TextClip(
                text=roe_text,
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_ROE,
                color=VC.COLOR_YELLOW,
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((VC.POS_X_ROE, VC.POS_Y_ROE))
        )
        clips.append(roe_clip)

    # ===== 配当利回り（あれば） =====
    if stock_info and stock_info.get("dividend_yield"):
        div_text = f"配当 {stock_info['dividend_yield']}%"
        div_clip = (
            TextClip(
                text=div_text,
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_DIVIDEND,
                color=VC.COLOR_PINK,
                size=(300, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((VC.POS_X_DIVIDEND, VC.POS_Y_DIVIDEND))
        )
        clips.append(div_clip)

    # ===== 時価総額（あれば） =====
    if stock_info and stock_info.get("market_cap"):
        cap_text = f"💰 {stock_info['market_cap']}"
        cap_clip = (
            TextClip(
                text=cap_text,
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_MARKET_CAP,
                color=VC.COLOR_WHITE,
                size=(500, None),
                method="caption"
            )
            .with_duration(duration)
            .with_position((VC.POS_X_MARKET_CAP, VC.POS_Y_MARKET_CAP))
        )
        clips.append(cap_clip)

    # ===== 「さくっと決算」（下端・控えめ） =====
    tagline_clip = (
        TextClip(
            text="さくっと決算",
            font=VC.FONT_PATH,
            font_size=VC.FONT_SIZE_TAGLINE,
            color=VC.COLOR_GRAY,
            size=(600, None),
            method="caption"
        )
        .with_duration(duration)
        .with_position(("center", VC.POS_Y_TAGLINE))
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

    # ===== オープニング =====
    opening_duration = VC.OPENING_DURATION
    opening_clip = generate_thumbnail(output_path, company_name=company_name, date_str=date_str,
                                      duration=opening_duration, stock_info=stock_info)

    # ===== 本編部分（音声と同期）=====
    # 背景
    background = (
        ColorClip(size=(VC.WIDTH, VC.HEIGHT), color=(0, 0, 0))
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
            font=VC.FONT_PATH,
            font_size=VC.FONT_SIZE_TITLE,
            color=VC.COLOR_WHITE,
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
                font=VC.FONT_PATH,
                font_size=VC.FONT_SIZE_BODY,
                color=VC.COLOR_WHITE,
                size=(1100, None),
                method="caption"
            )
            .with_start(0)
            .with_duration(audio_duration)
        )

        # テキストの高さを取得
        text_height = body_clip.h
        screen_height = VC.HEIGHT
        scroll_area_top = 100
        scroll_area_bottom = VC.HEIGHT
        start_y = VC.SCROLL_START_Y  # 画面中央から開始
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
            fps=VC.FPS,
            codec=VC.CODEC,
            audio_codec=VC.AUDIO_CODEC,
            logger="bar"
        )
    except TypeError:
        final_video.write_videofile(
            output_path,
            fps=VC.FPS,
            codec=VC.CODEC,
            audio_codec=VC.AUDIO_CODEC
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
    # =============================================

    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data" / "processed"

    # data/processedから該当企業のファイルを検索
    htm_files = list(processed_dir.glob(f"{COMPANY_NAME}_*_qualitative.htm"))

    if not htm_files:
        print(f"[ERROR] {COMPANY_NAME} のファイルが見つかりません")
        print(f"[INFO] 検索パス: {processed_dir / f'{COMPANY_NAME}_*_qualitative.htm'}")
        exit(1)

    # 最初のファイルを使用（通常は1件のみ）
    htm_file = htm_files[0]
    company_name_with_date = htm_file.stem.replace('_qualitative', '')


    # 日付を自動抽出
    def parse_date_from_filename(filename):
        try:
            parts = filename.split('_')
            date_str = parts[1] if len(parts) > 1 else None
            if date_str and len(date_str) == 8 and date_str.isdigit():
                year = date_str[0:4]
                month = str(int(date_str[4:6]))
                day = str(int(date_str[6:8]))
                return f"{year}年{month}月{day}日"
        except:
            pass
        return None


    date_str = parse_date_from_filename(company_name_with_date)

    # 各ファイルパスを自動生成
    test_audio = processed_dir / f"{company_name_with_date}_output.mp3"
    test_text = processed_dir / f"{company_name_with_date}_extracted_text.txt"
    test_subtitle = processed_dir / f"{company_name_with_date}_subtitle.srt"
    test_output = processed_dir / f"{company_name_with_date}_output.mp4"

    print("=" * 50)
    print(f"動画生成テスト開始: {COMPANY_NAME}")
    print(f"ファイル名: {company_name_with_date}")
    print(f"日付: {date_str if date_str else 'なし'}")
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

    # 株情報を取得
    from stock_info import fetch_stock_info

    stock_info = fetch_stock_info(COMPANY_NAME)
    if stock_info:
        print(
            f"[INFO] 株情報取得成功: コード={stock_info.get('code')}, PER={stock_info.get('per')}, PBR={stock_info.get('pbr')}")
    else:
        print(f"[WARNING] 株情報を取得できませんでした")

    generate_video(
        audio_path=str(test_audio),
        output_path=str(test_output),
        text_content=text_content,
        company_name=COMPANY_NAME,
        date_str=date_str,
        stock_info=stock_info  # 追加！
    )

    print("=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)