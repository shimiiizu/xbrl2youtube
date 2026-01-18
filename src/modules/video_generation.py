# src/modules/video_generation.py

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from pathlib import Path


def generate_video(audio_path: str, output_path: str, text_content: str = None) -> None:
    """
    音声ファイルから動画ファイルを生成する（静止画+音声+テキスト表示）

    Args:
        audio_path: 音声ファイルのパス（MP3）
        output_path: 出力する動画ファイルのパス（MP4）
        text_content: 表示するテキスト（省略時は音声のみ）
    """
    print(f"[INFO] Reading audio from: {audio_path}")

    # 音声ファイルを読み込む
    audio = AudioFileClip(audio_path)

    print(f"[INFO] Generating video...")
    print(f"[INFO] Audio duration: {audio.duration} seconds")

    # 黒い背景を作成（音声の長さに合わせる）
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio.duration)

    # テキストを表示する場合
    if text_content:
        print(f"[INFO] Adding text overlay...")

        # テキストを適切な長さで分割（画面に収まるように）
        max_chars_per_line = 40
        words = text_content.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        # 最大15行まで表示
        display_text = "\n".join(lines[:15])

        # テキストクリップを作成
        txt_clip = TextClip(
            text=display_text,
            font_size=24,
            color='white',
            size=(1200, 650),
            method='caption'
        ).with_position(('center', 'center')).with_duration(audio.duration)

        # 背景とテキストを合成
        video = CompositeVideoClip([background, txt_clip])
    else:
        video = background

    # 音声を動画に追加
    video = video.with_audio(audio)

    # MP4として出力
    print(f"[INFO] Writing video file...")
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac'
    )

    print(f"[INFO] Video saved to: {output_path}")


if __name__ == "__main__":
    # デバッグ用
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    test_audio = project_root / "data" / "processed" / "output.mp3"
    test_text = project_root / "data" / "processed" / "extracted_text.txt"
    test_output = project_root / "data" / "processed" / "output.mp4"

    print("=" * 50)
    print("動画生成テスト開始")
    print("=" * 50)

    # テキストファイルを読み込み
    text_content = None
    if test_text.exists():
        with open(test_text, 'r', encoding='utf-8') as f:
            text_content = f.read()
        print(f"[INFO] テキストファイル読み込み: {len(text_content)} 文字")

    generate_video(str(test_audio), str(test_output), text_content)

    print("\n" + "=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)