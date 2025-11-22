"""
ロギングユーティリティ
"""
import logging
import json
from typing import Any, Dict

from config.settings import settings


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名
    
    Returns:
        ロガーインスタンス
    """
    logger = logging.getLogger(name)
    
    # 既にハンドラーが設定されている場合はスキップ
    if logger.handlers:
        return logger
    
    logger.setLevel(settings.LOG_LEVEL)
    
    # コンソールハンドラー
    handler = logging.StreamHandler()
    handler.setLevel(settings.LOG_LEVEL)
    
    # フォーマット
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def log_event(logger: logging.Logger, event: Dict[str, Any]) -> None:
    """
    Lambda イベントをログ出力
    
    Args:
        logger: ロガー
        event: Lambdaイベント
    """
    # 本番環境では詳細をログ出力しない
    if settings.is_production():
        logger.info(f"Event received: {event.get('httpMethod')} {event.get('path')}")
    else:
        logger.debug(f"Event: {json.dumps(event, ensure_ascii=False, default=str)}")


def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    エラーをログ出力
    
    Args:
        logger: ロガー
        error: 例外オブジェクト
        context: エラーのコンテキスト情報
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)