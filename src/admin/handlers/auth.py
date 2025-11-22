"""
管理者認証ハンドラー
"""
import json
import bcrypt
from typing import Dict, Any

from admin.repositories.admin_repository import AdminRepository
from utils.auth import generate_admin_token
from utils.response import (
    success_response,
    bad_request_response,
    unauthorized_response,
    internal_server_error_response
)
from utils.logger import get_logger

logger = get_logger(__name__)


def admin_login(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    管理者ログイン

    POST /admin/auth/login
    Body: {
        "username": str,
        "password": str
    }
    """
    try:
        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return bad_request_response("ユーザー名とパスワードは必須です")

        # 管理者を取得
        admin_repo = AdminRepository()
        admin = admin_repo.get_by_username(username)

        if not admin:
            return unauthorized_response("ユーザー名またはパスワードが正しくありません")

        # パスワード検証
        password_hash = admin.get('passwordHash', '')
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return unauthorized_response("ユーザー名またはパスワードが正しくありません")

        # JWTトークン生成
        token = generate_admin_token(
            admin_id=admin['adminId'],
            role=admin['role'],
            company_id=admin.get('companyId'),
            store_id=admin.get('storeId')
        )

        # 最終ログイン日時を更新
        admin_repo.update_last_login(admin['adminId'])

        # レスポンス
        return success_response({
            'token': token,
            'admin': {
                'id': admin['adminId'],
                'username': admin['username'],
                'name': admin['name'],
                'email': admin['email'],
                'role': admin['role'],
                'companyId': admin.get('companyId'),
                'companyName': admin.get('companyName'),
                'storeId': admin.get('storeId'),
                'storeName': admin.get('storeName'),
                'lastLoginAt': admin.get('lastLoginAt'),
                'createdAt': admin['createdAt']
            }
        })

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return internal_server_error_response()
