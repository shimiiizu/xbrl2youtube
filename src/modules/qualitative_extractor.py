"""
downloadsのzipフォルダ内のZIPファイルを解凍して
qualitative.htmファイルだけを抽出する
"""

import zipfile
from pathlib import Path
import shutil


class QualitativeExtractor:
    def __init__(self, zip_dir="downloads/zip", output_dir="downloads/qualitative"):
        # プロジェクトルートからの絶対パスを構築
        project_root = Path(__file__).parent.parent.parent
        self.zip_dir = project_root / zip_dir
        self.output_dir = project_root / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_qualitative_files(self):
        """すべてのZIPファイルからqualitative.htmを抽出"""
        print(f"=== ZIP解凍開始 ===")
        print(f"検索フォルダ: {self.zip_dir}")
        print(f"出力フォルダ: {self.output_dir}")

        # ZIPファイル一覧を取得
        zip_files = list(self.zip_dir.glob("*.zip"))
        print(f"\n検出されたZIPファイル数: {len(zip_files)}")

        if not zip_files:
            print("[警告] ZIPファイルが見つかりません")
            return 0

        extracted_count = 0

        for zip_path in zip_files:
            print(f"\n処理中: {zip_path.name}")

            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    # ZIP内のファイル一覧を取得
                    file_list = zf.namelist()

                    # qualitative.htmを探す
                    qualitative_files = [f for f in file_list if f.lower().endswith('qualitative.htm')]

                    if not qualitative_files:
                        print(f"  [SKIP] qualitative.htmが見つかりません")
                        continue

                    # 見つかったqualitative.htmを抽出
                    for qual_file in qualitative_files:
                        # 元のZIPファイル名から企業名を抽出
                        # ファイル名形式: {企業名}_{元のファイル名}.zip
                        zip_base_name = zip_path.stem
                        # 最初のアンダースコアまでを企業名とする
                        parts = zip_base_name.split('_', 1)
                        if len(parts) >= 1:
                            company_name = parts[0]
                        else:
                            company_name = zip_base_name

                        output_filename = f"{company_name}_qualitative.htm"
                        output_path = self.output_dir / output_filename

                        # ファイルを抽出
                        with zf.open(qual_file) as source:
                            with open(output_path, 'wb') as target:
                                shutil.copyfileobj(source, target)

                        print(f"  [OK] 抽出完了: {output_filename}")
                        extracted_count += 1

            except zipfile.BadZipFile:
                print(f"  [ERROR] 破損したZIPファイル: {zip_path.name}")
            except Exception as e:
                print(f"  [ERROR] {type(e).__name__}: {e}")

        print(f"\n=== 処理完了 ===")
        print(f"抽出されたファイル数: {extracted_count}")
        print(f"保存先: {self.output_dir}")

        return extracted_count


# -------------------------------------------------
if __name__ == "__main__":
    extractor = QualitativeExtractor()
    extractor.extract_qualitative_files()