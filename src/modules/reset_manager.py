# src/modules/reset_manager.py

from pathlib import Path
from datetime import datetime
import shutil


def reset_files():
    """
    すべての生成ファイルを退避フォルダに移動する
    """
    print("\n" + "=" * 60)
    print("リセット処理を開始します")
    print("=" * 60)

    # プロジェクトルートを取得（modulesの親の親）
    project_root = Path(__file__).parent.parent.parent

    print(f"\n[DEBUG] このスクリプトの場所: {Path(__file__).resolve()}")
    print(f"[DEBUG] プロジェクトルート: {project_root.resolve()}")

    # タイムスタンプ付き退避フォルダ名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_base = project_root / "archive" / timestamp

    # 移動対象のファイルパターンと退避先のマッピング
    move_targets = [
        {
            "source_dir": project_root / "downloads" / "zip",
            "archive_dir": archive_base / "downloads" / "zip",
            "pattern": "*.zip",
            "description": "ZIPファイル"
        },
        {
            "source_dir": project_root / "downloads" / "qualitative",
            "archive_dir": archive_base / "downloads" / "qualitative",
            "pattern": "*.htm",
            "description": "HTMLファイル"
        },
        {
            "source_dir": project_root / "data" / "processed",
            "archive_dir": archive_base / "data" / "processed",
            "pattern": "*_extracted_text.txt",
            "description": "テキストファイル"
        },
        {
            "source_dir": project_root / "data" / "processed",
            "archive_dir": archive_base / "data" / "processed",
            "pattern": "*_output.mp3",
            "description": "音声ファイル"
        },
        {
            "source_dir": project_root / "data" / "processed",
            "archive_dir": archive_base / "data" / "processed",
            "pattern": "*_subtitle.srt",
            "description": "字幕ファイル"
        },
        {
            "source_dir": project_root / "data" / "processed",
            "archive_dir": archive_base / "data" / "processed",
            "pattern": "*_output.mp4",
            "description": "動画ファイル"
        },
        {
            "source_dir": project_root / "data" / "processed",
            "archive_dir": archive_base / "data" / "processed",
            "pattern": "*_thumbnail.png",
            "description": "サムネイル"
        }
    ]

    total_moved = 0

    for target in move_targets:
        source_dir = target["source_dir"]
        archive_dir = target["archive_dir"]
        pattern = target["pattern"]
        description = target["description"]

        print(f"\n[検索] {description}")
        print(f"  パス: {source_dir.resolve()}")
        print(f"  パターン: {pattern}")

        # 元ディレクトリが存在しない場合はスキップ
        if not source_dir.exists():
            print(f"  [SKIP] ディレクトリが存在しません")
            continue

        # ファイル一覧を取得
        files = list(source_dir.glob(pattern))

        if not files:
            print(f"  [SKIP] ファイルが見つかりません (0件)")
            continue

        print(f"  [検出] {len(files)}件のファイルを発見")

        # 退避先ディレクトリを作成
        archive_dir.mkdir(parents=True, exist_ok=True)

        # ファイルを移動
        moved_count = 0
        for file_path in files:
            try:
                dest_path = archive_dir / file_path.name
                shutil.move(str(file_path), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] {file_path.name}: {e}")

        print(f"  [OK] {moved_count}件移動完了")
        total_moved += moved_count

    print("\n" + "=" * 60)
    print(f"リセット完了: 合計 {total_moved} ファイルを移動しました")
    print(f"退避先: {archive_base}")
    print("=" * 60)


# -------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("リセットマネージャー - 単体実行")
    print("=" * 60)
    reset_files()