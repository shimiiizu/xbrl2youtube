# src/main.py

from pathlib import Path
from modules.text_extraction import extract_text_from_xbrl, save_text
from modules.audio_generation import generate_audio
from modules.video_generation import generate_video
from modules.youtube_upload import upload_to_youtube


def process_single_file(qualitative_path, processed_dir):
    """1つのqualitative.htmファイルを処理"""
    try:
        # ファイル名から企業名を抽出
        # ファイル名形式: {企業名}_qualitative.htm
        file_stem = qualitative_path.stem
        company_name = file_stem.replace('_qualitative', '')

        print(f"\n{'=' * 60}")
        print(f"処理開始: {company_name}")
        print(f"{'=' * 60}")

        # 出力ファイルのパスを設定
        text_path = processed_dir / f"{company_name}_extracted_text.txt"
        audio_path = processed_dir / f"{company_name}_output.mp3"
        video_path = processed_dir / f"{company_name}_output.mp4"

        # 1. XBRL → テキスト抽出
        print(f"[1/4] テキスト抽出中...")
        text = extract_text_from_xbrl(str(qualitative_path))

        # 2. テキストをファイルに保存
        print(f"[2/4] テキスト保存中...")
        save_text(text, str(text_path))

        # 3. テキストファイル → 音声
        print(f"[3/4] 音声生成中...")
        generate_audio(str(text_path), str(audio_path))

        # 4. 音声 → 動画
        print(f"[4/4] 動画生成中...")
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


def main():
    # パスの設定
    project_root = Path(__file__).parent.parent
    qualitative_dir = project_root / "downloads" / "qualitative"
    processed_dir = project_root / "data" / "processed"

    # 処理済みディレクトリを作成
    processed_dir.mkdir(parents=True, exist_ok=True)

    # qualitativeフォルダ内のすべての.htmファイルを取得
    htm_files = list(qualitative_dir.glob("*_qualitative.htm"))

    if not htm_files:
        print("処理対象のqualitative.htmファイルが見つかりません")
        print(f"検索パス: {qualitative_dir}")
        return

    print(f"\n{'=' * 60}")
    print(f"検出されたファイル数: {len(htm_files)}")
    print(f"{'=' * 60}")

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
    print(f"すべての処理が完了しました")
    print(f"{'=' * 60}")
    print(f"成功: {success_count} 件")
    print(f"失敗: {error_count} 件")
    print(f"合計: {len(htm_files)} 件")


if __name__ == "__main__":
    main()