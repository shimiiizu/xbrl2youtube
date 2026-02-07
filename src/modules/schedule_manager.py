# src/modules/schedule_manager.py

import json
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime


def setup_logging():
    """ログファイルとコンソールに同時に出力するロギング設定"""
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # ログファイル名に日時を付与
    log_filename = log_dir / f"auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # ルートロガーの設定
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # フォーマット
    formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # ファイル出力
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソール出力
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # printをloggingにリダイレクト
    import builtins
    original_print = builtins.print

    def log_print(*args, **kwargs):
        message = ' '.join(str(a) for a in args)
        # file引数が指定されている場合はloggingを使わない
        if 'file' in kwargs:
            original_print(*args, **kwargs)
        else:
            logging.info(message)

    builtins.print = log_print

    return log_filename


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

        if result.returncode != 0:
            print(f"[INFO] SYSTEMで失敗。カレントユーザーで再試行しています...")
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
            print("[OK] タスクスケジュラーに登録しました")
        else:
            print(f"[ERROR] タスク登録に失敗: {result.stderr}")
            return

        # PowerShellでログオンモードと電源管理を修正
        print("[INFO] タスク設定を修正しています...")
        ps_script = f"""
$taskName = "{task_name}"
$task = Get-ScheduledTask -TaskName $taskName

# 電源管理の修正
$settings = $task.Settings
$settings.StopIfGoingOnBatteries = $false
$settings.DisallowStartIfOnBatteries = $false

# ログオンモードの修正（Interactive = パスワード不要で対話型セッションで動作）
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

Set-ScheduledTask -TaskName $taskName -Settings $settings -Principal $principal
Write-Host "[OK] タスク設定の修正完了"
"""
        ps_result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="shift_jis"
        )

        if ps_result.returncode == 0:
            print("[OK] ログオンモード・電源管理の設定を修正しました")
        else:
            print(f"[ERROR] タスク設定の修正に失敗: {ps_result.stderr}")

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


def check_task():
    """タスクスケジュラーの登録状況を表示する"""
    task_name = get_task_name()

    print(f"\n[INFO] タスク登録状況を確認しています...")
    print(f"  タスク名: {task_name}\n")

    try:
        result = subprocess.run(
            ["schtasks", "/query", "/tn", task_name, "/v", "/fo", "LIST"],
            capture_output=True,
            text=True,
            encoding="shift_jis"
        )

        if result.returncode == 0:
            # 必要な項目だけ抽出して表示
            display_keys = [
                "タスク名",
                "次回の実行時刻",
                "状態",
                "ログオン モード",
                "前回の実行時刻",
                "前回の結果",
                "実行するタスク",
                "スケジュールされたタスクの状態",
                "電源管理",
                "日",
                "開始時刻",
            ]

            print("=" * 60)
            for line in result.stdout.splitlines():
                for key in display_keys:
                    if line.startswith(key):
                        print(line)
                        break
            print("=" * 60)
        else:
            print("✗ タスクが登録されていません")

    except Exception as e:
        print(f"[ERROR] タスク確認エラー: {e}")


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
        print("6. タスク登録状況を確認する")
        print("0. 戻る")
        print("=" * 60)

        choice = input("\n選択してください (0-6): ").strip()

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

        elif choice == "6":
            check_task()

        else:
            print("✗ 無効な選択です。0-6の数字を入力してください")


def run_auto(downloader_class, extractor_class, extract_text_fn, save_text_fn,
             generate_audio_fn, generate_video_fn, upload_fn, parse_date_fn, fetch_stock_info_fn):
    """
    自動実行モード（--auto引数で起動時に呼ばれる）

    Args:
        各モジュールの関数やクラスを外から受け取る
    """
    # ログ設定（すべての出力がログファイルに記録される）
    log_file = setup_logging()

    print(f"[LOG] ログファイル: {log_file}")
    print("=" * 60)

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
            # 株情報の取得
            info = fetch_stock_info_fn(company_only)
            if not info:
                print(f"✗ {company_name} スキップ（株情報取得できず）")
                continue

            text = extract_text_fn(str(htm_file))

            # 企業概要を冒頭に追加
            intro_parts = [f"【{company_only}】"]
            intro_parts.append(f"PER: {info.get('per', 'N/A')}")
            intro_parts.append(f"PBR: {info.get('pbr', 'N/A')}")
            if info.get('roe'):
                intro_parts.append(f"ROE: {info.get('roe')}%")
            if info.get('dividend_yield'):
                intro_parts.append(f"配当: {info.get('dividend_yield')}%")
            if info.get('market_cap'):
                intro_parts.append(f"時価総額: {info.get('market_cap')}")
            intro = " / ".join(intro_parts) + "\n\n"
            text = intro + text

            text_path = processed_dir / f"{company_name}_extracted_text.txt"
            audio_path = processed_dir / f"{company_name}_output.mp3"
            subtitle_path = processed_dir / f"{company_name}_subtitle.srt"
            video_path = processed_dir / f"{company_name}_output.mp4"

            save_text_fn(text, str(text_path))
            generate_audio_fn(str(text_path), str(audio_path))

            # 動画タイトル作成（株価コード付き）
            stock_code = f"【{info.get('code')}】" if info.get('code') else ""
            video_title = f"{stock_code}{company_only} {date_str} 決算サマリー" if date_str else f"{stock_code}{company_only} 決算サマリー"
            generate_video_fn(str(audio_path), str(video_path), text, company_only, date_str, stock_info=info)

            # YouTube説明欄作成
            desc_parts = [f"{company_only}の決算短信の内容を音声で解説した動画です。"]
            if info.get('code'):
                desc_parts.append(f"株価コード: {info.get('code')}")
            desc_parts.append(f"PER: {info.get('per', 'N/A')}")
            desc_parts.append(f"PBR: {info.get('pbr', 'N/A')}")
            if info.get('roe'):
                desc_parts.append(f"ROE: {info.get('roe')}%")
            if info.get('peg'):
                desc_parts.append(f"PEG: {info.get('peg')}")
            if info.get('dividend_yield'):
                desc_parts.append(f"配当利回り: {info.get('dividend_yield')}%")
            if info.get('equity_ratio'):
                desc_parts.append(f"自己資本比率: {info.get('equity_ratio')}%")
            if info.get('operating_margin'):
                desc_parts.append(f"営業利益率: {info.get('operating_margin')}%")
            if info.get('market_cap'):
                desc_parts.append(f"時価総額: {info.get('market_cap')}")
            description = "\n".join(desc_parts)

            # YouTubeアップロード
            upload_fn(
                video_path=str(video_path),
                title=video_title,
                description=description,
                privacy="public",
                company_name=company_only,
                subtitle_path=str(subtitle_path) if subtitle_path.exists() else None
            )
            print(f"✓ {company_name} 完了")
        except Exception as e:
            print(f"✗ {company_name} エラー: {e}")

    print("\n" + "=" * 60)
    print(f"自動実行完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)