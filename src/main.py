# src/main.py

import sys
from pathlib import Path
from datetime import datetime

# modulesフォルダをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# 既存モジュールから必要な関数をインポート
from xbrl_downloader import TdnetXBRLDownloader
from qualitative_extractor import QualitativeExtractor
from text_extraction import extract_text_from_xbrl, save_text
from audio_generation import generate_audio
from subtitle_generation import generate_subtitle
from video_generation import generate_video
from youtube_upload import upload_to_youtube


def parse_date_from_filename(filename):
    """ファイル名から日付を抽出して '2026年1月23日' 形式に変換"""
    try:
        # ファイル名から日付部分を抽出（例: オオバ_20260123 → 20260123）
        parts = filename.split('_')
        date_str = parts[1] if len(parts) > 1 else None

        if date_str and len(date_str) == 8 and date_str.isdigit():
            # 20260123 → 2026年1月23日
            year = date_str[0:4]
            month = str(int(date_str[4:6]))  # 01 → 1
            day = str(int(date_str[6:8]))  # 23 → 23
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
    print("0. 終了")
    print("=" * 60)


def main():
    """メイン処理"""
    project_root = Path(__file__).parent.parent

    while True:
        show_menu()
        choice = input("\n選択してください (0-8): ").strip()

        if choice == "0":
            print("\n終了します")
            break

        elif choice == "1":
            # すべて実行
            limit = int(input("ダウンロードする企業数 (デフォルト: 10): ").strip() or "10")

            print("\n" + "=" * 60)
            print("全自動処理を開始します")
            print("=" * 60)

            # ダウンロード
            try:
                downloader = TdnetXBRLDownloader("downloads")
                downloader.run(limit=limit, max_files_per_company=3)
            except Exception as e:
                print(f"⚠ ダウンロードエラー: {e}")

            # 抽出
            try:
                extractor = QualitativeExtractor()
                if extractor.extract_qualitative_files() == 0:
                    print("⚠ 抽出失敗。処理を中断します")
                    continue
            except Exception as e:
                print(f"⚠ 抽出エラー: {e}")
                continue

            # 動画作成
            qualitative_dir = project_root / "downloads" / "qualitative"
            processed_dir = project_root / "data" / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)

            htm_files = list(qualitative_dir.glob("*_qualitative.htm"))

            for htm_file in htm_files:
                company_name = htm_file.stem.replace('_qualitative', '')
                date_str = parse_date_from_filename(company_name)
                company_only = company_name.split('_')[0]  # 企業名のみ取得

                try:
                    text = extract_text_from_xbrl(str(htm_file))
                    text_path = processed_dir / f"{company_name}_extracted_text.txt"
                    audio_path = processed_dir / f"{company_name}_output.mp3"
                    subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
                    video_path = processed_dir / f"{company_name}_output.mp4"

                    save_text(text, str(text_path))
                    generate_audio(str(text_path), str(audio_path))
                    generate_subtitle(str(text_path), str(audio_path), str(subtitle_path), model_size="small")

                    # 動画タイトル作成
                    video_title = f"{company_only} {date_str} 決算サマリー" if date_str else f"{company_only} 決算サマリー"
                    generate_video(str(audio_path), str(video_path), text, company_only, date_str)

                    # YouTubeアップロード
                    upload_to_youtube(
                        video_path=str(video_path),
                        title=video_title,
                        description=f"{company_only}の決算短信の内容を音声で解説した動画です。",
                        privacy="private",
                        company_name=company_only,
                        subtitle_path=str(subtitle_path) if subtitle_path.exists() else None
                    )
                    print(f"✓ {company_name} 完了")
                except Exception as e:
                    print(f"✗ {company_name} エラー: {e}")

            print("\n" + "=" * 60)
            print("すべての処理が完了しました!")
            print("=" * 60)

        elif choice == "2":
            # ダウンロードのみ
            limit = int(input("ダウンロードする企業数 (デフォルト: 10): ").strip() or "10")
            try:
                downloader = TdnetXBRLDownloader("downloads")
                downloader.run(limit=limit, max_files_per_company=3)
                print("✓ ダウンロード完了")
            except Exception as e:
                print(f"✗ エラー: {e}")

        elif choice == "3":
            # 抽出のみ
            try:
                extractor = QualitativeExtractor()
                count = extractor.extract_qualitative_files()
                print(f"✓ {count}件抽出完了")
            except Exception as e:
                print(f"✗ エラー: {e}")

        elif choice == "4":
            # テキスト抽出のみ
            qualitative_dir = project_root / "downloads" / "qualitative"
            processed_dir = project_root / "data" / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)

            for htm_file in qualitative_dir.glob("*_qualitative.htm"):
                company_name = htm_file.stem.replace('_qualitative', '')
                try:
                    text = extract_text_from_xbrl(str(htm_file))
                    text_path = processed_dir / f"{company_name}_extracted_text.txt"
                    save_text(text, str(text_path))
                    print(f"✓ {company_name}")
                except Exception as e:
                    print(f"✗ {company_name}: {e}")

        elif choice == "5":
            # 音声生成のみ
            processed_dir = project_root / "data" / "processed"

            for text_file in processed_dir.glob("*_extracted_text.txt"):
                company_name = text_file.stem.replace('_extracted_text', '')
                try:
                    audio_path = processed_dir / f"{company_name}_output.mp3"
                    generate_audio(str(text_file), str(audio_path))
                    print(f"✓ {company_name}")
                except Exception as e:
                    print(f"✗ {company_name}: {e}")

        elif choice == "6":
            # 字幕生成のみ
            processed_dir = project_root / "data" / "processed"

            for audio_file in processed_dir.glob("*_output.mp3"):
                company_name = audio_file.stem.replace('_output', '')
                try:
                    text_path = processed_dir / f"{company_name}_extracted_text.txt"
                    subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
                    generate_subtitle(str(text_path), str(audio_file), str(subtitle_path), model_size="small")
                    print(f"✓ {company_name}")
                except Exception as e:
                    print(f"✗ {company_name}: {e}")

        elif choice == "7":
            # 動画作成のみ
            qualitative_dir = project_root / "downloads" / "qualitative"
            processed_dir = project_root / "data" / "processed"
            processed_dir.mkdir(parents=True, exist_ok=True)

            for htm_file in qualitative_dir.glob("*_qualitative.htm"):
                company_name = htm_file.stem.replace('_qualitative', '')
                date_str = parse_date_from_filename(company_name)
                company_only = company_name.split('_')[0]

                try:
                    text = extract_text_from_xbrl(str(htm_file))
                    text_path = processed_dir / f"{company_name}_extracted_text.txt"
                    audio_path = processed_dir / f"{company_name}_output.mp3"
                    subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
                    video_path = processed_dir / f"{company_name}_output.mp4"

                    save_text(text, str(text_path))
                    generate_audio(str(text_path), str(audio_path))
                    generate_subtitle(str(text_path), str(audio_path), str(subtitle_path), model_size="small")
                    generate_video(str(audio_path), str(video_path), text, company_only, date_str)
                    print(f"✓ {company_name}")
                except Exception as e:
                    print(f"✗ {company_name}: {e}")

        elif choice == "8":
            # YouTubeアップロードのみ
            processed_dir = project_root / "data" / "processed"

            for video_file in processed_dir.glob("*_output.mp4"):
                company_name = video_file.stem.replace('_output', '')
                date_str = parse_date_from_filename(company_name)
                company_only = company_name.split('_')[0]

                try:
                    subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
                    video_title = f"{company_only} {date_str} 決算サマリー" if date_str else f"{company_only} 決算サマリー"

                    upload_to_youtube(
                        video_path=str(video_file),
                        title=video_title,
                        description=f"{company_only}の決算短信の内容を音声で解説した動画です。",
                        privacy="private",
                        company_name=company_only,
                        subtitle_path=str(subtitle_path) if subtitle_path.exists() else None
                    )
                    print(f"✓ {company_name}")
                except Exception as e:
                    print(f"✗ {company_name}: {e}")

        else:
            print("✗ 無効な選択です。0-8の数字を入力してください")


if __name__ == "__main__":
    main()