# src/modules/subtitle_generation.py

import whisper
from pathlib import Path


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


def generate_subtitle(text_path: str, audio_path: str, output_path: str,
                      model_size: str = "base", company_name: str = None) -> None:
    """
    Whisperを使って音声から字幕ファイル(.srt)を生成

    Args:
        text_path: テキストファイルのパス（使用しないが互換性のため残す）
        audio_path: 音声ファイルのパス
        output_path: 出力する字幕ファイル(.srt)のパス
        model_size: Whisperモデルのサイズ ("tiny", "base", "small", "medium", "large")
        company_name: 企業名（ログ表示用）
    """
    if company_name:
        print(f"[INFO] Generating subtitle for: {company_name}")
    print(f"[INFO] Audio file: {audio_path}")
    print(f"[INFO] Loading Whisper model: {model_size}")

    # Whisperモデルをロード
    model = whisper.load_model(model_size)

    # 音声を文字起こし（タイムスタンプ付き）
    print(f"[INFO] Transcribing audio... (this may take a while)")
    result = model.transcribe(
        audio_path,
        language="ja",
        verbose=False,
        word_timestamps=True
    )

    # セグメント（文章の区切り）を取得
    segments = result['segments']

    if not segments:
        print("[WARNING] No segments found in transcription")
        return

    print(f"[INFO] Created {len(segments)} subtitle segments")

    # SRT形式で字幕を生成
    srt_content = []

    for i, segment in enumerate(segments):
        subtitle_number = i + 1
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip()

        start_timestamp = format_timestamp(start_time)
        end_timestamp = format_timestamp(end_time)

        srt_entry = f"{subtitle_number}\n{start_timestamp} --> {end_timestamp}\n{text}\n"
        srt_content.append(srt_entry)

    # ファイルに保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))

    print(f"[INFO] Subtitle saved to: {output_path}")
    print(f"[INFO] Total subtitles: {len(segments)}")

    # 文字起こし結果も表示
    print(f"[INFO] Transcribed text preview:")
    full_text = ' '.join([seg['text'].strip() for seg in segments[:3]])
    print(f"  {full_text}...")