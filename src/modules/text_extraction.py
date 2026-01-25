# src/modules/text_extraction.py

from bs4 import BeautifulSoup
from pathlib import Path
import re


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


def extract_company_and_date_from_filename(filename: str):
    """
    ファイル名から企業名と日付を抽出

    想定形式:
    - {企業名}_{YYYYMMDD}_qualitative.htm
    - {企業名}_qualitative.htm (日付なし)

    Returns:
        tuple: (企業名, 日付 or None)
    """
    file_stem = Path(filename).stem

    # _qualitative を削除
    if file_stem.endswith('_qualitative'):
        base_name = file_stem[:-12]  # '_qualitative' を削除
    else:
        base_name = file_stem

    # アンダースコアで分割
    parts = base_name.split('_')

    if len(parts) == 1:
        # アンダースコアがない場合は全体を企業名とする
        return base_name, None

    company_name = parts[0]

    # 2番目の要素が日付（YYYYMMDD形式）かチェック
    if len(parts) >= 2 and re.match(r'^\d{8}$', parts[1]):
        pub_date = parts[1]
        return company_name, pub_date
    else:
        # 日付がない場合
        return company_name, None


if __name__ == "__main__":
    # ===== ここを変更するだけで企業を切り替え可能 =====
    COMPANY_NAME = "アジュバンＨＤ"
    PUB_DATE = "20250127"  # None にすると日付なし
    # =============================================

    project_root = Path(__file__).parent.parent.parent
    qualitative_dir = project_root / "downloads" / "qualitative"
    processed_dir = project_root / "data" / "processed"

    # ファイル名を生成
    if PUB_DATE:
        test_file = qualitative_dir / f"{COMPANY_NAME}_{PUB_DATE}_qualitative.htm"
        output_file = processed_dir / f"{COMPANY_NAME}_{PUB_DATE}_extracted_text.txt"
    else:
        test_file = qualitative_dir / f"{COMPANY_NAME}_qualitative.htm"
        output_file = processed_dir / f"{COMPANY_NAME}_extracted_text.txt"

    print("=" * 50)
    print(f"テキスト抽出テスト開始: {COMPANY_NAME}")
    if PUB_DATE:
        print(f"公開日: {PUB_DATE}")
    print("=" * 50)

    # ファイル存在確認
    print(f"[CHECK] 入力ファイル: {test_file.exists()}")

    if not test_file.exists():
        print(f"[ERROR] ファイルが見つかりません: {test_file}")
        exit(1)

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

    print("\n" + "=" * 50)
    print("テキスト抽出完了")
    print(f"出力ファイル: {output_file}")
    print("=" * 50)