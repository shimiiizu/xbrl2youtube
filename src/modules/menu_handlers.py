# src/modules/menu_handlers.py

from pathlib import Path
from xbrl_downloader import TdnetXBRLDownloader
from qualitative_extractor import QualitativeExtractor
from text_extraction import extract_text_from_xbrl, save_text
from audio_generation import generate_audio
from subtitle_generation import generate_subtitle
from video_generation import generate_video
from youtube_upload import upload_to_youtube
from reset_manager import reset_files
from schedule_manager import show_schedule_menu
from stock_info import fetch_stock_info


def handle_full_process(project_root, parse_date_fn):
    """メニュー1: すべて実行"""
    date_input = input("日付を指定 (例: 20250127) または Enter でスキップ: ").strip()
    filter_date = date_input if date_input and len(date_input) == 8 and date_input.isdigit() else None

    limit = int(input("表示する企業数 (デフォルト: 50): ").strip() or "50")

    print("\n" + "=" * 60)
    print("全自動処理を開始します")
    print("=" * 60)

    # ダウンロード（企業選択あり）
    try:
        downloader = TdnetXBRLDownloader("downloads")
        downloader.run(limit=limit, max_files_per_company=1, interactive=True, filter_date=filter_date)
    except Exception as e:
        print(f"⚠ ダウンロードエラー: {e}")

    # 抽出
    try:
        extractor = QualitativeExtractor()
        if extractor.extract_qualitative_files() == 0:
            print("⚠ 抽出失敗。処理を中断します")
            return
    except Exception as e:
        print(f"⚠ 抽出エラー: {e}")
        return

    # 動画作成とアップロード
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    htm_files = list(processed_dir.glob("*_qualitative.htm"))

    for htm_file in htm_files:
        company_name = htm_file.stem.replace('_qualitative', '')
        date_str = parse_date_fn(company_name)
        company_only = company_name.split('_')[0]

        try:
            # 株情報の取得
            info = fetch_stock_info(company_only)
            if not info:
                print(f"✗ {company_name} スキップ（株情報取得できず）")
                continue

            text = extract_text_from_xbrl(str(htm_file))

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

            save_text(text, str(text_path))
            generate_audio(str(text_path), str(audio_path))
            # generate_subtitle(str(text_path), str(audio_path), str(subtitle_path), model_size="small")

            # 動画タイトル作成
            stock_code = f"【{info.get('code')}】" if info.get('code') else ""
            video_title = f"{stock_code}{company_only} {date_str} 決算サマリー" if date_str else f"{stock_code}{company_only} 決算サマリー"
            generate_video(str(audio_path), str(video_path), text, company_only, date_str, stock_info=info)

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
            upload_to_youtube(
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
    print("すべての処理が完了しました!")
    print("=" * 60)


def handle_download_only(project_root, parse_date_fn):
    """メニュー2: XBRLダウンロードのみ"""
    date_input = input("日付を指定 (例: 20250127) または Enter でスキップ: ").strip()
    filter_date = date_input if date_input and len(date_input) == 8 and date_input.isdigit() else None

    limit = int(input("表示する企業数 (デフォルト: 50): ").strip() or "50")
    try:
        downloader = TdnetXBRLDownloader("downloads")
        downloader.run(limit=limit, max_files_per_company=1, interactive=True, filter_date=filter_date)
        print("✓ ダウンロード完了")
    except Exception as e:
        print(f"✗ エラー: {e}")


def handle_extract_only(project_root, parse_date_fn):
    """メニュー3: qualitative.htm抽出のみ"""
    try:
        extractor = QualitativeExtractor()
        count = extractor.extract_qualitative_files()
        print(f"✓ 抽出完了: {count}件")
    except Exception as e:
        print(f"✗ エラー: {e}")


def handle_text_extraction_only(project_root, parse_date_fn):
    """メニュー4: テキスト抽出のみ"""
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    for htm_file in processed_dir.glob("*_qualitative.htm"):
        company_name = htm_file.stem.replace('_qualitative', '')
        try:
            text = extract_text_from_xbrl(str(htm_file))
            text_path = processed_dir / f"{company_name}_extracted_text.txt"
            save_text(text, str(text_path))
            print(f"✓ {company_name}")
        except Exception as e:
            print(f"✗ {company_name}: {e}")


def handle_audio_generation_only(project_root, parse_date_fn):
    """メニュー5: 音声生成のみ"""
    processed_dir = project_root / "data" / "processed"

    for text_file in processed_dir.glob("*_extracted_text.txt"):
        company_name = text_file.stem.replace('_extracted_text', '')
        try:
            audio_path = processed_dir / f"{company_name}_output.mp3"
            generate_audio(str(text_file), str(audio_path))
            print(f"✓ {company_name}")
        except Exception as e:
            print(f"✗ {company_name}: {e}")


def handle_subtitle_generation_only(project_root, parse_date_fn):
    """メニュー6: 字幕生成のみ"""
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


def handle_video_creation_only(project_root, parse_date_fn):
    """メニュー7: 動画作成のみ"""
    processed_dir = project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    for htm_file in processed_dir.glob("*_qualitative.htm"):
        company_name = htm_file.stem.replace('_qualitative', '')
        date_str = parse_date_fn(company_name)
        company_only = company_name.split('_')[0]

        try:
            # 株情報の取得
            info = fetch_stock_info(company_only)
            if not info:
                print(f"✗ {company_name} スキップ（株情報取得できず）")
                continue

            text = extract_text_from_xbrl(str(htm_file))

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

            save_text(text, str(text_path))
            generate_audio(str(text_path), str(audio_path))
            # generate_subtitle(str(text_path), str(audio_path), str(subtitle_path), model_size="small")
            generate_video(str(audio_path), str(video_path), text, company_only, date_str, stock_info=info)
            print(f"✓ {company_name}")
        except Exception as e:
            print(f"✗ {company_name}: {e}")


def handle_upload_only(project_root, parse_date_fn):
    """メニュー8: YouTubeアップロードのみ"""
    processed_dir = project_root / "data" / "processed"

    for video_file in processed_dir.glob("*_output.mp4"):
        company_name = video_file.stem.replace('_output', '')
        date_str = parse_date_fn(company_name)
        company_only = company_name.split('_')[0]

        try:
            # 株情報の取得
            info = fetch_stock_info(company_only)

            subtitle_path = processed_dir / f"{company_name}_subtitle.srt"

            # 動画タイトル作成（株価コード付き）
            stock_code = f"【{info.get('code')}】" if info and info.get('code') else ""
            video_title = f"{stock_code}{company_only} {date_str} 決算サマリー" if date_str else f"{stock_code}{company_only} 決算サマリー"

            # YouTube説明欄作成
            if info:
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
            else:
                description = f"{company_only}の決算短信の内容を音声で解説した動画です。"

            upload_to_youtube(
                video_path=str(video_file),
                title=video_title,
                description=description,
                privacy="public",
                company_name=company_only,
                subtitle_path=str(subtitle_path) if subtitle_path.exists() else None
            )
            print(f"✓ {company_name}")
        except Exception as e:
            print(f"✗ {company_name}: {e}")


def handle_reset(project_root, parse_date_fn):
    """メニュー9: リセット"""
    reset_files()


def handle_schedule_settings(project_root, parse_date_fn):
    """メニュー10: スケジュール設定・確認"""
    show_schedule_menu()


def handle_stock_info_check(project_root, parse_date_fn):
    """メニュー11: 株情報確認のみ"""
    user_input = input("\n企業名を入力してください (スペース区切りで複数可, 例: トヨタ自動車 ソニー): ").strip()
    if not user_input:
        print("✗ 入力が空です")
        return

    companies = user_input.split()
    print(f"\n=== 株情報確認: {len(companies)}社 ===\n")

    for company in companies:
        info = fetch_stock_info(company)
        if info:
            print(f"  ✓ {company}")
            if info.get('code'):
                print(f"      株価コード:  {info.get('code')}")
            print(f"      PER:  {info.get('per', 'N/A')}")
            print(f"      PBR:  {info.get('pbr', 'N/A')}")
            if info.get('roe'):
                print(f"      ROE:  {info.get('roe')}%")
            if info.get('peg'):
                print(f"      PEG:  {info.get('peg')}")
            if info.get('dividend_yield'):
                print(f"      配当利回り:  {info.get('dividend_yield')}%")
            if info.get('equity_ratio'):
                print(f"      自己資本比率:  {info.get('equity_ratio')}%")
            if info.get('operating_margin'):
                print(f"      営業利益率:  {info.get('operating_margin')}%")
            if info.get('market_cap'):
                print(f"      時価総額:  {info.get('market_cap')}")
        else:
            print(f"  ✗ {company} - 取得できませんでした")
        print()