# src/modules/text_extraction.py

from bs4 import BeautifulSoup


def extract_text_from_xbrl(file_path: str) -> str:
    """
    HTMLファイルから「（１）当四半期の経営成績の概況」または
    「（１）当中間期の経営成績の概況」部分のテキストのみを抽出する

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
    target_keywords = [
        "（１）当四半期の経営成績の概況",
        "（１）当中間期の経営成績の概況",
        "(1)当四半期の経営成績の概況",
        "(1)当中間期の経営成績の概況"
    ]

    for element in soup.find_all('p'):
        text = element.get_text(strip=True)

        # 空のテキストや空白のみはスキップ
        if not text or text == '　':
            continue

        # ターゲットセクションの開始を検出
        if not in_target_section:
            for keyword in target_keywords:
                if keyword in text:
                    in_target_section = True
                    print(f"[INFO] Found section: {text}")
                    break
            continue

        # 次の見出し（２）が来たら終了
        if text.startswith("（２）") or text.startswith("(2)"):
            print(f"[INFO] End section detected: {text}")
            break

        # セクション内のテキストを収集（10文字以上）
        if len(text) > 10:
            texts.append(text)

    result = '\n\n'.join(texts)
    print(f"[INFO] Extracted {len(texts)} paragraphs")
    print(f"[INFO] Total characters: {len(result)}")

    return result


def save_text(text: str, output_path: str) -> None:
    """
    抽出したテキストをファイルに保存する

    Args:
        text: 保存するテキスト
        output_path: 出力ファイルのパス
    """
    print(f"[INFO] Saving text to: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"[INFO] Text saved successfully")


if __name__ == "__main__":
    # デバッグ用
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    test_file = project_root / "data" / "qualitative.htm"
    output_file = project_root / "data" / "processed" / "extracted_text.txt"

    print("=" * 50)
    print("テキスト抽出テスト開始")
    print("=" * 50)

    extracted_text = extract_text_from_xbrl(str(test_file))

    print("\n" + "=" * 50)
    print("抽出結果:")
    print("=" * 50)
    print(extracted_text)
    print("\n" + "=" * 50)
    print(f"抽出文字数: {len(extracted_text)} 文字")
    print("=" * 50)

    # テキストを保存
    print()
    save_text(extracted_text, str(output_file))