# src/modules/config.py

"""
プロジェクト全体の設定を一元管理
"""


class VideoConfig:
    """動画生成の設定"""

    # 解像度
    WIDTH = 1280
    HEIGHT = 720

    # 動画設定
    FPS = 24
    CODEC = "libx264"
    AUDIO_CODEC = "aac"
    OPENING_DURATION = 3.0
    SCROLL_START_Y = 360  # スクロールテキストの開始Y座標

    # フォント
    FONT_PATH = r"C:\Windows\Fonts\YuGothB.ttc"

    # フォントサイズ（サムネイル）
    FONT_SIZE_COMPANY = 105  # 企業名
    FONT_SIZE_CODE = 42  # 株価コード
    FONT_SIZE_PER_PBR = 62  # PER・PBR
    FONT_SIZE_ROE = 40  # ROE
    FONT_SIZE_DIVIDEND = 40  # 配当利回り
    FONT_SIZE_MARKET_CAP = 40  # 時価総額
    FONT_SIZE_TAGLINE = 28  # 「さくっと決算」
    FONT_SIZE_BADGE = 36  # 「決算速報」バッジ
    FONT_SIZE_DATE = 32  # 日付

    # フォントサイズ（本編）
    FONT_SIZE_TITLE = 48  # タイトル
    FONT_SIZE_BODY = 30  # 本文スクロール

    # 色
    COLOR_GOLD = "#FFD700"  # ゴールド
    COLOR_GREEN = "#00FF00"  # 緑（PER）
    COLOR_BLUE = "#00BFFF"  # 水色（PBR）
    COLOR_YELLOW = "#FFFF00"  # 黄色（ROE）
    COLOR_PINK = "#FF69B4"  # ピンク（配当）
    COLOR_WHITE = "#FFFFFF"  # 白
    COLOR_GRAY = "#888888"  # グレー
    COLOR_RED = "#FF4444"  # 赤（バッジ背景）
    COLOR_LIGHT_GRAY = "#CCCCCC"  # ライトグレー
    COLOR_BLACK = "#000000"  # 黒

    # Y座標（サムネイルレイアウト）
    POS_Y_COMPANY = 170  # 企業名
    POS_Y_CODE = 275  # 株価コード
    POS_Y_LINE = 320  # 装飾線
    POS_Y_PER_PBR = 365  # PER・PBR
    POS_Y_ROE = 520  # ROE
    POS_Y_DIVIDEND = 520  # 配当利回り
    POS_Y_MARKET_CAP = 520  # 時価総額
    POS_Y_TAGLINE = 650  # 「さくっと決算」

    # X座標（サムネイルレイアウト）
    POS_X_PER = 380  # PER
    POS_X_PBR = 680  # PBR
    POS_X_ROE = 100  # ROE
    POS_X_DIVIDEND = 400  # 配当利回り
    POS_X_MARKET_CAP = 700  # 時価総額

    # サイズ
    SIZE_COMPANY = (1100, None)  # 企業名エリア
    SIZE_CODE = (200, None)  # 株価コードエリア
    SIZE_PER_PBR = (260, None)  # PER・PBRエリア
    SIZE_BADGE = (160, 50)  # バッジエリア

    # 装飾線
    LINE_WIDTH = 650
    LINE_HEIGHT = 3
    LINE_COLOR = (255, 215, 0)  # RGB形式（ゴールド）

    # 縁取り
    STROKE_WIDTH_COMPANY = 3  # 企業名
    STROKE_WIDTH_CODE = 1  # 株価コード
    STROKE_WIDTH_PER_PBR = 2  # PER・PBR


class PathConfig:
    """パス設定"""

    # ディレクトリ
    DATA_DIR = "data"
    PROCESSED_DIR = "data/processed"
    LOGS_DIR = "data/logs"
    DOWNLOADS_DIR = "downloads"
    ARCHIVE_DIR = "data/archive"

    # ファイル名サフィックス
    SUFFIX_QUALITATIVE_HTM = "_qualitative.htm"
    SUFFIX_EXTRACTED_TEXT = "_extracted_text.txt"
    SUFFIX_AUDIO = "_output.mp3"
    SUFFIX_SUBTITLE = "_subtitle.srt"
    SUFFIX_VIDEO = "_output.mp4"
    SUFFIX_THUMBNAIL = "_thumbnail.png"


class YouTubeConfig:
    """YouTube設定"""

    DEFAULT_PRIVACY = "public"

    # タイトルフォーマット（将来の拡張用）
    # 現在は video_helpers.py の create_video_title() で生成


class ScheduleConfig:
    """スケジュール設定"""

    SCHEDULE_FILE = "data/schedule.json"
    DEFAULT_TIME = "14:00"
    DEFAULT_COMPANY_LIMIT = 10
    DEFAULT_ENABLED = False