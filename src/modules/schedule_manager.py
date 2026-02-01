# src/modules/schedule_manager.py

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# デフォルト設定
DEFAULT_SCHEDULE = {
    "enabled": False,
    "time": "15:00",
    "company_limit": 10
}


def get_config_path():
    """設定ファイルのパスを返す"""
    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "data" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "schedule.json"


def load_schedule():
    """設定ファイルを読み込む。存在しない場合はデフォルト設定で作成"""
    config_path = get_config_path()

    if not config_path.exists():
        save_schedule(DEFAULT_SCHEDULE)
        print(f"[INFO] 設定ファイルを作成しました: {config_path}")
        return DEFAULT_SCHEDULE.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] 設定ファイルの読み込みに失敗: {e}")
        return DEFAULT_SCHEDULE.copy()


def save_schedule(schedule):
    """設定ファイルに書き込む"""
    config_path = get_config_path()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 設定ファイルを保存しました: {config_path}")
    except Exception as e:
        print(f"[ERROR] 設定ファイルの書き込みに失敗: {e}")


def get_task_name():
    """タスクスケジュラーのタスク名"""
    return "XBRL2YouTube_AutoRun"


def get_main_script_path():
    """main.pyの絶対パスを返す"""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "src" / "main.py"


def register_task(schedule):
    """Windowsタスクスケジュラーにタスクを登録する"""
    task_name = get_task_name()
    main_script = get_main_script_path()
    python_exe = sys.executable
    time_str = schedule["time"]  # HH:MM

    print(f"\n[INFO] タスクスケジュラーに登録しています...")
    print(f"  タスク名: {task_name}")
    print(f"  実行時刻: 毎平日 {time_str}")
    print(f"  実行コマンド: {python_exe} {main_script} --auto")

    # 既存タスクがある場合は削除
    subprocess.run(
        ["schtasks", "/delete", "/tn", task_name, "/f"],
        capture_output=True
    )

    # タスク登録コマンド
    # /sc WEEKLY で週単位、/d MON,TUE,WED,THU,FRI で平日のみ
    try:
        result = subprocess.run(
            [
                "schtasks", "/create",
                "/tn", task_name,
                "/tr", f"{python_exe} {main_script} --auto",
                "/sc", "WEEKLY",
                "/d", "MON,TUE,WED,THU,FRI",
                "/st", time_str,
                "/f",
                "/ru", "SYSTEM",
                "/rl", "HIGHEST"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[OK] タスクスケジュラーに登録しました")
        else:
            print(f"[ERROR] タスク登録に失敗: {result.stderr}")
            # SYSTEM で失敗した場合、カレントユーザーで再試行
            print("[INFO] カレントユーザーで再試行しています...")
            result = subprocess.run(
                [
                    "schtasks", "/create",
                    "/tn", task_name,
                    "/tr", f"{python_exe} {main_script} --auto",
                    "/sc", "WEEKLY",
                    "/d", "MON,TUE,WED,THU,FRI",
                    "/st", time_str,
                    "/f"
                ],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[OK] カレントユーザーでタスクスケジュラーに登録しました")
            else:
                print(f"[ERROR] タスク登録に失敗: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] タスク登録エラー: {e}")


def unregister_task():
    """Windowsタスクスケジュラーからタスクを削除する"""
    task_name = get_task_name()

    print(f"\n[INFO] タスクスケジュラーからタスクを削除しています...")
    print(f"  タスク名: {task_name}")

    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[OK] タスクスケジュラーからタスクを削除しました")
        else:
            print(f"[ERROR] タスク削除に失敗: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] タスク削除エラー: {e}")


def show_schedule_menu():
    """スケジュール設定メニューを表示・操作"""
    while True:
        schedule = load_schedule()
        enabled_str = "有効" if schedule["enabled"] else "無効"

        print("\n" + "=" * 60)
        print("スケジュール設定")
        print("=" * 60)
        print(f"現在の状態: {enabled_str}")
        print(f"実行時刻: 毎平日 {schedule['time']}")
        print(f"企業数: {schedule['company_limit']}社")
        print("-" * 60)
        print("1. スケジュールを有効にする/無効にする")
        print("2. 実行時刻を変更")
        print("3. 企業数を変更")
        print("4. タスクスケジュラーに登録する")
        print("5. タスクスケジュラーから削除する")
        print("0. 戻る")
        print("=" * 60)

        choice = input("\n選択してください (0-5): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            schedule["enabled"] = not schedule["enabled"]
            save_schedule(schedule)
            print(f"✓ スケジュールを{'有効にしました' if schedule['enabled'] else '無効にしました'}")

        elif choice == "2":
            while True:
                time_input = input("実行時刻を入力してください (例: 15:00): ").strip()
                try:
                    # HH:MM形式のバリデーション
                    datetime.strptime(time_input, "%H:%M")
                    schedule["time"] = time_input
                    save_schedule(schedule)
                    print(f"✓ 実行時刻を {time_input} に変更しました")
                    break
                except ValueError:
                    print("✗ 無効な時刻形式です。HH:MM形式で入力してください (例: 15:00)")

        elif choice == "3":
            while True:
                limit_input = input("企業数を入力してください (例: 10): ").strip()
                try:
                    limit = int(limit_input)
                    if limit < 1:
                        print("✗ 1以上の数字を入力してください")
                        continue
                    schedule["company_limit"] = limit
                    save_schedule(schedule)
                    print(f"✓ 企業数を {limit}社 に変更しました")
                    break
                except ValueError:
                    print("✗ 無効な入力です。数字を入力してください")

        elif choice == "4":
            register_task(schedule)

        elif choice == "5":
            unregister_task()

        else:
            print("✗ 無効な選択です。0-5の数字を入力してください")


def run_auto(downloader_class, extractor_class, extract_text_fn, save_text_fn,
             generate_audio_fn, generate_video_fn, upload_fn, parse_date_fn):
    """
    自動実行モード（--auto引数で起動時に呼ばれる）

    Args:
        各モジュールの関数やクラスを外から受け取る
    """
    schedule = load_schedule()

    if not schedule["enabled"]:
        print("[INFO] スケジュールは無効です。終了しています。")
        return

    print("\n" + "=" * 60)
    print(f"自動実行モード開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 今日の日付をYYYYMMDD形式で取得
    today = datetime.now().strftime("%Y%m%d")
    company_limit = schedule["company_limit"]

    print(f"[INFO] 対象日付: {today}")
    print(f"[INFO] 企業数上限: {company_limit}社")

    # プロジェクトルート
    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # ダウンロード（非対話モード、日付フィルタ付き）
    try:
        downloader = downloader_class("downloads")
        downloader.run(
            limit=company_limit,
            max_files_per_company=1,
            interactive=False,
            filter_date=today
        )
    except Exception as e:
        print(f"⚠ ダウンロードエラー: {e}")

    # 抽出
    try:
        extractor = extractor_class()
        if extractor.extract_qualitative_files() == 0:
            print("⚠ 抽出失敗。処理を中断します")
            return
    except Exception as e:
        print(f"⚠ 抽出エラー: {e}")
        return

    # 動画作成とアップロード
    htm_files = list(processed_dir.glob("*_qualitative.htm"))

    for htm_file in htm_files:
        company_name = htm_file.stem.replace('_qualitative', '')
        date_str = parse_date_fn(company_name)
        company_only = company_name.split('_')[0]

        try:
            text = extract_text_fn(str(htm_file))
            text_path = processed_dir / f"{company_name}_extracted_text.txt"
            audio_path = processed_dir / f"{company_name}_output.mp3"
            subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
            video_path = processed_dir / f"{company_name}_output.mp4"

            save_text_fn(text, str(text_path))
            generate_audio_fn(str(text_path), str(audio_path))

            # 動画タイトル作成
            video_title = f"{company_only} {date_str} 決算サマリー" if date_str else f"{company_only} 決算サマリー"
            generate_video_fn(str(audio_path), str(video_path), text, company_only, date_str)

            # YouTubeアップロード
            upload_fn(
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
    print(f"自動実行完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)