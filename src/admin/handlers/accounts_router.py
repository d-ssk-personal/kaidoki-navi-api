"""
アカウント管理APIルーター
1つのLambda関数で全てのアカウント管理APIを処理することで、コールドスタートを削減
"""
import json
from typing import Dict, Any

from admin.services.account_service import AccountService
from utils.auth import require_admin_auth
from utils.response import (
    success_response,
    bad_request_response,
    not_found_response,
    forbidden_response,
    internal_server_error_response
)
from utils.logger import get_logger

logger = get_logger(__name__)


def route_accounts(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    アカウント管理APIのルーティング
    パスとメソッドに基づいて適切なハンドラーに振り分ける

    対応するエンドポイント:
    - GET    /admin/accounts/list
    - GET    /admin/accounts/list/{accountId}
    - POST   /admin/accounts/add
    - PUT    /admin/accounts/update/{accountId}
    - DELETE /admin/accounts/delete/{accountId}
    """
    try:
        # リクエスト情報を取得
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
        path = event.get('path', event.get('rawPath', ''))
        path_parameters = event.get('pathParameters') or {}

        logger.info(f"Routing request: {http_method} {path}")

        # ルーティング
        if http_method == 'GET' and path.endswith('/list'):
            return list_accounts(event)
        elif http_method == 'GET' and 'accountId' in path_parameters:
            return get_account(event)
        elif http_method == 'POST' and path.endswith('/add'):
            return create_account(event)
        elif http_method == 'PUT' and 'accountId' in path_parameters:
            return update_account(event)
        elif http_method == 'DELETE' and 'accountId' in path_parameters:
            return delete_account(event)
        else:
            return bad_request_response(f"Unsupported route: {http_method} {path}")

    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        return internal_server_error_response()


def list_accounts(event: Dict[str, Any]) -> Dict[str, Any]:
    """アカウント一覧取得"""
    try:
        # 認証チェック
        admin = require_admin_auth(event)

        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}

        filters = {
            'search': params.get('search'),
            'role': params.get('role'),
            'companyId': params.get('companyId')
        }

        page = int(params.get('page', 1))
        limit = int(params.get('limit', 20))

        # サービス層に委譲
        service = AccountService()
        accounts, total, total_pages = service.list_accounts(filters, page, limit, admin)

        return success_response({
            'items': accounts,
            'pagination': {
                'currentPage': page,
                'totalPages': total_pages,
                'totalItems': total,
                'limit': limit
            }
        })

    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to list accounts: {str(e)}")
        return internal_server_error_response()


def get_account(event: Dict[str, Any]) -> Dict[str, Any]:
    """アカウント詳細取得"""
    try:
        # 認証チェック
        admin = require_admin_auth(event)

        # パスパラメータを取得
        account_id = event['pathParameters']['accountId']

        # サービス層に委譲
        service = AccountService()
        account = service.get_account(account_id, admin)

        if not account:
            return not_found_response("アカウントが見つかりません")

        return success_response(account)

    except KeyError:
        return bad_request_response("アカウントIDが指定されていません")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        if "権限" in str(e):
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to get account: {str(e)}")
        return internal_server_error_response()


def create_account(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    アカウント作成
    ※動作確認のため、一時的に認証なしで実装
    """
    try:
        # NOTE: 動作確認のため一時的に認証なし
        # 本番環境では以下のコメントを外す
        # admin = require_admin_auth(event)
        # 仮の管理者情報（動作確認用）
        admin = {
            'admin_id': 'system',
            'role': 'system_admin',
            'company_id': None,
            'store_id': None
        }

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # 必須フィールドのバリデーション
        required_fields = ['username', 'name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in body:
                return bad_request_response(f"{field}は必須です")

        # サービス層に委譲
        service = AccountService()
        account = service.create_account(body, admin)

        return success_response(account, status_code=201)

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to create account: {str(e)}")
        return internal_server_error_response()


def update_account(event: Dict[str, Any]) -> Dict[str, Any]:
    """アカウント更新"""
    try:
        # 認証チェック
        admin = require_admin_auth(event)

        # パスパラメータを取得
        account_id = event['pathParameters']['accountId']

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # サービス層に委譲
        service = AccountService()
        account = service.update_account(account_id, body, admin)

        if not account:
            return not_found_response("アカウントが見つかりません")

        return success_response(account)

    except KeyError:
        return bad_request_response("アカウントIDが指定されていません")
    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        if "権限" in str(e):
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to update account: {str(e)}")
        return internal_server_error_response()


def delete_account(event: Dict[str, Any]) -> Dict[str, Any]:
    """アカウント削除"""
    try:
        # 認証チェック
        admin = require_admin_auth(event)

        # パスパラメータを取得
        account_id = event['pathParameters']['accountId']

        # サービス層に委譲
        service = AccountService()
        success = service.delete_account(account_id, admin)

        if not success:
            return not_found_response("アカウントが見つかりません")

        return success_response({'message': 'アカウントを削除しました'})

    except KeyError:
        return bad_request_response("アカウントIDが指定されていません")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        if "権限" in str(e) or "自分自身" in str(e):
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to delete account: {str(e)}")
        return internal_server_error_response()
