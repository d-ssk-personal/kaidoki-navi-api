"""
通知設定リポジトリ
"""
import boto3
from typing import Dict, Any, Optional

from src.config.settings import settings
from src.repositories.product_repository import ProductRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationRepository:
    """通知設定リポジトリクラス"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.NOTIFICATION_SETTINGS_TABLE_NAME)
    
    def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        ユーザーの通知設定を取得
        
        Args:
            user_id: ユーザーID
        
        Returns:
            通知設定データ。存在しない場合はデフォルト設定
        """
        try:
            response = self.table.get_item(Key={'userId': user_id})
            item = response.get('Item')
            
            if item:
                return ProductRepository._convert_decimals(item)
            
            # デフォルト設定を返す
            from src.common.constants import NotificationFrequency
            return {
                'userId': user_id,
                'categories': [],
                'frequency': NotificationFrequency.REALTIME.value,
                'priceChangeThreshold': settings.DEFAULT_PRICE_CHANGE_THRESHOLD,
                'lineConnected': False,
                'webPushEnabled': False
            }
            
        except Exception as e:
            logger.error(f"Failed to get notification settings for {user_id}: {str(e)}")
            raise
    
    def save(self, user_id: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        通知設定を保存
        
        Args:
            user_id: ユーザーID
            settings_data: 通知設定データ
        
        Returns:
            保存された通知設定データ
        """
        try:
            from datetime import datetime
            
            item = {
                'userId': user_id,
                **settings_data,
                'updatedAt': datetime.now().isoformat()
            }
            
            # Decimal型に変換
            item = ProductRepository._convert_to_decimals(item)
            
            self.table.put_item(Item=item)
            
            return ProductRepository._convert_decimals(item)
            
        except Exception as e:
            logger.error(f"Failed to save notification settings: {str(e)}")
            raise
    
    def update_line_connection(self, user_id: str, line_user_id: Optional[str], connected: bool) -> Dict[str, Any]:
        """
        LINE連携状態を更新
        
        Args:
            user_id: ユーザーID
            line_user_id: LINE User ID
            connected: 連携状態
        
        Returns:
            更新された通知設定データ
        """
        try:
            from datetime import datetime
            
            update_expression = "SET lineConnected = :connected, updatedAt = :updated"
            expression_attribute_values = {
                ':connected': connected,
                ':updated': datetime.now().isoformat()
            }
            
            if line_user_id:
                update_expression += ", lineUserId = :lineUserId"
                expression_attribute_values[':lineUserId'] = line_user_id
            
            response = self.table.update_item(
                Key={'userId': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            item = response.get('Attributes')
            if item:
                return ProductRepository._convert_decimals(item)
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to update LINE connection: {str(e)}")
            raise