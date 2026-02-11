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
        {"code": "6920", "per": "25.3", "pbr": "3.2", ...} のような辞書。
        取得できない場合はNone
    """
    try:
        url = f"{YAHOO_FINANCE_BASE}/quote/{stock_code}.T"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        info = {"code": stock_code}  # 株価コードを追加

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
        # Yahoo! ファイナンスの表記例:
        #   「PER（会社予想）」「45.23」のように、ラベルと値がセパレートされている
        #   または「PER（実績）45.23倍」のような形もある
        all_text = soup.get_text()

        # デバッグ用: 指標周辺のテキストを出力
        for keyword in ["PER", "PBR", "ROE", "配当利回り", "時価総額", "PEG", "自己資本比率", "営業利益率"]:
            indices = [m.start() for m in re.finditer(keyword, all_text)]
            for idx in indices[:3]:  # 最初の3件まで
                snippet = all_text[idx:idx + 80].replace('\n', ' ').strip()
                print(f"[DEBUG] {keyword} found: '{snippet}'")

        # PERの検索（複数パターン対応）
        # まず「---」をチェック
        per_na_match = re.search(r"PER[（(][^）)]*[）)][^P]*?---", all_text)
        if per_na_match:
            info["per"] = "---"
            print(f"[DEBUG] PER is N/A (---)")
        else:
            per_patterns = [
                r"PER[（(][^）)]*[）)][^0-9]*([\d.]+)倍",  # PER（会社予想）用語(連)54.66倍
                r"PER[（(][^）)]*[）)]\s*([\d.]+)",  # PER（会社予想）45.23
                r"PER\s*[：:]\s*([\d.]+)",  # PER：45.23
                r"([\d.]+)\s*PER",  # 45.23 PER
            ]
            for pattern in per_patterns:
                per_match = re.search(pattern, all_text)
                if per_match:
                    info["per"] = per_match.group(1)
                    print(f"[DEBUG] PER matched with pattern: {pattern}")
                    break

        # PBRの検索（複数パターン対応）
        # まず「---」をチェック
        pbr_na_match = re.search(r"PBR[（(][^）)]*[）)][^E]*?---", all_text)
        if pbr_na_match:
            info["pbr"] = "---"
            print(f"[DEBUG] PBR is N/A (---)")
        else:
            pbr_patterns = [
                r"PBR[（(][^）)]*[）)][^0-9]*([\d.]+)倍",  # PBR（実績）用語(連)15.90倍
                r"PBR[（(][^）)]*[）)]\s*([\d.]+)",  # PBR（実績）54.66
                r"PBR\s*[：:]\s*([\d.]+)",  # PBR：54.66
                r"([\d.]+)\s*PBR",  # 54.66 PBR
            ]
            for pattern in pbr_patterns:
                pbr_match = re.search(pattern, all_text)
                if pbr_match:
                    info["pbr"] = pbr_match.group(1)
                    print(f"[DEBUG] PBR matched with pattern: {pattern}")
                    break

        # ROEの検索
        roe_patterns = [
            r"ROE[（(][^）)]*[）)][^0-9]*([\d.]+)%",  # ROE（実績）15.20%
            r"ROE[（(][^）)]*[）)]\s*([\d.]+)",  # ROE（実績）15.20
            r"ROE\s*[：:]\s*([\d.]+)",  # ROE：15.20
        ]
        for pattern in roe_patterns:
            roe_match = re.search(pattern, all_text)
            if roe_match:
                info["roe"] = roe_match.group(1)
                print(f"[DEBUG] ROE matched with pattern: {pattern}")
                break

        # 配当利回りの検索
        dividend_patterns = [
            r"配当利回り[（(][^）)]*[）)][^0-9]*([\d.]+)%",  # 配当利回り（会社予想）2.50%
            r"配当利回り\s*[：:]\s*([\d.]+)",  # 配当利回り：2.50
            r"利回り[^0-9]*([\d.]+)%",  # 利回り 2.50%
        ]
        for pattern in dividend_patterns:
            div_match = re.search(pattern, all_text)
            if div_match:
                info["dividend_yield"] = div_match.group(1)
                print(f"[DEBUG] 配当利回り matched with pattern: {pattern}")
                break

        # 時価総額の検索（例: 1.2兆円、5,000億円、300億円）
        market_cap_patterns = [
            r"時価総額[^0-9]*([\d,]+\.?\d*)\s*兆円",  # 1.2兆円
            r"時価総額[^0-9]*([\d,]+)\s*億円",  # 5,000億円
            r"時価総額\s*[：:]\s*([\d,]+\.?\d*)\s*兆円",
            r"時価総額\s*[：:]\s*([\d,]+)\s*億円",
        ]
        for pattern in market_cap_patterns:
            cap_match = re.search(pattern, all_text)
            if cap_match:
                value = cap_match.group(1).replace(',', '')
                if '兆円' in pattern:
                    info["market_cap"] = f"{value}兆円"
                else:
                    info["market_cap"] = f"{value}億円"
                print(f"[DEBUG] 時価総額 matched with pattern: {pattern}")
                break

        # PEGレシオの検索
        peg_patterns = [
            r"PEG[^0-9]*([\d.]+)",  # PEG 1.5
            r"PEG\s*[：:]\s*([\d.]+)",  # PEG：1.5
        ]
        for pattern in peg_patterns:
            peg_match = re.search(pattern, all_text)
            if peg_match:
                info["peg"] = peg_match.group(1)
                print(f"[DEBUG] PEG matched with pattern: {pattern}")
                break

        # 自己資本比率の検索
        equity_ratio_patterns = [
            r"自己資本比率[^0-9]*([\d.]+)%",  # 自己資本比率 65.5%
            r"自己資本比率\s*[：:]\s*([\d.]+)",  # 自己資本比率：65.5
        ]
        for pattern in equity_ratio_patterns:
            eq_match = re.search(pattern, all_text)
            if eq_match:
                info["equity_ratio"] = eq_match.group(1)
                print(f"[DEBUG] 自己資本比率 matched with pattern: {pattern}")
                break

        # 営業利益率の検索
        operating_margin_patterns = [
            r"営業利益率[^0-9]*([\d.]+)%",  # 営業利益率 15.5%
            r"営業利益率\s*[：:]\s*([\d.]+)",  # 営業利益率：15.5
        ]
        for pattern in operating_margin_patterns:
            om_match = re.search(pattern, all_text)
            if om_match:
                info["operating_margin"] = om_match.group(1)
                print(f"[DEBUG] 営業利益率 matched with pattern: {pattern}")
                break

        # PERとPBRが両方取得できた場合のみ返す（その他はオプション）
        if "per" in info and "pbr" in info:
            print(
                f"[INFO] 取得成功 - コード: {info.get('code')}, PER: {info.get('per', 'N/A')}, PBR: {info.get('pbr', 'N/A')}, ROE: {info.get('roe', 'N/A')}, PEG: {info.get('peg', 'N/A')}, 自己資本比率: {info.get('equity_ratio', 'N/A')}%, 営業利益率: {info.get('operating_margin', 'N/A')}%")
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
        f"[INFO] 株情報取得完了: {company_name} → PER: {info.get('per', 'N/A')}, PBR: {info.get('pbr', 'N/A')}, ROE: {info.get('roe', 'N/A')}%, 配当: {info.get('dividend_yield', 'N/A')}%, 時価総額: {info.get('market_cap', 'N/A')}")
    return info