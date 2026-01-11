# src/modules/audio_generation.py

from gtts import gTTS


def generate_audio(text_path: str, output_path: str) -> None:
    """
    テキストファイルから音声ファイル（MP3）を生成する

    Args:
        text_path: 読み上げるテキストファイルのパス
        output_path: 出力する音声ファイルのパス（MP3）
    """
    print(f"[INFO] Reading text from: {text_path}")

    # テキストファイルを読み込む
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] Generating audio from text...")
    print(f"[INFO] Text length: {len(text)} characters")

    # 日本語でTTS生成
    tts = gTTS(text=text, lang='ja')

    # MP3として保存
    tts.save(output_path)

    print(f"[INFO] Audio saved to: {output_path}")


if __name__ == "__main__":
    # デバッグ用
    test_text_file = "../../data/processed/extracted_text.txt"
    test_output = "../../data/processed/output.mp3"

    print("=" * 50)
    print("音声生成テスト開始")
    print("=" * 50)

    generate_audio(test_text_file, test_output)

    print("\n" + "=" * 50)
    print("音声生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)