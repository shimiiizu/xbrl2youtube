# src/modules/xbrl_downloader.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import zipfile
import os
from pathlib import Path


def download_xbrl(date: str) -> None:
    """
    指定日の決算短信のqualitative.htmファイルをダウンロード

    Args:
        date: 公開日（YYYY-MM-DD形式、例: "2026-01-12"）
    """
    print(f"[INFO] Downloading XBRL files for date: {date}")

    # ダウンロード先を設定
    download_dir = os.path.abspath("../../downloads")
    os.makedirs(download_dir, exist_ok=True)

    # Chromeオプション設定
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
    }
    options.add_experimental_option("prefs", prefs)

    # ブラウザ起動
    driver = webdriver.Chrome(options=options)

    try:
        # Tdnetにアクセス
        driver.get("https://www.release.tdnet.info/inbs/I_main_00.html")

        # 日付入力（例: 2026/01/12形式に変換）
        date_formatted = date.replace("-", "/")

        # 日付フィールドに入力（実際のフィールド名は要確認）
        # ※Tdnetの実際のHTML構造に合わせて調整が必要
        date_input = driver.find_element(By.NAME, "date_input_field_name")  # 要確認
        date_input.clear()
        date_input.send_keys(date_formatted)

        # 検索ボタンをクリック
        search_button = driver.find_element(By.ID, "search_button_id")  # 要確認
        search_button.click()

        time.sleep(2)

        # XBRLボタンを全て取得
        xbrl_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'XBRL')]")

        if not xbrl_buttons:
            print("[WARNING] No XBRL files found for this date")
            return

        print(f"[INFO] Found {len(xbrl_buttons)} XBRL files")

        for i, button in enumerate(xbrl_buttons):
            try:
                # 企業コードと会社名を取得（同じ行から）
                row = button.find_element(By.XPATH, "./ancestor::tr")
                code = row.find_element(By.XPATH, ".//td[2]").text  # コード列
                company = row.find_element(By.XPATH, ".//td[3]").text  # 会社名列

                print(f"[INFO] Downloading: {code} - {company}")

                # XBRLボタンをクリック
                button.click()
                time.sleep(3)  # ダウンロード待機

                # ダウンロードされたzipファイルを処理
                latest_zip = get_latest_file(download_dir, ".zip")
                if latest_zip:
                    extract_qualitative(latest_zip, code, company)

            except Exception as e:
                print(f"[WARNING] Failed to download XBRL for item {i + 1}: {e}")
                continue

        print("[INFO] Download completed")

    finally:
        driver.quit()


def get_latest_file(directory: str, extension: str) -> str:
    """最新のファイルを取得"""
    files = Path(directory).glob(f"*{extension}")
    files = sorted(files, key=os.path.getmtime, reverse=True)
    return str(files[0]) if files else None


def extract_qualitative(zip_path: str, code: str, company: str) -> None:
    """
    zipファイルからqualitative.htmを抽出

    Args:
        zip_path: zipファイルのパス
        code: 企業コード
        company: 会社名
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # qualitative.htmを探す
            for file in zip_ref.namelist():
                if 'qualitative.htm' in file.lower():
                    # 抽出
                    content = zip_ref.read(file)

                    # data/フォルダに保存
                    output_path = f"../../data/qualitative_{code}_{company}.htm"
                    with open(output_path, 'wb') as f:
                        f.write(content)

                    print(f"[INFO] Saved: {output_path}")
                    break

        # zipファイルを削除
        os.remove(zip_path)

    except Exception as e:
        print(f"[WARNING] Failed to extract qualitative.htm: {e}")


if __name__ == "__main__":
    # デバッグ用
    test_date = "2026-01-12"

    print("=" * 50)
    print("XBRL ダウンロードテスト開始")
    print("=" * 50)

    download_xbrl(test_date)

    print("\n" + "=" * 50)
    print("ダウンロード完了")
    print("=" * 50)