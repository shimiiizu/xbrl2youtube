# src/modules/youtube_upload.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import os


def upload_to_youtube(video_path: str, title: str = "決算短信解説動画",
                      description: str = "決算短信の内容を音声で解説した動画です。",
                      privacy: str = "private") -> None:
    """
    動画をYouTubeにアップロードする

    Args:
        video_path: アップロードする動画ファイルのパス
        title: 動画のタイトル
        description: 動画の説明文
        privacy: 公開設定（public/private/unlisted）
    """
    print(f"[INFO] Uploading video to YouTube: {video_path}")

    # OAuth 2.0認証
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    # プロジェクトルートからの絶対パスを構築
    project_root = Path(__file__).parent.parent.parent
    client_secrets_path = project_root / "data" / "client_secrets.json"

    # 認証情報の読み込み
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secrets_path), SCOPES)
    credentials = flow.run_local_server(port=0)

    # YouTube APIクライアント作成
    youtube = build('youtube', 'v3', credentials=credentials)

    # 動画メタデータ
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': '22'  # People & Blogs
        },
        'status': {
            'privacyStatus': privacy
        }
    }

    # 動画ファイルをアップロード
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    print(f"[INFO] Uploading...")
    response = request.execute()

    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"[INFO] Upload complete!")
    print(f"[INFO] Video ID: {video_id}")
    print(f"[INFO] Video URL: {video_url}")


if __name__ == "__main__":
    # デバッグ用
    project_root = Path(__file__).parent.parent.parent
    test_video = project_root / "data" / "processed" / "output.mp4"

    print("=" * 50)
    print("YouTube アップロードテスト開始")
    print("=" * 50)

    upload_to_youtube(str(test_video), privacy="private")

    print("\n" + "=" * 50)
    print("アップロード完了")
    print("=" * 50)