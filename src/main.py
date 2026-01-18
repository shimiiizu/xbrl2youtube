# src/main.py

import sys
from pathlib import Path

# 各モジュールをインポート
sys.path.append(str(Path(__file__).parent))

from modules.tdnet_xbrl.xbrl_downloader import TdnetXBRLDownloader
from modules.tdnet_xbrl.qualitative_extractor import QualitativeExtractor
from modules.text_extraction import extract_text_from_xbrl, save_text
from modules.audio_generation import generate_audio
from modules.video_generation import generate_video
from modules.youtube_upload import upload_to_youtube


def download_xbrl_files(limit=10):
    """XBRLファイルをダウンロード"""
    print("\n" + "=" * 60)
    print("ステップ1: XBRLファイルのダウンロード")
    print("=" * 60)

    try:
        downloader = TdnetXBRLDownloader("downloads")
        downloader.run(limit=limit, max_files_per_company=3)
        print("✓ ダウンロード完了")
        return True
    except Exception as e:
        print(f"✗ ダウンロードエラー: {type(e).__name__}: {e}")
        return False


def extract_qualitative_files():
    """ZIPファイルからqualitative.htmを抽出"""
    print("\n" + "=" * 60)
    print("ステップ2: qualitative.htmの抽出")
    print("=" * 60)

    try:
        extractor = QualitativeExtractor()
        count = extractor.extract_qualitative_files()

        if count > 0:
            print("✓ 抽出完了")
            return True
        else:
            print("✗ 抽出するファイルがありませんでした")
            return False
    except Exception as e:
        print(f"✗ 抽出エラー: {type(e).__name__}: {e}")
        return False


def process_single_file(qualitative_path, processed_dir):
    """1つのqualitative.htmファイルを処理"""
    try:
        # ファイル名から企業名を抽出
        file_stem = qualitative_path.stem
        company_name = file_stem.replace('_qualitative', '')

        print(f"\n{'=' * 60}")
        print(f"処理開始: {company_name}")
        print(f"{'=' * 60}")

        # 出力ファイルのパスを設定
        text_path = processed_dir / f"{company_name}_extracted_text.txt"
        audio_path = processed_dir / f"{company_name}_output.mp3"
        video_path = processed_dir / f"{company_name}_output.mp4"

        # 既存ファイルがあればスキップ
        if video_path.exists():
            print(f"[SKIP] 既に動画ファイルが存在します: {video_path.name}")
            return True

        # 1. XBRL → テキスト抽出
        print(f"[1/5] テキスト抽出中...")
        text = extract_text_from_xbrl(str(qualitative_path))

        # 2. テキストをファイルに保存
        print(f"[2/5] テキスト保存中...")
        save_text(text, str(text_path))

        # 3. テキストファイル → 音声
        print(f"[3/5] 音声生成中...")
        generate_audio(str(text_path), str(audio_path))

        # 4. 音声 → 動画
        print(f"[4/5] 動画生成中...")
        generate_video(str(audio_path), str(video_path))

        # 5. YouTubeへアップロード
        video_title = f"さくっと決算短信 {company_name}"
        print(f"[5/5] YouTubeアップロード中: {video_title}")
        upload_to_youtube(str(video_path), title=video_title)

        print(f"✓ {company_name} の処理が完了しました")
        return True

    except Exception as e:
        print(f"✗ エラーが発生しました: {company_name}")
        print(f"  エラー内容: {type(e).__name__}: {e}")
        return False


def create_videos():
    """動画作成とYouTubeアップロード"""
    print("\n" + "=" * 60)
    print("ステップ3: 動画作成とYouTubeアップロード")
    print("=" * 60)

    # パスの設定
    project_root = Path(__file__).parent.parent
    qualitative_dir = project_root / "downloads" / "qualitative"
    processed_dir = project_root / "data" / "processed"

    # 処理済みディレクトリを作成
    processed_dir.mkdir(parents=True, exist_ok=True)

    # qualitativeフォルダ内のすべての.htmファイルを取得
    htm_files = list(qualitative_dir.glob("*_qualitative.htm"))

    if not htm_files:
        print("✗ 処理対象のqualitative.htmファイルが見つかりません")
        print(f"  検索パス: {qualitative_dir}")
        return False

    print(f"検出されたファイル数: {len(htm_files)}")

    # 処理結果のカウント
    success_count = 0
    error_count = 0

    # 各ファイルを順番に処理
    for idx, htm_file in enumerate(htm_files, 1):
        print(f"\n進捗: [{idx}/{len(htm_files)}]")

        if process_single_file(htm_file, processed_dir):
            success_count += 1
        else:
            error_count += 1

    # 最終結果を表示
    print(f"\n{'=' * 60}")
    print(f"動画作成・アップロード完了")
    print(f"{'=' * 60}")
    print(f"成功: {success_count} 件")
    print(f"失敗: {error_count} 件")
    print(f"合計: {len(htm_files)} 件")

    return success_count > 0


def show_menu():
    """メニューを表示"""
    print("\n" + "=" * 60)
    print("XBRL → YouTube 自動化ツール")
    print("=" * 60)
    print("1. すべて実行（ダウンロード → 抽出 → 動画作成）")
    print("2. XBRLダウンロードのみ")
    print("3. qualitative.htm抽出のみ")
    print("4. 動画作成・YouTubeアップロードのみ")
    print("0. 終了")
    print("=" * 60)


def main():
    """メイン処理"""
    while True:
        show_menu()
        choice = input("\n選択してください (0-4): ").strip()

        if choice == "0":
            print("\n終了します")
            break

        elif choice == "1":
            # すべて実行
            limit_input = input("ダウンロードする企業数を入力 (デフォルト: 10): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 10

            print("\n" + "=" * 60)
            print("全自動処理を開始します")
            print("=" * 60)

            # 1. ダウンロード
            if not download_xbrl_files(limit):
                print("\n⚠ ダウンロードに失敗しましたが、続行します")

            # 2. 抽出
            if not extract_qualitative_files():
                print("\n⚠ 抽出に失敗しました。処理を中断します")
                continue

            # 3. 動画作成
            create_videos()

            print("\n" + "=" * 60)
            print("すべての処理が完了しました！")
            print("=" * 60)

        elif choice == "2":
            # ダウンロードのみ
            limit_input = input("ダウンロードする企業数を入力 (デフォルト: 10): ").strip()
            limit = int(limit_input) if limit_input.isdigit() else 10
            download_xbrl_files(limit)

        elif choice == "3":
            # 抽出のみ
            extract_qualitative_files()

        elif choice == "4":
            # 動画作成のみ
            create_videos()

        else:
            print("✗ 無効な選択です。0-4の数字を入力してください")


if __name__ == "__main__":
    main()