# xbrl2youtube
xbrlファイルからテキストデータを抽出し、音声データに変換したのち、画像データと合わせて動画を作成し、youtubeにUploadする。

## 機能
### ✅Tdnetから『zipファイル』をダウンロードする。
### 『zipファイル』を解凍して、qualitative.htmを抽出する。
### ✅『qualitative.htm』からテキスト情報（経営状況）を抽出する。
### ✅テキスト情報から音声データを作成する。
### ✅音声データから動画を生成する。
### ✅動画をYoutubeにアップロードする。


project_root/
│
├── data/                   # 入力ファイル（XBRL）を格納
│   └── processed/        # 処理後のファイル（テキスト化、音声ファイルなど）
│
├── src/main.py                   # メインのソースコード
│   ├── text_extraction.py   # XBRLからテキストを抽出するモジュール
│   ├── audio_generation.py  # 音声ファイルを生成するモジュール
│   ├── video_generation.py  # 動画を生成するモジュール
│   └── youtube_upload.py    # YouTubeへアップロードするモジュール
│
├── tests/                  # テストコード
│   ├── data_extraction/   # data_extractionモジュールのテスト
│   ├── text_processing/   # text_processingモジュールのテスト
│   ├── audio_generation/   # audio_generationモジュールのテスト
│   ├── video_generation/   # video_generationモジュールのテスト
│   └── youtube_upload/    # youtube_uploadモジュールのテスト
│
├── docs/                   # ドキュメント
│   └── guides/               # 使用方法や設計に関するドキュメント
│
├── scripts/                # 補助的なスクリプト（データ変換など）
│
└── requirements.txt   # 必要なパッケージ一覧

### Tdnetから『zipファイル』をダウンロードする。
- TdnetのAPI（https://webapi.yanoshin.jp/tdnet/）
- を使用して、指定した企業コードと日付に基づいてzipファイルをダウンロードします。
