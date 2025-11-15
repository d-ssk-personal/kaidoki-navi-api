"""
お気に入り関連のLambda関数ハンドラー
"""
import json
from typing import Dict, Any

from src.repositories.favorite_repository import FavoriteRepository
from src.repositories.product_repository import ProductRepository
from src.utils.response import (
    success_response,
    bad_request_response,
    unauthorized_response,
    not_found_response,
    conflict_response,
    internal_server_error_response
)
from src.utils.auth import require_auth
from src.utils.logger import get_logger, log_event, log_error
from src.common.constants import HTTPStatus

logger = get_logger(__name__)


def list_favorites(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    お気に入り一覧を取得
    
    GET /favorites
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # お気に入り商品IDを取得
        favorite_repo = FavoriteRepository()
        product_ids = favorite_repo.get_by_user_id(user_id)
        
        # 商品詳細を取得
        product_repo = ProductRepository()
        products = []
        for product_id in product_ids:
            product = product_repo.get_by_id(product_id)
            if product:
                products.append(product)
        
        return success_response(body={
            'favorites': products
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to list favorites")
        return internal_server_error_response()


def add_favorite(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    お気に入りに追加
    
    POST /favorites
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
            product_id = body['productId']
        except (KeyError, json.JSONDecodeError):
            return bad_request_response("商品IDが指定されていません")
        
        # 商品が存在するかチェック
        product_repo = ProductRepository()
        product = product_repo.get_by_id(product_id)
        
        if not product:
            return not_found_response("商品が見つかりません")
        
        # お気に入りに追加
        favorite_repo = FavoriteRepository()
        try:
            favorite_repo.add(user_id, product_id)
        except ValueError:
            return conflict_response("既にお気に入りに追加済みです")
        
        return success_response(
            status_code=HTTPStatus.CREATED,
            body={
                'message': 'お気に入りに追加しました',
                'productId': product_id
            }
        )
        
    except Exception as e:
        log_error(logger, e, "Failed to add favorite")
        return internal_server_error_response()


def remove_favorite(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    お気に入りから削除
    
    DELETE /favorites/{productId}
    """
    try:
        log_event(logger, event)
        
        # 認証チェック
        try:
            user_id = require_auth(event)
        except ValueError:
            return unauthorized_response()
        
        # パスパラメータを取得
        try:
            product_id = event['pathParameters']['productId']
        except KeyError:
            return bad_request_response("商品IDが指定されていません")
        
        # お気に入りから削除
        favorite_repo = FavoriteRepository()
        favorite_repo.remove(user_id, product_id)
        
        return success_response(body={
            'message': 'お気に入りから削除しました'
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to remove favorite")
        return internal_server_error_response()