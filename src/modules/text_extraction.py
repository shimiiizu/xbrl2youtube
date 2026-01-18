# src/modules/text_extraction.py

from bs4 import BeautifulSoup


def extract_text_from_xbrl(file_path: str) -> str:
    """
    HTMLファイルから「（１）経営成績」セクションのテキストを抽出する
    h1, h2, h3タグで開始・終了を判定し、その間のpタグを収集する
    pタグ内にも終了キーワードがあればそこで終了

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

    # 開始キーワード
    start_keywords = [
        "経営成績",
        "(1)経営成績"
    ]

    # 終了キーワード
    end_keywords = [
        "財政状態",
        "(2)財政状態"
    ]

    # h1, h2, h3, pタグを順番に処理
    for element in soup.find_all(['h1', 'h2', 'h3', 'p']):

        if element.name in ['h1', 'h2', 'h3']:
            header_text = element.get_text(strip=True)

            # 開始判定
            if not in_target_section:
                for keyword in start_keywords:
                    if keyword in header_text:
                        in_target_section = True
                        print(f"[INFO] Found start section ({element.name}): {header_text}")
                        break
            else:
                # 終了判定
                for keyword in end_keywords:
                    if keyword in header_text:
                        print(f"[INFO] Found end section ({element.name}): {header_text}")
                        in_target_section = False
                        break

                # 終了したらループを抜ける
                if not in_target_section:
                    break

        elif element.name == 'p':
            text = element.get_text(strip=True)

            # 空のテキストや空白のみはスキップ
            if not text or text == '　':
                continue

            # pタグ内でも終了キーワードをチェック
            if in_target_section:
                for keyword in end_keywords:
                    if keyword in text:
                        print(f"[INFO] Found end keyword in p tag: {text[:50]}...")
                        in_target_section = False
                        break

                # 終了したらループを抜ける
                if not in_target_section:
                    break

                # 10文字以上のテキストを収集
                if len(text) > 15:
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
    test_file = project_root / "downloads" / "qualitative" / "アジュバンＨＤ_qualitative.htm"
    output_file = project_root / "data" / "processed" / "extracted_text.txt"

    print("=" * 50)
    print("テキスト抽出テスト開始")
    print("=" * 50)

    extracted_text = extract_text_from_xbrl(str(test_file))

    print("\n" + "=" * 50)
    print("抽出結果プレビュー:")
    print("=" * 50)
    print(extracted_text[:500])  # 最初の500文字だけ表示
    print("\n..." if len(extracted_text) > 500 else "")
    print("\n" + "=" * 50)
    print(f"抽出文字数: {len(extracted_text)} 文字")
    print("=" * 50)

    # テキストを保存
    print()
    save_text(extracted_text, str(output_file))