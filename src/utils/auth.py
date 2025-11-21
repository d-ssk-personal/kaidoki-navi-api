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


# 管理者認証機能

def generate_admin_token(admin_id: str, role: str, company_id: Optional[str] = None,
                        store_id: Optional[str] = None) -> str:
    """
    管理者用JWTトークンを生成

    Args:
        admin_id: 管理者ID
        role: 役割（system_admin, company_admin, store_user）
        company_id: 企業ID（company_admin, store_userの場合）
        store_id: 店舗ID（store_userの場合）

    Returns:
        JWTトークン文字列
    """
    payload = {
        'admin_id': admin_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
        'type': 'admin'
    }

    if company_id:
        payload['company_id'] = company_id
    if store_id:
        payload['store_id'] = store_id

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def get_admin_from_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Lambdaイベントから管理者情報を取得

    Args:
        event: Lambdaイベント

    Returns:
        管理者情報の辞書。認証されていない場合はNone
        {
            'admin_id': str,
            'role': str,
            'company_id': Optional[str],
            'store_id': Optional[str]
        }
    """
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization') or headers.get('authorization')

    if not auth_header:
        return None

    token = extract_token_from_header(auth_header)
    if not token:
        return None

    payload = verify_token(token)
    if not payload or payload.get('type') != 'admin':
        return None

    return {
        'admin_id': payload.get('admin_id'),
        'role': payload.get('role'),
        'company_id': payload.get('company_id'),
        'store_id': payload.get('store_id')
    }


def require_admin_auth(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    管理者認証を必須とし、管理者情報を取得

    Args:
        event: Lambdaイベント

    Returns:
        管理者情報の辞書

    Raises:
        ValueError: 認証されていない場合
    """
    admin = get_admin_from_event(event)

    if not admin:
        raise ValueError("Admin authentication required")

    return admin


def require_role(event: Dict[str, Any], allowed_roles: list) -> Dict[str, Any]:
    """
    特定の役割を必須とする

    Args:
        event: Lambdaイベント
        allowed_roles: 許可される役割のリスト

    Returns:
        管理者情報の辞書

    Raises:
        ValueError: 認証されていない場合、または権限がない場合
    """
    admin = require_admin_auth(event)

    if admin['role'] not in allowed_roles:
        raise ValueError(f"Required role: {', '.join(allowed_roles)}")

    return admin


def check_permission(admin: Dict[str, Any], resource_company_id: Optional[str] = None,
                    resource_store_id: Optional[str] = None) -> bool:
    """
    管理者が特定のリソースにアクセス権限があるかチェック

    Args:
        admin: 管理者情報
        resource_company_id: リソースの企業ID
        resource_store_id: リソースの店舗ID

    Returns:
        権限がある場合True
    """
    role = admin.get('role')

    # システム管理者は全てのリソースにアクセス可能
    if role == 'system_admin':
        return True

    # 企業管理者は自社のリソースにのみアクセス可能
    if role == 'company_admin':
        if resource_company_id and admin.get('company_id') == resource_company_id:
            return True
        return False

    # 店舗ユーザーは自店舗のリソースにのみアクセス可能
    if role == 'store_user':
        if resource_store_id and admin.get('store_id') == resource_store_id:
            return True
        return False

    return False