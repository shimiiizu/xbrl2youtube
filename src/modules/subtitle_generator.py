# src/modules/subtitle_generation.py

from moviepy import AudioFileClip
from pathlib import Path
import re


def split_text_into_chunks(text: str, max_chars: int = 40) -> list[str]:
    """
    テキストを字幕用のチャンクに分割

    Args:
        text: 分割するテキスト
        max_chars: 1行あたりの最大文字数

    Returns:
        分割されたテキストのリスト
    """
    # 句点や改行で文章を分割
    sentences = re.split(r'([。\n]+)', text)

    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

        # 空の文を無視
        if not sentence.strip():
            continue

        full_sentence = sentence + delimiter

        # 現在のチャンクに追加しても最大文字数以内なら追加
        if len(current_chunk) + len(full_sentence) <= max_chars:
            current_chunk += full_sentence
        else:
            # チャンクを保存して新しいチャンクを開始
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence

    # 最後のチャンクを追加
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def format_timestamp(seconds: float) -> str:
    """
    秒数を SRT タイムスタンプ形式に変換

    Args:
        seconds: 秒数

    Returns:
        "00:00:00,000" 形式のタイムスタンプ
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_subtitle(text_path: str, audio_path: str, output_path: str) -> None:
    """
    テキストと音声から字幕ファイル(.srt)を生成

    Args:
        text_path: テキストファイルのパス
        audio_path: 音声ファイルのパス
        output_path: 出力する字幕ファイル(.srt)のパス
    """
    print(f"[INFO] Generating subtitle from: {text_path}")

    # テキストを読み込み
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 音声の長さを取得
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    audio.close()

    print(f"[INFO] Audio duration: {total_duration:.2f} seconds")

    # テキストを字幕チャンクに分割
    chunks = split_text_into_chunks(text, max_chars=40)

    if not chunks:
        print("[WARNING] No text chunks to create subtitles")
        return

    print(f"[INFO] Created {len(chunks)} subtitle chunks")

    # 各チャンクの表示時間を計算
    duration_per_chunk = total_duration / len(chunks)

    # SRT形式で字幕を生成
    srt_content = []

    for i, chunk in enumerate(chunks):
        # 字幕番号（1から始まる）
        subtitle_number = i + 1

        # 開始・終了時間
        start_time = i * duration_per_chunk
        end_time = (i + 1) * duration_per_chunk

        # タイムスタンプを作成
        start_timestamp = format_timestamp(start_time)
        end_timestamp = format_timestamp(end_time)

        # SRT形式のエントリを作成
        srt_entry = f"{subtitle_number}\n{start_timestamp} --> {end_timestamp}\n{chunk}\n"
        srt_content.append(srt_entry)

    # ファイルに保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))

    print(f"[INFO] Subtitle saved to: {output_path}")
    print(f"[INFO] Total subtitles: {len(chunks)}")


# ===== デバッグ実行 =====
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent

    test_text = project_root / "data" / "processed" / "extracted_text.txt"
    test_audio = project_root / "data" / "processed" / "output.mp3"
    test_output = project_root / "data" / "processed" / "subtitle.srt"

    print("=" * 50)
    print("字幕生成テスト開始")
    print("=" * 50)

    if test_text.exists() and test_audio.exists():
        generate_subtitle(
            text_path=str(test_text),
            audio_path=str(test_audio),
            output_path=str(test_output)
        )

        print("\n" + "=" * 50)
        print("字幕生成完了")
        print(f"ファイル: {test_output}")
        print("=" * 50)

        # 生成された字幕の先頭を表示
        if test_output.exists():
            print("\n[プレビュー] 最初の3エントリ:")
            with open(test_output, 'r', encoding='utf-8') as f:
                content = f.read()
                entries = content.split('\n\n')[:3]
                for entry in entries:
                    print(entry)
                    print()
    else:
        print("テストファイルが見つかりません")
        print(f"テキスト: {test_text.exists()}")
        print(f"音声: {test_audio.exists()}")