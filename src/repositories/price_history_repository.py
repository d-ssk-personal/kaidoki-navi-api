"""
価格履歴リポジトリ
"""
import boto3
from typing import List, Dict, Any
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

from src.config.settings import settings
from src.repositories.product_repository import ProductRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PriceHistoryRepository:
    """価格履歴リポジトリクラス"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.PRICE_HISTORY_TABLE_NAME)
    
    def get_by_product_id(self, product_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        商品の価格履歴を取得
        
        Args:
            product_id: 商品ID
            days: 取得日数
        
        Returns:
            価格履歴のリスト
        """
        try:
            # 取得開始日を計算
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            response = self.table.query(
                KeyConditionExpression=Key('productId').eq(product_id) & Key('date').gte(start_date),
                ScanIndexForward=True  # 日付の昇順
            )
            
            items = response.get('Items', [])
            
            # Decimal型を変換
            items = [ProductRepository._convert_decimals(item) for item in items]
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to get price history for {product_id}: {str(e)}")
            raise
    
    def add(self, history: Dict[str, Any]) -> Dict[str, Any]:
        """
        価格履歴を追加
        
        Args:
            history: 価格履歴データ
        
        Returns:
            追加された価格履歴データ
        """
        try:
            # Decimal型に変換
            history = ProductRepository._convert_to_decimals(history)
            
            self.table.put_item(Item=history)
            
            return ProductRepository._convert_decimals(history)
            
        except Exception as e:
            logger.error(f"Failed to add price history: {str(e)}")
            raise
    
    def get_latest_by_product_id(self, product_id: str) -> Dict[str, Any]:
        """
        商品の最新の価格履歴を取得
        
        Args:
            product_id: 商品ID
        
        Returns:
            最新の価格履歴
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key('productId').eq(product_id),
                ScanIndexForward=False,  # 日付の降順
                Limit=1
            )
            
            items = response.get('Items', [])
            
            if items:
                return ProductRepository._convert_decimals(items[0])
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get latest price history for {product_id}: {str(e)}")
            raise