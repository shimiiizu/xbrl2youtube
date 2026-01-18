"""
TDnet RSS → 企業名取得 → JPX企業名検索 → XBRLダウンロード
（企業名をファイル名に含める仕様）
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import time
import re
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from tqdm import tqdm


class TdnetXBRLDownloader:
    def __init__(self, download_dir="downloads"):
        self.rss_url = "https://webapi.yanoshin.jp/webapi/tdnet/list/recent.rss"
        self.jpx_url = "https://www2.jpx.co.jp/tseHpFront/JJK010010Action.do?Show=Show"
        # プロジェクトルートからの絶対パスを構築
        project_root = Path(__file__).parent.parent.parent
        self.download_dir = project_root / download_dir / "zip"
        self.download_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    def fetch_rss(self):
        print("=== RSS取得開始 ===")
        r = requests.get(self.rss_url, timeout=30)
        r.raise_for_status()
        print(f"RSS取得成功: {len(r.content)} bytes")
        return r.content

    # -------------------------------------------------
    def parse_rss(self, rss_content):
        print("=== RSS解析開始 ===")
        items = []
        root = ET.fromstring(rss_content)

        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            if "決算短信" not in title:
                continue

            m = re.match(r"^([^:：]+)[：:]", title)
            if not m:
                print(f"[SKIP] タイトル解析失敗: {title}")
                continue

            company = re.sub(r"\b\d{4}\b", "", m.group(1)).strip()
            print(f"[RSS] 企業名抽出: {company}")

            items.append({"company": company, "title": title})

        print(f"RSS解析完了: {len(items)} 社")
        return items

    # -------------------------------------------------
    def rename_downloaded_files(self, company_name, download_before_count):
        """ダウンロードされたファイルに企業名を付与"""
        time.sleep(3)  # ダウンロード完了を待つ

        # ダウンロードフォルダ内の新しいZIPファイルを検索
        zip_files = sorted(
            self.download_dir.glob("*.zip"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # 新規ダウンロードファイルのみを対象
        new_files = zip_files[:len(zip_files) - download_before_count]

        renamed_count = 0
        for zip_file in new_files:
            # 企業名を含む新しいファイル名を作成
            # ファイル名に使えない文字を除去
            safe_company_name = re.sub(r'[\\/:*?"<>|]', '', company_name)
            new_name = f"{safe_company_name}_{zip_file.name}"
            new_path = zip_file.parent / new_name

            try:
                zip_file.rename(new_path)
                print(f"[RENAME] {zip_file.name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"[RENAME ERROR] {zip_file.name}: {e}")

        return renamed_count

    # -------------------------------------------------
    def download_xbrl_by_company(self, company, max_files=3):
        print(f"\n=== JPX検索開始: {company} ===")

        # ダウンロード前のファイル数をカウント
        download_before_count = len(list(self.download_dir.glob("*.zip")))

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": str(self.download_dir.resolve()),
            "download.prompt_for_download": False,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)

        try:
            print("[JPX] トップページアクセス")
            driver.get(self.jpx_url)

            # ★ 正しい入力欄：銘柄名（会社名）
            input_box = wait.until(
                EC.presence_of_element_located((By.NAME, "mgrMiTxtBx"))
            )
            input_box.clear()
            input_box.send_keys(company)
            print(f"[JPX] 銘柄名入力: {company}")

            driver.find_element(By.NAME, "searchButton").click()
            print("[JPX] 検索ボタンクリック")
            time.sleep(2)

            try:
                detail = wait.until(
                    EC.presence_of_element_located((By.NAME, "detail_button"))
                )
                print("[JPX] detail_button 見つかりました")
                detail.click()
            except TimeoutException:
                print("[NG] detail_button が見つかりません（検索ヒットなし）")
                return 0

            time.sleep(2)

            print("[JPX] 有価証券報告書タブへ切替")
            driver.execute_script("changeTab('2');")
            time.sleep(2)

            try:
                kaiji = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "/html/body/div/form/div/div[3]/div/table[4]/tbody/tr/th/input")
                    )
                )
                kaiji.click()
                print("[JPX] 開示情報 展開")
            except TimeoutException:
                print("[NG] 開示ボタンが見つかりません")
                return 0

            time.sleep(2)

            elements = driver.find_elements(By.XPATH, '//img[@alt="XBRL"]')
            print(f"[JPX] XBRLアイコン検出数: {len(elements)}")

            if not elements:
                print("[INFO] XBRLなし")
                return 0

            clicked = 0
            for idx, e in enumerate(elements, 1):
                try:
                    if not e.is_displayed():
                        print(f"[SKIP] {idx}: 非表示")
                        continue

                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", e
                    )
                    time.sleep(0.5)

                    e.click()
                    print(f"[OK] {idx}: XBRLクリック")
                    time.sleep(2)

                    clicked += 1
                    if clicked >= max_files:
                        break

                except Exception as ex:
                    print(f"[NG] {idx}: {type(ex).__name__}")
                    continue

            # ブラウザを閉じる前にファイル名を変更
            driver.quit()

            # ダウンロードされたファイルに企業名を付与
            if clicked > 0:
                self.rename_downloaded_files(company, download_before_count)

            return clicked

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            driver.quit()
            return 0

    # -------------------------------------------------
    def run(self, limit=10, max_files_per_company=3):
        rss = self.fetch_rss()
        items = self.parse_rss(rss)

        seen = set()
        unique = []
        for i in items:
            if i["company"] not in seen:
                seen.add(i["company"])
                unique.append(i)

        unique = unique[:limit]
        print(f"\n=== 処理対象企業数: {len(unique)} ===")

        total = 0
        for idx, item in enumerate(unique, 1):
            print(f"\n[{idx}/{len(unique)}] {item['company']}")
            total += self.download_xbrl_by_company(
                item["company"], max_files_per_company
            )
            time.sleep(3)

        print("\n=== 処理完了 ===")
        print(f"総ダウンロード数: {total}")
        print(f"保存先: {self.download_dir.resolve()}")


# -------------------------------------------------
if __name__ == "__main__":
    TdnetXBRLDownloader("downloads").run(
        limit=10,
        max_files_per_company=1
    )