# src/modules/video_helpers.py

"""
動画生成・アップロード処理で共通利用するヘルパー関数
"""


def create_intro_text(company_name: str, stock_info: dict) -> str:
    """企業概要テキストを生成

    Args:
        company_name: 企業名（日付なし）
        stock_info: 株情報辞書

    Returns:
        企業概要テキスト（例: 【企業名】PER: XX / PBR: XX / ROE: XX%...）
    """
    intro_parts = [f"【{company_name}】"]
    intro_parts.append(f"PER: {stock_info.get('per', 'N/A')}")
    intro_parts.append(f"PBR: {stock_info.get('pbr', 'N/A')}")

    if stock_info.get('roe'):
        intro_parts.append(f"ROE: {stock_info.get('roe')}%")
    if stock_info.get('dividend_yield'):
        intro_parts.append(f"配当: {stock_info.get('dividend_yield')}%")
    if stock_info.get('market_cap'):
        intro_parts.append(f"時価総額: {stock_info.get('market_cap')}")

    return " / ".join(intro_parts) + "\n\n"


def create_video_title(company_name: str, date_str: str = None, stock_code: str = None) -> str:
    """動画タイトルを生成

    Args:
        company_name: 企業名
        date_str: 日付文字列（例: 2026年1月30日）
        stock_code: 株価コード（例: 6920）

    Returns:
        動画タイトル（例: 【6920】レーザーテック 2026年1月30日 決算サマリー）
    """
    code_prefix = f"【{stock_code}】" if stock_code else ""

    if date_str:
        return f"{code_prefix}{company_name} {date_str} 決算サマリー"
    else:
        return f"{code_prefix}{company_name} 決算サマリー"


def create_youtube_description(company_name: str, stock_info: dict = None) -> str:
    """YouTube説明欄を生成

    Args:
        company_name: 企業名
        stock_info: 株情報辞書（Noneの場合は基本説明のみ）

    Returns:
        YouTube説明欄テキスト
    """
    desc_parts = [f"{company_name}の決算短信の内容を音声で解説した動画です。"]

    if stock_info:
        if stock_info.get('code'):
            desc_parts.append(f"株価コード: {stock_info.get('code')}")

        desc_parts.append(f"PER: {stock_info.get('per', 'N/A')}")
        desc_parts.append(f"PBR: {stock_info.get('pbr', 'N/A')}")

        if stock_info.get('roe'):
            desc_parts.append(f"ROE: {stock_info.get('roe')}%")
        if stock_info.get('peg'):
            desc_parts.append(f"PEG: {stock_info.get('peg')}")
        if stock_info.get('dividend_yield'):
            desc_parts.append(f"配当利回り: {stock_info.get('dividend_yield')}%")
        if stock_info.get('equity_ratio'):
            desc_parts.append(f"自己資本比率: {stock_info.get('equity_ratio')}%")
        if stock_info.get('operating_margin'):
            desc_parts.append(f"営業利益率: {stock_info.get('operating_margin')}%")
        if stock_info.get('market_cap'):
            desc_parts.append(f"時価総額: {stock_info.get('market_cap')}")

    return "\n".join(desc_parts)