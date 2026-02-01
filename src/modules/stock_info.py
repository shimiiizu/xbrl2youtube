# src/modules/stock_info.py

import re
import time
import requests
from bs4 import BeautifulSoup

# Yahoo! ファイナンス（日本版）のURL
YAHOO_SEARCH_URL = "https://search.yahoo.co.jp/search"
YAHOO_FINANCE_BASE = "https://finance.yahoo.co.jp"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def search_stock_code(company_name: str) -> str | None:
    """企業名から株式コードを検索する

    Args:
        company_name: 企業名（略称可）

    Returns:
        株式コード（4桁文字列）。見つからない場合はNone
    """
    try:
        # Yahoo! ファイナンスで企業名を検索
        params = {"p": f"{company_name} 株価"}
        response = requests.get(YAHOO_SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 検索結果からfinance.yahoo.co.jpのリンクを探す
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # finance.yahoo.co.jp/quote/XXXX.T のパターン
            match = re.search(r"finance\.yahoo\.co\.jp/quote/(\d+)\.T", href)
            if match:
                return match.group(1)

        return None

    except Exception as e:
        print(f"[ERROR] 株式コード検索エラー ({company_name}): {e}")
        return None


def get_stock_info(stock_code: str) -> dict | None:
    """株式コードからPER・PBR・業種を取得する

    Args:
        stock_code: 株式コード（4桁）

    Returns:
        {"per": "25.3", "pbr": "3.2", "sector": "電気機器"} のような辞書。
        取得できない場合はNone
    """
    try:
        url = f"{YAHOO_FINANCE_BASE}/quote/{stock_code}.T"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        info = {}

        # 業種の取得
        # Yahoo! ファイナンスの業種表示箇所を探す
        sector_patterns = [
            {"tag": "span", "class_contains": "sector"},
            {"tag": "div", "class_contains": "sector"},
        ]
        for pattern in sector_patterns:
            elements = soup.find_all(pattern["tag"])
            for elem in elements:
                class_str = " ".join(elem.get("class", []))
                if pattern["class_contains"] in class_str.lower():
                    text = elem.get_text(strip=True)
                    if text:
                        info["sector"] = text
                        break

        # PER・PBRの取得
        # Yahoo! ファイナンスの株価情報テーブルから探す
        all_text = soup.get_text()

        # PERの検索
        per_match = re.search(r"PER[（(]?\s*倍[）)]?\s*[\s：:]*\s*([\d.]+)", all_text)
        if not per_match:
            per_match = re.search(r"([\d.]+)\s*倍.*?PER", all_text)
        if per_match:
            info["per"] = per_match.group(1)

        # PBRの検索
        pbr_match = re.search(r"PBR[（(]?\s*倍[）)]?\s*[\s：:]*\s*([\d.]+)", all_text)
        if not pbr_match:
            pbr_match = re.search(r"([\d.]+)\s*倍.*?PBR", all_text)
        if pbr_match:
            info["pbr"] = pbr_match.group(1)

        # PERとPBRが両方取得できた場合のみ返す
        if "per" in info and "pbr" in info:
            return info
        else:
            print(f"[WARN] PER/PBR取得できず (コード: {stock_code}): {info}")
            return None

    except Exception as e:
        print(f"[ERROR] 株情報取得エラー (コード: {stock_code}): {e}")
        return None


def fetch_stock_info(company_name: str) -> dict | None:
    """企業名からPER・PBR・業種を取得するメイン関数

    企業名 → 株式コード検索 → PER・PBR・業種取得

    Args:
        company_name: 企業名

    Returns:
        {"per": "25.3", "pbr": "3.2", "sector": "電気機器"} のような辞書。
        取得できない場合はNone
    """
    print(f"[INFO] 株情報取得開始: {company_name}")

    # Step 1: 株式コード検索
    stock_code = search_stock_code(company_name)
    if not stock_code:
        print(f"[WARN] 株式コード見つからず: {company_name}")
        return None

    print(f"[INFO] 株式コード: {stock_code}")
    time.sleep(1)  # リクエスト間隔

    # Step 2: PER・PBR・業種取得
    info = get_stock_info(stock_code)
    if not info:
        print(f"[WARN] PER/PBR取得できず: {company_name} (コード: {stock_code})")
        return None

    print(
        f"[INFO] 株情報取得完了: {company_name} → PER: {info.get('per', 'N/A')}, PBR: {info.get('pbr', 'N/A')}, 業種: {info.get('sector', 'N/A')}")
    return info