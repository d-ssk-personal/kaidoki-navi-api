"""
認証ユーティリティ
JWT認証を実装
"""
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_token(user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """
    JWTトークンを生成
    
    Args:
        user_id: ユーザーID
        additional_claims: 追加のクレーム
    
    Returns:
        JWTトークン文字列
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWTトークンを検証
    
    Args:
        token: JWTトークン文字列
    
    Returns:
        トークンのペイロード。検証失敗時はNone
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None


def extract_token_from_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    AuthorizationヘッダーからBearerトークンを抽出
    
    Args:
        authorization_header: Authorizationヘッダーの値
    
    Returns:
        トークン文字列。存在しない場合はNone
    """
    if not authorization_header:
        return None
    
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def get_user_id_from_event(event: Dict[str, Any]) -> Optional[str]:
    """
    LambdaイベントからユーザーIDを取得
    
    Args:
        event: Lambdaイベント
    
    Returns:
        ユーザーID。認証されていない場合はNone
    """
    headers = event.get('headers', {})
    
    # ヘッダー名は大文字小文字を区別しないため、小文字で統一
    auth_header = headers.get('Authorization') or headers.get('authorization')
    
    if not auth_header:
        return None
    
    token = extract_token_from_header(auth_header)
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    return payload.get('user_id')


def require_auth(event: Dict[str, Any]) -> str:
    """
    認証を必須とし、ユーザーIDを取得
    認証されていない場合は例外を発生
    
    Args:
        event: Lambdaイベント
    
    Returns:
        ユーザーID
    
    Raises:
        ValueError: 認証されていない場合
    """
    user_id = get_user_id_from_event(event)
    
    if not user_id:
        raise ValueError("Authentication required")
    
    return user_id