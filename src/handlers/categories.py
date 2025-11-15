"""
カテゴリ関連のLambda関数ハンドラー
"""
from typing import Dict, Any

from src.common.constants import CATEGORIES
from src.utils.response import success_response, internal_server_error_response
from src.utils.logger import get_logger, log_event, log_error

logger = get_logger(__name__)


def list_categories(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    カテゴリ一覧を取得
    
    GET /categories
    """
    try:
        log_event(logger, event)
        
        # TODO: DynamoDBから取得する実装に変更
        # 現在は定数から返す
        categories = [
            {
                'id': cat['id'],
                'name': cat['name'],
                'displayOrder': cat['displayOrder'],
                'productCount': 0  # TODO: 実際の商品数を取得
            }
            for cat in CATEGORIES
        ]
        
        return success_response(body={
            'categories': categories
        })
        
    except Exception as e:
        log_error(logger, e, "Failed to list categories")
        return internal_server_error_response()