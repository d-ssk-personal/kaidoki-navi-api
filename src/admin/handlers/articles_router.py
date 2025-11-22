"""
コラム管理APIルーター
1つのLambda関数で全てのコラム管理APIを処理することで、コールドスタートを削減
"""
import json
from typing import Dict, Any

from src.admin.services.article_service import ArticleService
from src.utils.auth import require_role
from src.utils.response import (
    success_response,
    bad_request_response,
    not_found_response,
    forbidden_response,
    internal_server_error_response
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def route_articles(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム管理APIのルーティング
    パスとメソッドに基づいて適切なハンドラーに振り分ける

    対応するエンドポイント:
    - GET    /admin/articles/list
    - GET    /admin/articles/list/{articleId}
    - POST   /admin/articles/add
    - PUT    /admin/articles/update/{articleId}
    - DELETE /admin/articles/delete/{articleId}
    - PUT    /admin/articles/bulk-status
    - DELETE /admin/articles/bulk-delete
    """
    try:
        # リクエスト情報を取得
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
        path = event.get('path', event.get('rawPath', ''))
        path_parameters = event.get('pathParameters') or {}

        logger.info(f"Routing request: {http_method} {path}")

        # ルーティング
        if http_method == 'GET' and path.endswith('/list'):
            return list_articles(event)
        elif http_method == 'GET' and 'articleId' in path_parameters:
            return get_article(event)
        elif http_method == 'POST' and path.endswith('/add'):
            return create_article(event)
        elif http_method == 'PUT' and 'articleId' in path_parameters:
            return update_article(event)
        elif http_method == 'DELETE' and 'articleId' in path_parameters:
            return delete_article(event)
        elif http_method == 'PUT' and path.endswith('/bulk-status'):
            return bulk_update_status(event)
        elif http_method == 'DELETE' and path.endswith('/bulk-delete'):
            return bulk_delete_articles(event)
        else:
            return bad_request_response(f"Unsupported route: {http_method} {path}")

    except Exception as e:
        logger.error(f"Routing error: {str(e)}")
        return internal_server_error_response()


def list_articles(event: Dict[str, Any]) -> Dict[str, Any]:
    """コラム一覧取得"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}

        filters = {
            'search': params.get('search'),
            'status': params.get('status'),
            'category': params.get('category'),
            'tags': params.get('tags'),
            'dateFrom': params.get('dateFrom'),
            'dateTo': params.get('dateTo')
        }

        page = int(params.get('page', 1))
        limit = int(params.get('limit', 20))

        # サービス層に委譲
        service = ArticleService()
        articles, total, total_pages = service.list_articles(filters, page, limit)

        return success_response({
            'items': articles,
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
        logger.error(f"Failed to list articles: {str(e)}")
        return internal_server_error_response()


def get_article(event: Dict[str, Any]) -> Dict[str, Any]:
    """コラム詳細取得"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # サービス層に委譲
        service = ArticleService()
        article = service.get_article(article_id)

        if not article:
            return not_found_response("コラムが見つかりません")

        return success_response(article)

    except KeyError:
        return bad_request_response("コラムIDが指定されていません")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response("不正なコラムIDです")
    except Exception as e:
        logger.error(f"Failed to get article: {str(e)}")
        return internal_server_error_response()


def create_article(event: Dict[str, Any]) -> Dict[str, Any]:
    """コラム作成"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # 必須フィールドのバリデーション
        required_fields = ['title', 'content', 'category', 'status']
        for field in required_fields:
            if field not in body:
                return bad_request_response(f"{field}は必須です")

        # サービス層に委譲
        service = ArticleService()
        article = service.create_article(body)

        return success_response(article, status_code=201)

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to create article: {str(e)}")
        return internal_server_error_response()


def update_article(event: Dict[str, Any]) -> Dict[str, Any]:
    """コラム更新"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # サービス層に委譲
        service = ArticleService()
        article = service.update_article(article_id, body)

        if not article:
            return not_found_response("コラムが見つかりません")

        return success_response(article)

    except KeyError:
        return bad_request_response("コラムIDが指定されていません")
    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to update article: {str(e)}")
        return internal_server_error_response()


def delete_article(event: Dict[str, Any]) -> Dict[str, Any]:
    """コラム削除"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # サービス層に委譲
        service = ArticleService()
        success = service.delete_article(article_id)

        if not success:
            return not_found_response("コラムが見つかりません")

        return success_response({'message': 'コラムを削除しました'})

    except KeyError:
        return bad_request_response("コラムIDが指定されていません")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to delete article: {str(e)}")
        return internal_server_error_response()


def bulk_update_status(event: Dict[str, Any]) -> Dict[str, Any]:
    """複数コラムのステータス一括更新"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        article_ids = body.get('articleIds', [])
        status = body.get('status')

        if not article_ids or not status:
            return bad_request_response("articleIdsとstatusは必須です")

        # サービス層に委譲
        service = ArticleService()
        success_count, failed_count = service.bulk_update_status(article_ids, status)

        return success_response({
            'message': f'{success_count}件のコラムを更新しました',
            'successCount': success_count,
            'failedCount': failed_count
        })

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to bulk update status: {str(e)}")
        return internal_server_error_response()


def bulk_delete_articles(event: Dict[str, Any]) -> Dict[str, Any]:
    """複数コラムの一括削除"""
    try:
        # 認証チェック
        admin = require_role(event, ['system_admin'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        article_ids = body.get('articleIds', [])

        if not article_ids:
            return bad_request_response("articleIdsは必須です")

        # サービス層に委譲
        service = ArticleService()
        success_count, failed_count = service.bulk_delete_articles(article_ids)

        return success_response({
            'message': f'{success_count}件のコラムを削除しました',
            'successCount': success_count,
            'failedCount': failed_count
        })

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to bulk delete articles: {str(e)}")
        return internal_server_error_response()
