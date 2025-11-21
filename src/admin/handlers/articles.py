"""
コラム管理ハンドラー
"""
import json
from typing import Dict, Any

from src.admin.repositories.article_repository import ArticleRepository
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


def list_articles(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム一覧取得

    GET /admin/articles/list
    """
    try:
        # システム管理者のみ
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

        # データ取得
        article_repo = ArticleRepository()
        articles, total = article_repo.list_articles(filters, page, limit)

        # ページネーション情報を計算
        total_pages = (total + limit - 1) // limit

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


def get_article(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム詳細取得

    GET /admin/articles/list/{articleId}
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # データ取得
        article_repo = ArticleRepository()
        article = article_repo.get_by_id(article_id)

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


def create_article(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム追加

    POST /admin/articles/add
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # 必須フィールドチェック
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if not body.get(field):
                return bad_request_response(f"{field}は必須です")

        # データ作成
        article_repo = ArticleRepository()
        article = article_repo.create(body, admin['admin_id'])

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


def update_article(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム更新

    PUT /admin/articles/update/{articleId}
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        # データ更新
        article_repo = ArticleRepository()
        article = article_repo.update(article_id, body, admin['admin_id'])

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


def delete_article(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム削除

    DELETE /admin/articles/delete/{articleId}
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # パスパラメータを取得
        article_id = int(event['pathParameters']['articleId'])

        # データ削除
        article_repo = ArticleRepository()
        success = article_repo.delete(article_id)

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


def bulk_update_status(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム一括ステータス変更

    PUT /admin/articles/bulk-status
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # リクエストボディを取得
        body = json.loads(event.get('body', '{}'))

        article_ids = body.get('articleIds', [])
        status = body.get('status')

        if not article_ids:
            return bad_request_response("articleIdsは必須です")
        if status not in ['published', 'draft']:
            return bad_request_response("statusは'published'または'draft'である必要があります")

        # データ更新
        article_repo = ArticleRepository()
        updated_count = article_repo.bulk_update_status(article_ids, status, admin['admin_id'])

        return success_response({
            'message': f'{updated_count}件のコラムを更新しました',
            'updatedCount': updated_count
        })

    except json.JSONDecodeError:
        return bad_request_response("不正なJSONフォーマットです")
    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response(str(e))
    except Exception as e:
        logger.error(f"Failed to bulk update articles: {str(e)}")
        return internal_server_error_response()


def bulk_delete_articles(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    コラム一括削除

    DELETE /admin/articles/bulk-delete?articleIds=1,2,3
    """
    try:
        # システム管理者のみ
        admin = require_role(event, ['system_admin'])

        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}
        article_ids_str = params.get('articleIds', '')

        if not article_ids_str:
            return bad_request_response("articleIdsは必須です")

        # カンマ区切りの文字列をリストに変換
        article_ids = [int(id.strip()) for id in article_ids_str.split(',')]

        # データ削除
        article_repo = ArticleRepository()
        deleted_count = article_repo.bulk_delete(article_ids)

        return success_response({
            'message': f'{deleted_count}件のコラムを削除しました',
            'deletedCount': deleted_count
        })

    except ValueError as e:
        if "required" in str(e).lower() or "authentication" in str(e).lower():
            return forbidden_response(str(e))
        return bad_request_response("不正なarticleIdsです")
    except Exception as e:
        logger.error(f"Failed to bulk delete articles: {str(e)}")
        return internal_server_error_response()
