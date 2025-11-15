"""
お気に入りリポジトリ
"""
import boto3
from typing import List, Dict, Any
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from src.config.settings import settings
from src.repositories.product_repository import ProductRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FavoriteRepository:
    """お気に入りリポジトリクラス"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.FAVORITES_TABLE_NAME)
    
    def get_by_user_id(self, user_id: str) -> List[str]:
        """
        ユーザーのお気に入り商品IDリストを取得
        
        Args:
            user_id: ユーザーID
        
        Returns:
            商品IDのリスト
        """
        try:
            response = self.table.query(
                KeyConditionExpression=Key('userId').eq(user_id)
            )
            
            items = response.get('Items', [])
            
            return [item['productId'] for item in items]
            
        except Exception as e:
            logger.error(f"Failed to get favorites for user {user_id}: {str(e)}")
            raise
    
    def add(self, user_id: str, product_id: str) -> Dict[str, Any]:
        """
        お気に入りに追加
        
        Args:
            user_id: ユーザーID
            product_id: 商品ID
        
        Returns:
            追加されたお気に入りデータ
        
        Raises:
            ValueError: 既にお気に入りに追加済みの場合
        """
        try:
            from datetime import datetime
            
            item = {
                'userId': user_id,
                'productId': product_id,
                'createdAt': datetime.now().isoformat()
            }
            
            # 既に存在する場合はエラー
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(userId) AND attribute_not_exists(productId)'
            )
            
            return item
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError("Already added to favorites")
            logger.error(f"Failed to add favorite: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to add favorite: {str(e)}")
            raise
    
    def remove(self, user_id: str, product_id: str) -> bool:
        """
        お気に入りから削除
        
        Args:
            user_id: ユーザーID
            product_id: 商品ID
        
        Returns:
            削除成功した場合True
        """
        try:
            self.table.delete_item(
                Key={
                    'userId': user_id,
                    'productId': product_id
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove favorite: {str(e)}")
            raise
    
    def exists(self, user_id: str, product_id: str) -> bool:
        """
        お気に入りに存在するかチェック
        
        Args:
            user_id: ユーザーID
            product_id: 商品ID
        
        Returns:
            存在する場合True
        """
        try:
            response = self.table.get_item(
                Key={
                    'userId': user_id,
                    'productId': product_id
                }
            )
            
            return 'Item' in response
            
        except Exception as e:
            logger.error(f"Failed to check favorite existence: {str(e)}")
            raise