"""
アプリケーション設定
環境変数から設定値を読み込む
"""
import os
from typing import Optional


class Settings:
    """アプリケーション設定クラス"""
    
    # DynamoDB テーブル名（管理者機能）
    ARTICLES_TABLE_NAME: str = os.environ.get('ARTICLES_TABLE_NAME', 'articles')
    COMPANIES_TABLE_NAME: str = os.environ.get('COMPANIES_TABLE_NAME', 'companies')
    STORES_TABLE_NAME: str = os.environ.get('STORES_TABLE_NAME', 'stores')
    FLYERS_TABLE_NAME: str = os.environ.get('FLYERS_TABLE_NAME', 'flyers')
    ADMINS_TABLE_NAME: str = os.environ.get('ADMINS_TABLE_NAME', 'admins')

    # DynamoDB テーブル名（ユーザー機能）
    USERS_TABLE_NAME: str = os.environ.get('USERS_TABLE_NAME', 'users')
    FAVORITE_STORES_TABLE_NAME: str = os.environ.get('FAVORITE_STORES_TABLE_NAME', 'favorite-stores')
    RECIPES_TABLE_NAME: str = os.environ.get('RECIPES_TABLE_NAME', 'recipes')
    SHARED_RECIPES_TABLE_NAME: str = os.environ.get('SHARED_RECIPES_TABLE_NAME', 'shared-recipes')

    # AWS設定
    AWS_REGION: str = os.environ.get('AWS_REGION', 'ap-northeast-1')
    DYNAMODB_ENDPOINT_URL: Optional[str] = os.environ.get('DYNAMODB_ENDPOINT_URL')  # ローカル開発用

    # S3設定
    S3_BUCKET_NAME: str = os.environ.get('S3_BUCKET_NAME', 'images')
    S3_FLYERS_FOLDER: str = 'flyers'
    S3_ARTICLES_FOLDER: str = 'articles'
    S3_LOGOS_FOLDER: str = 'logos'
    
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