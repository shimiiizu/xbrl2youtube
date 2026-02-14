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


def load_playlists(playlists_path: str) -> dict:
    """
    再生リストの対応表をJSONから読み込む

    Args:
        playlists_path: playlists.jsonのパス

    Returns:
        企業名 -> プレイリストID の辞書
    """
    if os.path.exists(playlists_path):
        with open(playlists_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_playlists(playlists_path: str, playlists: dict) -> None:
    """
    再生リストの対応表をJSONに保存する

    Args:
        playlists_path: playlists.jsonのパス
        playlists: 企業名 -> プレイリストID の辞書
    """
    os.makedirs(os.path.dirname(playlists_path), exist_ok=True)
    with open(playlists_path, 'w', encoding='utf-8') as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)


def create_playlist(youtube, company_name: str) -> str:
    """
    企業名で新しい再生リストを作成する

    Args:
        youtube: YouTube APIクライアント
        company_name: 企業名

    Returns:
        作成された再生リストのID
    """
    playlist_title = f"【{company_name}】決算シリーズ"
    playlist_description = f"{company_name}の決算短信を解説する動画シリーズです。"

    print(f"[INFO] Creating new playlist: {playlist_title}")

    playlist_body = {
        'snippet': {
            'title': playlist_title,
            'description': playlist_description,
            'defaultLanguage': 'ja'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    request = youtube.playlists().insert(
        part='snippet,status',
        body=playlist_body
    )

    response = request.execute()
    playlist_id = response['id']

    print(f"[INFO] Playlist created! ID: {playlist_id}")
    return playlist_id


def add_video_to_playlist(youtube, playlist_id: str, video_id: str) -> None:
    """
    動画を再生リストに追加する

    Args:
        youtube: YouTube APIクライアント
        playlist_id: 再生リストのID
        video_id: 動画のID
    """
    print(f"[INFO] Adding video to playlist: {playlist_id}")

    playlist_item_body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            }
        }
    }

    request = youtube.playlistItems().insert(
        part='snippet',
        body=playlist_item_body
    )

    response = request.execute()
    print(f"[INFO] Video added to playlist successfully!")


def get_or_create_playlist(youtube, company_name: str, playlists_path: str) -> str:
    """
    企業名に対応する再生リストを取得または作成する

    Args:
        youtube: YouTube APIクライアント
        company_name: 企業名
        playlists_path: playlists.jsonのパス

    Returns:
        再生リストのID
    """
    # 既存の対応表を読み込む
    playlists = load_playlists(playlists_path)

    # 企業名が既に登録されているか確認
    if company_name in playlists:
        playlist_id = playlists[company_name]
        print(f"[INFO] Using existing playlist for {company_name}: {playlist_id}")
        return playlist_id

    # 新規作成
    playlist_id = create_playlist(youtube, company_name)

    # 対応表に追加して保存
    playlists[company_name] = playlist_id
    save_playlists(playlists_path, playlists)

    return playlist_id


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
                      subtitle_path: str | None = None,
                      thumbnail_path: str | None = None) -> str:
    """
    動画をYouTubeにアップロードする

    Args:
        video_path: アップロードする動画ファイルのパス
        title: 動画のタイトル
        description: 動画の説明文
        privacy: 公開設定（public/private/unlisted）
        company_name: 企業名（タグに使用、再生リストに自動追加）
        subtitle_path: 字幕ファイル（.srt）のパス
        thumbnail_path: サムネイル画像ファイル（.png/.jpg）のパス

    Returns:
        video_id: アップロードされた動画のID
    """
    print(f"[INFO] Uploading video to YouTube: {video_path}")

    # プロジェクトルートからの絶対パスを構築
    project_root = Path(__file__).parent.parent.parent
    client_secrets_path = project_root / "data" / "json" / "client_secrets.json"
    token_path = project_root / "data" / "json" / "youtube_token.json"
    playlists_path = project_root / "data" / "json" / "playlists.json"

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

    # サムネイル画像のアップロード
    if thumbnail_path and os.path.exists(thumbnail_path):
        print(f"[INFO] Uploading thumbnail: {thumbnail_path}")

        try:
            thumbnail_media = MediaFileUpload(thumbnail_path)

            thumbnail_request = youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumbnail_media
            )

            thumbnail_response = thumbnail_request.execute()
            print(f"[INFO] Thumbnail uploaded successfully!")

            # サムネイルのURLを表示（利用可能な場合）
            if 'items' in thumbnail_response and len(thumbnail_response['items']) > 0:
                thumb_url = thumbnail_response['items'][0].get('default', {}).get('url', 'N/A')
                print(f"[INFO] Thumbnail URL: {thumb_url}")

        except Exception as e:
            print(f"[ERROR] Failed to upload thumbnail: {e}")
            print(f"[WARNING] Video was uploaded successfully, but thumbnail upload failed.")

    elif thumbnail_path:
        print(f"[WARNING] Thumbnail file not found: {thumbnail_path}")
        print(f"[INFO] Video uploaded without custom thumbnail.")

    # 再生リストに追加（企業名が指定されている場合）
    if company_name:
        try:
            print(f"\n[INFO] Managing playlist for: {company_name}")
            playlist_id = get_or_create_playlist(youtube, company_name, str(playlists_path))
            add_video_to_playlist(youtube, playlist_id, video_id)
            print(f"[INFO] Playlist URL: https://www.youtube.com/playlist?list={playlist_id}")
        except Exception as e:
            print(f"[ERROR] Failed to add video to playlist: {e}")
            print(f"[WARNING] Video was uploaded successfully, but playlist operation failed.")

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
    # ===== ここを変更するだけで企業を切り替え可能 =====
    COMPANY_NAME = "ヒガシＨＤ"
    # =============================================

    project_root = Path(__file__).parent.parent.parent
    processed_dir = project_root / "data" / "processed"

    # 企業名から各ファイルパスを自動生成
    test_video = processed_dir / f"{COMPANY_NAME}_output.mp4"
    test_subtitle = processed_dir / f"{COMPANY_NAME}_subtitle.srt"
    test_thumbnail = processed_dir / f"{COMPANY_NAME}_thumbnail.png"

    print("=" * 50)
    print(f"YouTube アップロードテスト開始: {COMPANY_NAME}")
    print("=" * 50)

    # ファイル存在確認
    print(f"[CHECK] 動画ファイル: {test_video.exists()}")
    print(f"[CHECK] 字幕ファイル: {test_subtitle.exists()}")
    print(f"[CHECK] サムネイル: {test_thumbnail.exists()}")

    if not test_video.exists():
        print(f"[ERROR] 動画ファイルが見つかりません: {test_video}")
        exit(1)

    video_id = upload_to_youtube(
        video_path=str(test_video),
        title=f"{COMPANY_NAME} 決算サマリー",
        description=f"{COMPANY_NAME}の決算短信の内容を音声で解説した動画です。",
        privacy="private",
        company_name=COMPANY_NAME,
        subtitle_path=str(test_subtitle) if test_subtitle.exists() else None,
        thumbnail_path=str(test_thumbnail) if test_thumbnail.exists() else None
    )

    print("\n" + "=" * 50)
    print("アップロード完了")
    print(f"Video ID: {video_id}")
    print("=" * 50)