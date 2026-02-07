# src/main.py

import sys
from pathlib import Path

# modulesフォルダをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# menu_handlers から各処理をインポート
from menu_handlers import (
    handle_full_process,
    handle_download_only,
    handle_extract_only,
    handle_text_extraction_only,
    handle_audio_generation_only,
    handle_subtitle_generation_only,
    handle_video_creation_only,
    handle_upload_only,
    handle_reset,
    handle_schedule_settings,
    handle_stock_info_check
)

# 自動実行用
from xbrl_downloader import TdnetXBRLDownloader
from qualitative_extractor import QualitativeExtractor
from text_extraction import extract_text_from_xbrl, save_text
from audio_generation import generate_audio
from video_generation import generate_video
from youtube_upload import upload_to_youtube
from stock_info import fetch_stock_info
from schedule_manager import run_auto


def parse_date_from_filename(filename):
    """ファイル名から日付を抽出して '2026年1月23日' 形式に変換"""
    try:
        # ファイル名から日付部分を抽出（例: オオバ_20260123 → 20260123）
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


def show_menu():
    """メニューを表示"""
    print("\n" + "=" * 60)
    print("XBRL → YouTube 自動化ツール")
    print("=" * 60)
    print("1. すべて実行(ダウンロード → 抽出 → 動画作成 → アップロード)")
    print("2. XBRLダウンロードのみ")
    print("3. qualitative.htm抽出のみ")
    print("4. テキスト抽出のみ")
    print("5. 音声生成のみ")
    print("6. 字幕生成のみ")
    print("7. 動画作成のみ")
    print("8. YouTubeアップロードのみ")
    print("9. リセット（全ファイルを退避フォルダに移動）")
    print("10. スケジュール設定・確認")
    print("11. 株情報確認のみ")
    print("0. 終了")
    print("=" * 60)


def main():
    """メイン処理"""
    project_root = Path(__file__).parent.parent

    while True:
        show_menu()
        choice = input("\n選択してください (0-11): ").strip()

        if choice == "0":
            print("\n終了します")
            break

        elif choice == "1":
            handle_full_process(project_root, parse_date_from_filename)

        elif choice == "2":
            handle_download_only(project_root, parse_date_from_filename)

        elif choice == "3":
            handle_extract_only(project_root, parse_date_from_filename)

        elif choice == "4":
            handle_text_extraction_only(project_root, parse_date_from_filename)

        elif choice == "5":
            handle_audio_generation_only(project_root, parse_date_from_filename)

        elif choice == "6":
            handle_subtitle_generation_only(project_root, parse_date_from_filename)

        elif choice == "7":
            handle_video_creation_only(project_root, parse_date_from_filename)

        elif choice == "8":
            handle_upload_only(project_root, parse_date_from_filename)

        elif choice == "9":
            handle_reset(project_root, parse_date_from_filename)

        elif choice == "10":
            handle_schedule_settings(project_root, parse_date_from_filename)

        elif choice == "11":
            handle_stock_info_check(project_root, parse_date_from_filename)

        else:
            print("✗ 無効な選択です。0-11の数字を入力してください")


if __name__ == "__main__":
    # --auto引数がある場合は自動実行モード
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        run_auto(
            downloader_class=TdnetXBRLDownloader,
            extractor_class=QualitativeExtractor,
            extract_text_fn=extract_text_from_xbrl,
            save_text_fn=save_text,
            generate_audio_fn=generate_audio,
            generate_video_fn=generate_video,
            upload_fn=upload_to_youtube,
            parse_date_fn=parse_date_from_filename,
            fetch_stock_info_fn=fetch_stock_info
        )
    else:
        # 通常のメニューモード
        main()