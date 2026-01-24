# src/modules/youtube_upload.py

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import os
import json

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'  # 字幕アップロードに必要
]


def get_authenticated_service(client_secrets_path: str, token_path: str):
    """
    YouTube APIの認証を行い、サービスオブジェクトを返す
    トークンがあれば再利用、なければ新規認証
    """
    credentials = None

    # 保存されたトークンがあれば読み込む
    if os.path.exists(token_path):
        print("[INFO] Loading saved token...")
        with open(token_path, 'r') as token_file:
            token_data = json.load(token_file)
            credentials = Credentials.from_authorized_user_info(token_data, SCOPES)

    # トークンがないか無効な場合は新規認証
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("[INFO] Refreshing token...")
            credentials.refresh(Request())
        else:
            print("[INFO] Starting new authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, SCOPES)
            credentials = flow.run_local_server(port=0)

        # トークンを保存
        print(f"[INFO] Saving token to: {token_path}")
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        with open(token_path, 'w') as token_file:
            json.dump(token_data, token_file)

    # YouTube APIクライアント作成
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube


def upload_to_youtube(video_path: str,
                      title: str = "決算短信解説動画",
                      description: str = "決算短信の内容を音声で解説した動画です。",
                      privacy: str = "private",
                      company_name: str | None = None,
                      subtitle_path: str | None = None) -> str:
    """
    動画をYouTubeにアップロードする

    Args:
        video_path: アップロードする動画ファイルのパス
        title: 動画のタイトル
        description: 動画の説明文
        privacy: 公開設定（public/private/unlisted）
        company_name: 企業名（タグに使用）
        subtitle_path: 字幕ファイル（.srt）のパス

    Returns:
        video_id: アップロードされた動画のID
    """
    print(f"[INFO] Uploading video to YouTube: {video_path}")

    # プロジェクトルートからの絶対パスを構築
    project_root = Path(__file__).parent.parent.parent
    client_secrets_path = project_root / "data" / "client_secrets.json"
    token_path = project_root / "data" / "youtube_token.json"

    # 認証
    youtube = get_authenticated_service(str(client_secrets_path), str(token_path))

    # タグの生成
    tags = ["決算", "IR", "決算短信", "企業分析"]
    if company_name:
        tags.append(company_name)
        tags.append(f"{company_name}決算")

    # 動画メタデータ
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27'  # Education
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

    print(f"[INFO] Uploading video...")
    response = request.execute()

    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"[INFO] Video upload complete!")
    print(f"[INFO] Video ID: {video_id}")
    print(f"[INFO] Video URL: {video_url}")
    print(f"[INFO] Tags: {', '.join(tags)}")

    # 字幕ファイルのアップロード
    if subtitle_path and os.path.exists(subtitle_path):
        print(f"[INFO] Uploading subtitle: {subtitle_path}")

        caption_body = {
            'snippet': {
                'videoId': video_id,
                'language': 'ja',
                'name': '日本語字幕'
            }
        }

        media = MediaFileUpload(subtitle_path, mimetype='application/octet-stream')

        caption_request = youtube.captions().insert(
            part='snippet',
            body=caption_body,
            media_body=media
        )

        caption_response = caption_request.execute()
        print(f"[INFO] Subtitle uploaded! Caption ID: {caption_response['id']}")
    elif subtitle_path:
        print(f"[WARNING] Subtitle file not found: {subtitle_path}")

    return video_id


if __name__ == "__main__":
    # デバッグ用
    project_root = Path(__file__).parent.parent.parent
    test_video = project_root / "data" / "processed" / "output.mp4"
    test_subtitle = project_root / "data" / "processed" / "subtitle.srt"

    print("=" * 50)
    print("YouTube アップロードテスト開始")
    print("=" * 50)

    video_id = upload_to_youtube(
        video_path=str(test_video),
        title="トヨタ自動車 2024年Q4決算サマリー",
        description="トヨタ自動車の2024年第4四半期決算短信の内容を音声で解説した動画です。",
        privacy="private",
        company_name="トヨタ自動車",
        subtitle_path=str(test_subtitle) if test_subtitle.exists() else None
    )

    print("\n" + "=" * 50)
    print("アップロード完了")
    print(f"Video ID: {video_id}")
    print("=" * 50)