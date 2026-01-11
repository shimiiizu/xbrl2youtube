# src/modules/text_extraction.py

from bs4 import BeautifulSoup


def extract_text_from_xbrl(file_path: str) -> str:
    """
    HTMLファイルから「経営成績に関する説明」セクションのテキストを抽出する

    Args:
        file_path: HTMLファイルのパス

    Returns:
        抽出されたテキスト
    """
    print(f"[INFO] Extracting text from HTML: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')

    texts = []
    in_target_section = False

    for element in soup.find_all(['h3', 'p']):
        text = element.get_text(strip=True)

        if not text or text == '　':
            continue

        # 「経営成績に関する説明」セクションの開始
        if "経営成績に関する説明" in text:
            in_target_section = True
            continue

        # 次の見出しが来たら終了
        if in_target_section and element.name == 'h3':
            break

        # セクション内のテキストを収集
        if in_target_section and len(text) > 10:
            texts.append(text)

    result = '\n\n'.join(texts)
    print(f"[INFO] Extracted {len(texts)} paragraphs")

    return result


if __name__ == "__main__":
    # デバッグ用
    test_file = "../../data/qualitative.htm"

    print("=" * 50)
    print("テキスト抽出テスト開始")
    print("=" * 50)

    extracted_text = extract_text_from_xbrl(test_file)

    print("\n" + "=" * 50)
    print("抽出結果:")
    print("=" * 50)
    print(extracted_text)
    print("\n" + "=" * 50)
    print(f"抽出文字数: {len(extracted_text)} 文字")
    print("=" * 50)