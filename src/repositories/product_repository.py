"""
商品リポジトリ
DynamoDBへのアクセスを担当
"""
import boto3
from typing import List, Optional, Dict, Any
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProductRepository:
    """商品リポジトリクラス"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.PRODUCTS_TABLE_NAME)
    
    def get_all(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        商品一覧を取得
        
        Args:
            keyword: 検索キーワード
            category: カテゴリフィルター
            limit: 取得件数
            offset: 取得開始位置
        
        Returns:
            (商品リスト, 総件数)
        """
        try:
            # カテゴリフィルターがある場合はGSIを使用
            if category:
                response = self.table.query(
                    IndexName='category-updatedAt-index',
                    KeyConditionExpression=Key('category').eq(category),
                    ScanIndexForward=False  # 更新日時の降順
                )
            else:
                response = self.table.scan()
            
            items = response.get('Items', [])
            
            # キーワード検索
            if keyword:
                keyword_lower = keyword.lower()
                items = [
                    item for item in items
                    if keyword_lower in item.get('name', '').lower()
                ]
            
            # 総件数
            total = len(items)
            
            # ページネーション
            items = items[offset:offset + limit]
            
            # Decimal型を変換
            items = [self._convert_decimals(item) for item in items]
            
            return items, total
            
        except Exception as e:
            logger.error(f"Failed to get products: {str(e)}")
            raise
    
    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        商品IDで商品を取得
        
        Args:
            product_id: 商品ID
        
        Returns:
            商品データ。存在しない場合はNone
        """
        try:
            response = self.table.get_item(Key={'productId': product_id})
            item = response.get('Item')
            
            if item:
                return self._convert_decimals(item)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {str(e)}")
            raise
    
    def create(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        商品を作成
        
        Args:
            product: 商品データ
        
        Returns:
            作成された商品データ
        """
        try:
            # Decimal型に変換
            product = self._convert_to_decimals(product)
            
            self.table.put_item(Item=product)
            
            return self._convert_decimals(product)
            
        except Exception as e:
            logger.error(f"Failed to create product: {str(e)}")
            raise
    
    def update(self, product_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        商品を更新
        
        Args:
            product_id: 商品ID
            updates: 更新データ
        
        Returns:
            更新された商品データ。存在しない場合はNone
        """
        try:
            # 更新式を構築
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for i, (key, value) in enumerate(updates.items()):
                attr_name = f"#{key}"
                attr_value = f":val{i}"
                
                if i > 0:
                    update_expression += ", "
                
                update_expression += f"{attr_name} = {attr_value}"
                expression_attribute_names[attr_name] = key
                
                # Decimal型に変換
                if isinstance(value, (int, float)):
                    value = Decimal(str(value))
                
                expression_attribute_values[attr_value] = value
            
            response = self.table.update_item(
                Key={'productId': product_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            item = response.get('Attributes')
            if item:
                return self._convert_decimals(item)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {str(e)}")
            raise
    
    def delete(self, product_id: str) -> bool:
        """
        商品を削除
        
        Args:
            product_id: 商品ID
        
        Returns:
            削除成功した場合True
        """
        try:
            self.table.delete_item(Key={'productId': product_id})
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {str(e)}")
            raise
    
    @staticmethod
    def _convert_decimals(obj: Any) -> Any:
        """
        Decimal型をfloat/intに変換
        
        Args:
            obj: 変換対象のオブジェクト
        
        Returns:
            変換後のオブジェクト
        """
        if isinstance(obj, list):
            return [ProductRepository._convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: ProductRepository._convert_decimals(value) for key, value in obj.items()}
        elif isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj
    
    @staticmethod
    def _convert_to_decimals(obj: Any) -> Any:
        """
        float/intをDecimal型に変換
        
        Args:
            obj: 変換対象のオブジェクト
        
        Returns:
            変換後のオブジェクト
        """
        if isinstance(obj, list):
            return [ProductRepository._convert_to_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: ProductRepository._convert_to_decimals(value) for key, value in obj.items()}
        elif isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, int) and not isinstance(obj, bool):
            return Decimal(obj)
        else:
            return obj