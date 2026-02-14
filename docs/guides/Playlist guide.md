# YouTube 再生リスト自動管理機能

## 概要
企業ごとに再生リストを自動作成・管理する機能です。同じ企業の動画を自動的に同じ再生リストに追加します。

## 機能

### 1. 初回アップロード時
- 企業名で再生リスト「【{企業名}】決算シリーズ」を自動作成
- 説明文：「{企業名}の決算短信を解説する動画シリーズです。」
- 公開設定：public（常時）
- プレイリストIDを `data/json/playlists.json` に保存

### 2. 2回目以降のアップロード
- `data/json/playlists.json` から企業名に対応するプレイリストIDを取得
- 既存の再生リストに動画を自動追加

## ファイル構造

```
data/
└── json/
    ├── client_secrets.json     # OAuth認証情報
    ├── youtube_token.json      # アクセストークン
    └── playlists.json          # 企業名とプレイリストIDの対応表（自動生成）
```

### playlists.json の例
```json
{
  "ヒガシＨＤ": "PLxxxxxxxxxxxxxxxxxx",
  "カーバイド": "PLyyyyyyyyyyyyyyyyyy",
  "トヨタ自動車": "PLzzzzzzzzzzzzzzzzzz"
}
```

## 使い方

### 基本的な使用方法

```python
from youtube_upload import upload_to_youtube

# 動画をアップロード（企業名を指定すると自動的に再生リストに追加）
video_id = upload_to_youtube(
    video_path="data/processed/ヒガシＨＤ_20250214_output.mp4",
    title="ヒガシＨＤ 決算サマリー",
    description="ヒガシＨＤの決算内容を解説します。",
    privacy="private",
    company_name="ヒガシＨＤ",  # ← これが重要！
    subtitle_path="data/processed/ヒガシＨＤ_20250214_subtitle.srt",
    thumbnail_path="data/processed/ヒガシＨＤ_20250214_thumbnail.png"
)
```

### 実行例

```bash
# コマンドラインから実行
python src/modules/youtube_upload.py
```

実行時のログ例：
```
[INFO] Uploading video to YouTube: data/processed/ヒガシＨＤ_output.mp4
[INFO] Uploading video...
[INFO] Video upload complete!
[INFO] Video ID: xxxxxxxxxxx
[INFO] Video URL: https://www.youtube.com/watch?v=xxxxxxxxxxx
[INFO] Tags: 決算, IR, 決算短信, 企業分析, ヒガシＨＤ, ヒガシＨＤ決算
[INFO] Uploading thumbnail: data/processed/ヒガシＨＤ_thumbnail.png
[INFO] Thumbnail uploaded successfully!

[INFO] Managing playlist for: ヒガシＨＤ
[INFO] Creating new playlist: 【ヒガシＨＤ】決算シリーズ
[INFO] Playlist created! ID: PLxxxxxxxxxxxxxxxxxx
[INFO] Adding video to playlist: PLxxxxxxxxxxxxxxxxxx
[INFO] Video added to playlist successfully!
[INFO] Playlist URL: https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxx

[INFO] Uploading subtitle: data/processed/ヒガシＨＤ_subtitle.srt
[INFO] Subtitle uploaded! Caption ID: yyyyyyyyyyyyyyy
```

### 2回目以降の実行

```
[INFO] Managing playlist for: ヒガシＨＤ
[INFO] Using existing playlist for ヒガシＨＤ: PLxxxxxxxxxxxxxxxxxx
[INFO] Adding video to playlist: PLxxxxxxxxxxxxxxxxxx
[INFO] Video added to playlist successfully!
```

## 処理の流れ

```
1. 動画をアップロード
   ↓
2. サムネイルを設定
   ↓
3. 企業名で再生リスト検索
   ├─ 存在する → 既存リストに追加
   └─ 存在しない → 新規作成 → リストに追加 → playlists.jsonに保存
   ↓
4. 字幕をアップロード
```

## 再生リストの管理

### 手動で再生リストを確認

```python
import json

# playlists.jsonを読み込む
with open('data/json/playlists.json', 'r', encoding='utf-8') as f:
    playlists = json.load(f)

# 企業ごとのプレイリストIDを表示
for company, playlist_id in playlists.items():
    url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"{company}: {url}")
```

### 特定企業の再生リストを削除

```python
import json

# playlists.jsonから企業を削除（次回は新規作成される）
with open('data/json/playlists.json', 'r', encoding='utf-8') as f:
    playlists = json.load(f)

# 削除したい企業名
del playlists['ヒガシＨＤ']

# 保存
with open('data/json/playlists.json', 'w', encoding='utf-8') as f:
    json.dump(playlists, f, ensure_ascii=False, indent=2)
```

## トラブルシューティング

### Q1: 再生リストが作成されない

**確認事項**:
- `company_name` パラメータが正しく指定されているか確認
- YouTube APIの認証が正しく行われているか確認
- YouTube Data APIのクォータが残っているか確認（再生リスト作成: 50 units）

### Q2: playlists.jsonが見つからない

**対処法**:
初回実行時に自動作成されます。手動で作成する場合：

```bash
mkdir -p data/json
echo "{}" > data/json/playlists.json
```

### Q3: 間違った再生リストに追加されてしまった

**対処法**:
1. YouTube Studioで手動で動画を正しい再生リストに移動
2. `playlists.json` を編集して正しいプレイリストIDを設定

### Q4: 再生リストをリセットしたい

**対処法**:
```bash
# playlists.jsonをバックアップ
cp data/json/playlists.json data/json/playlists.json.backup

# 空の状態に戻す
echo "{}" > data/json/playlists.json

# または特定の企業のみ削除
# （上記「特定企業の再生リストを削除」を参照）
```

## API使用量（クォータ）

YouTube Data API v3 の使用量：

| 操作 | コスト（units） |
|------|----------------|
| 動画アップロード | 1,600 |
| サムネイル設定 | 50 |
| 再生リスト作成 | 50 |
| 再生リストに追加 | 50 |
| 字幕アップロード | 50 |
| **合計（初回）** | **1,800** |
| **合計（2回目以降）** | **1,750** |

デフォルトの1日のクォータ: 10,000 units
→ 1日あたり約5〜6本の動画をアップロード可能

## 注意事項

1. **再生リストは常にpublic**: 動画がprivateでも再生リストはpublicになります
2. **企業名の一貫性**: 「トヨタ」と「トヨタ自動車」は別の再生リストになります
3. **JSONファイルのバックアップ**: `playlists.json` を定期的にバックアップすることを推奨

## 将来の拡張案

- 月別・四半期別の再生リスト自動作成
- 業種別の再生リスト自動作成
- 再生リストの並び順の自動調整（日付順など）
- 古い動画の自動アーカイブ化