"""
商品関連のLambda関数ハンドラー
"""
import json
from typing import Dict, Any

from src.repositories.product_repository import ProductRepository
from src.repositories.price_history_repository import PriceHistoryRepository
from src.utils.response import (
    success_response,
    bad_request_response,
    not_found_response,
    internal_server_error_response,
    validation_error_response
)
from src.utils.validation import (
    validate_pagination,
    validate_sort_order,
    validate_price_history_days,
    ValidationError
)
from src.utils.logger import get_logger, log_event, log_error
from src.common.constants import HTTPStatus

logger = get_logger(__name__)


def list_products(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    商品一覧を取得
    
    GET /products
    """
    try:
        log_event(logger, event)
        
        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}
        keyword = params.get('keyword')
        category = params.get('category')
        sort = params.get('sort')
        limit = params.get('limit')
        offset = params.get('offset')
        
        # バリデーション
        try:
            limit, offset = validate_pagination(limit, offset)
            sort = validate_sort_order(sort)
        except ValidationError as e:
            return validation_error_response(e.details)
        
        # データ取得
        repo = ProductRepository()
        products, total = repo.get_all(
            keyword=keyword,
            category=category,
            limit=limit,
            offset=offset
        )
        
        # TODO: ソート処理を実装
        
        return success_response(body={
            'products': products,
            'total': total,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to list products")
        return internal_server_error_response()


def get_product(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    商品詳細を取得
    
    GET /products/{productId}
    """
    try:
        log_event(logger, event)
        
        # パスパラメータを取得
        product_id = event['pathParameters']['productId']
        
        # データ取得
        product_repo = ProductRepository()
        product = product_repo.get_by_id(product_id)
        
        if not product:
            return not_found_response("商品が見つかりません")
        
        # 価格履歴を取得（デフォルト30日分）
        history_repo = PriceHistoryRepository()
        price_history = history_repo.get_by_product_id(product_id, days=30)
        
        # AI要約を追加（TODO: 実際のAI実装）
        product['priceHistory'] = price_history
        product['aiSummary'] = {
            'lowestPrice': f"直近30日で最安値は{min([h['price'] for h in price_history] + [product['currentPrice']])}円です",
            'trend': "来週火曜日に値下げの傾向があります（過去の曜日パターンより）",
            'recommendation': "今週末の購入がお得です"
        }
        
        return success_response(body=product)
        
    except KeyError:
        return bad_request_response("商品IDが指定されていません")
    except Exception as e:
        log_error(logger, e, "Failed to get product")
        return internal_server_error_response()


def get_price_history(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    価格履歴を取得
    
    GET /products/{productId}/price-history
    """
    try:
        log_event(logger, event)
        
        # パスパラメータを取得
        product_id = event['pathParameters']['productId']
        
        # クエリパラメータを取得
        params = event.get('queryStringParameters') or {}
        days = params.get('days')
        
        # バリデーション
        try:
            days = validate_price_history_days(days)
        except ValidationError as e:
            return validation_error_response(e.details)
        
        # 商品が存在するかチェック
        product_repo = ProductRepository()
        product = product_repo.get_by_id(product_id)
        
        if not product:
            return not_found_response("商品が見つかりません")
        
        # 価格履歴を取得
        history_repo = PriceHistoryRepository()
        history = history_repo.get_by_product_id(product_id, days=days)
        
        return success_response(body={
            'productId': product_id,
            'history': history
        })
        
    except KeyError:
        return bad_request_response("商品IDが指定されていません")
    except Exception as e:
        log_error(logger, e, "Failed to get price history")
        return internal_server_error_response()