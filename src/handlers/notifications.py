"""
通知設定関連のLambda関数ハンドラー
"""
import json
from typing import Dict, Any

from src.repositories.notification_repository import NotificationRepository
from src.utils.response import (
    success_response,
    bad_request_response,
    unauthorized_response,
    internal_server_error_response,
    validation_error_response
)
from src.utils.auth import require_auth
from src.utils.validation import validate_notification_settings, ValidationError
from src.utils.logger import get_logger, log_event, log_error

logger = get_logger(__name__)


def get_notification_settings(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    通知設定を取得
    
    GET /notifications/settings
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # 通知設定を取得
        repo = NotificationRepository()
        settings = repo.get_by_user_id(user_id)
        
        return success_response(body=settings)
        
    except Exception as e:
        log_error(logger, e, "Failed to get notification settings")
        return internal_server_error_response()


def update_notification_settings(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    通知設定を更新
    
    PUT /notifications/settings
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # リクエストボディを取得
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return bad_request_response("リクエストボディが不正です")
        
        # バリデーション
        try:
            validate_notification_settings(body)
        except ValidationError as e:
            return validation_error_response(e.details)
        
        # 通知設定を保存
        repo = NotificationRepository()
        settings = repo.save(user_id, body)
        
        return success_response(body={
            'message': '通知設定を更新しました',
            'settings': settings
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to update notification settings")
        return internal_server_error_response()


def connect_line(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    LINE連携
    
    POST /notifications/line/connect
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # リクエストボディを取得
        try:
            body = json.loads(event['body'])
            line_user_id = body['lineUserId']
        except (KeyError, json.JSONDecodeError):
            return bad_request_response("LINE User IDが指定されていません")
        
        # LINE連携を更新
        repo = NotificationRepository()
        settings = repo.update_line_connection(user_id, line_user_id, True)
        
        return success_response(body={
            'message': 'LINE連携が完了しました',
            'lineUserId': line_user_id
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to connect LINE")
        return internal_server_error_response()


def disconnect_line(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    LINE連携解除
    
    POST /notifications/line/disconnect
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # LINE連携を解除
        repo = NotificationRepository()
        settings = repo.update_line_connection(user_id, None, False)
        
        return success_response(body={
            'message': 'LINE連携を解除しました'
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to disconnect LINE")
        return internal_server_error_response()