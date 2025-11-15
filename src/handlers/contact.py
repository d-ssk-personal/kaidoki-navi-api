"""
お問い合わせ関連のLambda関数ハンドラー
"""
import json
import uuid
from typing import Dict, Any

from src.utils.response import (
    success_response,
    bad_request_response,
    internal_server_error_response,
    validation_error_response
)
from src.utils.validation import validate_contact_form, ValidationError
from src.utils.logger import get_logger, log_event, log_error

logger = get_logger(__name__)


def submit_contact(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    お問い合わせを送信
    
    POST /contact
    """
    try:
        log_event(logger, event)
        
        # リクエストボディを取得
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return bad_request_response("リクエストボディが不正です")
        
        # バリデーション
        try:
            validate_contact_form(body)
        except ValidationError as e:
            return validation_error_response(e.details)
        
        # お問い合わせIDを生成
        contact_id = str(uuid.uuid4())
        
        # TODO: 以下の処理を実装
        # 1. DynamoDBに保存
        # 2. 管理者にメール通知（SES）
        # 3. ユーザーに自動返信メール
        
        logger.info(f"Contact received: {contact_id}")
        logger.info(f"Name: {body['name']}, Email: {body['email']}, Category: {body['category']}")
        
        return success_response(body={
            'message': 'お問い合わせを受け付けました',
            'contactId': contact_id
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to submit contact")
        return internal_server_error_response()