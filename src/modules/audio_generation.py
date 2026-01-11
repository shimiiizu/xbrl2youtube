# src/modules/audio_generation.py

from gtts import gTTS


def generate_audio(text: str, output_path: str) -> None:
    """
    テキストから音声ファイル（MP3）を生成する

    Args:
        text: 読み上げるテキスト
        output_path: 出力する音声ファイルのパス（MP3）
    """
    print(f"[INFO] Generating audio from text...")
    print(f"[INFO] Text length: {len(text)} characters")

    # 日本語でTTS生成
    tts = gTTS(text=text, lang='ja')

    # MP3として保存
    tts.save(output_path)

    print(f"[INFO] Audio saved to: {output_path}")


if __name__ == "__main__":
    # デバッグ用
    test_text = "これは音声生成のテストです。決算短信の内容を読み上げます。"
    test_output = "../../data/processed/test_output.mp3"

    print("=" * 50)
    print("音声生成テスト開始")
    print("=" * 50)

    generate_audio(test_text, test_output)

    print("\n" + "=" * 50)
    print("音声生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)