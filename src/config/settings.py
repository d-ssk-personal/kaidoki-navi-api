"""
アプリケーション設定
環境変数から設定値を読み込む
"""
import os
from typing import Optional


class Settings:
    """アプリケーション設定クラス"""
    
    # DynamoDB テーブル名
    PRODUCTS_TABLE_NAME: str = os.environ.get('PRODUCTS_TABLE_NAME', 'kaidoki-navi-products')
    PRICE_HISTORY_TABLE_NAME: str = os.environ.get('PRICE_HISTORY_TABLE_NAME', 'kaidoki-navi-price-history')
    USERS_TABLE_NAME: str = os.environ.get('USERS_TABLE_NAME', 'kaidoki-navi-users')
    FAVORITES_TABLE_NAME: str = os.environ.get('FAVORITES_TABLE_NAME', 'kaidoki-navi-favorites')
    NOTIFICATION_SETTINGS_TABLE_NAME: str = os.environ.get('NOTIFICATION_SETTINGS_TABLE_NAME', 'kaidoki-navi-notification-settings')
    CATEGORIES_TABLE_NAME: str = os.environ.get('CATEGORIES_TABLE_NAME', 'kaidoki-navi-categories')
    
    # AWS設定
    AWS_REGION: str = os.environ.get('AWS_REGION', 'ap-northeast-1')
    
    # 認証設定
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = 24
    
    # OpenAI API
    OPENAI_API_KEY: Optional[str] = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL: str = 'gpt-3.5-turbo'
    
    # LINE Messaging API
    LINE_CHANNEL_ACCESS_TOKEN: Optional[str] = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET: Optional[str] = os.environ.get('LINE_CHANNEL_SECRET')
    
    # ページネーション
    DEFAULT_PAGE_LIMIT: int = 20
    MAX_PAGE_LIMIT: int = 100
    
    # 価格履歴
    PRICE_HISTORY_DEFAULT_DAYS: int = 30
    PRICE_HISTORY_MAX_DAYS: int = 180
    
    # 通知設定
    DEFAULT_PRICE_CHANGE_THRESHOLD: int = 5  # %
    
    # ログレベル
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 環境
    ENVIRONMENT: str = os.environ.get('ENVIRONMENT', 'development')
    
    @classmethod
    def is_production(cls) -> bool:
        """本番環境かどうか"""
        return cls.ENVIRONMENT == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """開発環境かどうか"""
        return cls.ENVIRONMENT == 'development'


# シングルトンインスタンス
settings = Settings()