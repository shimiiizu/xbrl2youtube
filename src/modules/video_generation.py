# src/modules/video_generation.py

from moviepy.editor import AudioFileClip, ColorClip


def generate_video(audio_path: str, output_path: str) -> None:
    """
    音声ファイルから動画ファイルを生成する（静止画+音声）

    Args:
        audio_path: 音声ファイルのパス（MP3）
        output_path: 出力する動画ファイルのパス（MP4）
    """
    print(f"[INFO] Reading audio from: {audio_path}")

    # 音声ファイルを読み込む
    audio = AudioFileClip(audio_path)

    print(f"[INFO] Generating video...")
    print(f"[INFO] Audio duration: {audio.duration} seconds")

    # 黒い静止画を作成（音声の長さに合わせる）
    video = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=audio.duration)

    # 音声を動画に追加
    video = video.set_audio(audio)

    # MP4として出力
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac'
    )

    print(f"[INFO] Video saved to: {output_path}")


if __name__ == "__main__":
    # デバッグ用
    test_audio = "../../data/processed/output.mp3"
    test_output = "../../data/processed/output.mp4"

    print("=" * 50)
    print("動画生成テスト開始")
    print("=" * 50)

    generate_video(test_audio, test_output)

    print("\n" + "=" * 50)
    print("動画生成完了")
    print(f"ファイル: {test_output}")
    print("=" * 50)