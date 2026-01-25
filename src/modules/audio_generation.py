# src/modules/audio_generation.py

from gtts import gTTS
import librosa
import soundfile as sf
from pathlib import Path
import os


def generate_audio(text_path: str, output_path: str, speed: float = 1.3) -> None:
    """
    テキストファイルから音声ファイル（MP3）を生成する

    Args:
        text_path: 読み上げるテキストファイルのパス
        output_path: 出力する音声ファイルのパス（MP3）
        speed: 再生速度（1.0が通常速度、1.3が1.3倍速）
    """
    print(f"[INFO] Reading text from: {text_path}")

    # テキストファイルを読み込む
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] Generating audio from text...")
    print(f"[INFO] Text length: {len(text)} characters")
    print(f"[INFO] Speed: {speed}x")

    # 日本語でTTS生成
    tts = gTTS(text=text, lang='ja')

    # 一時ファイルとして保存
    temp_path = output_path.replace('.mp3', '_temp.mp3')
    tts.save(temp_path)

    # 速度調整
    y, sr = librosa.load(temp_path)
    y_fast = librosa.effects.time_stretch(y, rate=speed)
    sf.write(output_path, y_fast, sr)

    # 一時ファイル削除
    os.remove(temp_path)

    print(f"[INFO] Audio saved to: {output_path}")


if __name__ == "__main__":
    # ===== ここを変更するだけで企業を切り替え可能 =====
    COMPANY_NAME = "アジュバンＨＤ"
    PUB_DATE = "20250127"  # None にすると日付なし
    # =============================================

    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data" / "processed"

    # ファイル名を生成
    if PUB_DATE:
        test_text_file = processed_dir / f"{COMPANY_NAME}_{PUB_DATE}_extracted_text.txt"
        test_output = processed_dir / f"{COMPANY_NAME}_{PUB_DATE}_audio.mp3"
    else:
        test_text_file = processed_dir / f"{COMPANY_NAME}_extracted_text.txt"
        test_output = processed_dir / f"{COMPANY_NAME}_audio.mp3"

    print("=" * 50)
    print(f"音声生成テスト開始: {COMPANY_NAME}")
    if PUB_DATE:
        print(f"公開日: {PUB_DATE}")
    print("=" * 50)

    # ファイル存在確認
    print(f"[CHECK] 入力ファイル: {test_text_file.exists()}")

    if not test_text_file.exists():
        print(f"[ERROR] テキストファイルが見つかりません: {test_text_file}")
        exit(1)

    generate_audio(str(test_text_file), str(test_output), speed=1.3)

    print("\n" + "=" * 50)
    print("音声生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)