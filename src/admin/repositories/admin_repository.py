"""
管理者リポジトリ
"""
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any
from datetime import datetime

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# DynamoDB接続設定（ローカル開発環境対応）
dynamodb_config = {'region_name': settings.AWS_REGION}
if settings.DYNAMODB_ENDPOINT_URL:
    dynamodb_config['endpoint_url'] = settings.DYNAMODB_ENDPOINT_URL
    logger.info(f"Using DynamoDB endpoint: {settings.DYNAMODB_ENDPOINT_URL}")

dynamodb = boto3.resource('dynamodb', **dynamodb_config)


class AdminRepository:
    """管理者のDynamoDBリポジトリ"""

    def __init__(self):
        self.table = dynamodb.Table(settings.ADMINS_TABLE_NAME)

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        ユーザー名で管理者を取得

        Args:
            username: ユーザー名（ログインID）

        Returns:
            管理者情報の辞書。見つからない場合はNone
        """
        try:
            response = self.table.query(
                IndexName='UsernameIndex',
                KeyConditionExpression=Key('username').eq(username)
            )

            items = response.get('Items', [])
            return items[0] if items else None

        except Exception as e:
            logger.error(f"Failed to get admin by username {username}: {str(e)}")
            return None

    def get_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """
        IDで管理者を取得

        Args:
            admin_id: 管理者ID

        Returns:
            管理者情報の辞書。見つからない場合はNone
        """
        try:
            response = self.table.get_item(Key={'adminId': admin_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get admin {admin_id}: {str(e)}")
            return None

    def update_last_login(self, admin_id: str) -> bool:
        """
        最終ログイン日時を更新

        Args:
            admin_id: 管理者ID

        Returns:
            更新に成功した場合True
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'

            self.table.update_item(
                Key={'adminId': admin_id},
                UpdateExpression="SET lastLoginAt = :lastLoginAt",
                ExpressionAttributeValues={':lastLoginAt': now}
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update last login for admin {admin_id}: {str(e)}")
            return False
