"""
管理者リポジトリ
"""
import boto3
import bcrypt
import uuid
from boto3.dynamodb.conditions import Key
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from config.settings import settings
from utils.logger import get_logger

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

    def list_accounts(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        アカウント一覧を取得（フィルター対応）

        Args:
            filters: フィルター条件
                - search: キーワード検索（名前・ユーザー名）
                - role: 役割
                - companyId: 企業ID
            page: ページ番号
            limit: 1ページあたりの件数

        Returns:
            (アカウントリスト, 総件数)
        """
        try:
            items = []

            # 企業IDでフィルター（GSI-2を使用）
            if filters.get('companyId'):
                response = self.table.query(
                    IndexName='CompanyIndex',
                    KeyConditionExpression=Key('companyId').eq(filters['companyId'])
                )
                items = response.get('Items', [])
            else:
                # フィルターなしの場合はスキャン
                response = self.table.scan()
                items = response.get('Items', [])

                # ページネーション対応
                while 'LastEvaluatedKey' in response:
                    response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    items.extend(response.get('Items', []))

            # 追加フィルター
            filtered_items = items

            # キーワード検索
            if filters.get('search'):
                search = filters['search'].lower()
                filtered_items = [
                    item for item in filtered_items
                    if search in item.get('name', '').lower() or
                       search in item.get('username', '').lower()
                ]

            # 役割フィルター
            if filters.get('role'):
                filtered_items = [
                    item for item in filtered_items
                    if item.get('role') == filters['role']
                ]

            # ソート（createdAtで新しい順）
            filtered_items.sort(
                key=lambda x: x.get('createdAt', ''),
                reverse=True
            )

            # ページネーション
            total = len(filtered_items)
            start = (page - 1) * limit
            end = start + limit
            paginated_items = filtered_items[start:end]

            return paginated_items, total

        except Exception as e:
            logger.error(f"Failed to list accounts: {str(e)}")
            return [], 0

    def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        新しいアカウントを作成

        Args:
            account_data: アカウントデータ

        Returns:
            作成されたアカウント情報
        """
        try:
            # 新しいIDを生成
            admin_id = f"admin_{str(uuid.uuid4())[:8]}"

            # パスワードをハッシュ化
            password_hash = bcrypt.hashpw(
                account_data['password'].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            now = datetime.utcnow().isoformat() + 'Z'

            item = {
                'adminId': admin_id,
                'username': account_data['username'],
                'name': account_data['name'],
                'email': account_data['email'],
                'passwordHash': password_hash,
                'role': account_data['role'],
                'createdAt': now,
                'updatedAt': now
            }

            # 役割に応じて追加情報を設定
            if account_data['role'] in ['company_admin', 'store_user']:
                item['companyId'] = account_data.get('companyId')
                item['companyName'] = account_data.get('companyName')

            if account_data['role'] == 'store_user':
                item['storeId'] = account_data.get('storeId')
                item['storeName'] = account_data.get('storeName')

            self.table.put_item(Item=item)

            # パスワードハッシュを削除してから返す
            del item['passwordHash']

            logger.info(f"Account created successfully: {admin_id}")
            return item

        except Exception as e:
            logger.error(f"Failed to create account: {str(e)}")
            raise

    def update_account(
        self,
        admin_id: str,
        account_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        既存のアカウントを更新

        Args:
            admin_id: 管理者ID
            account_data: 更新するアカウントデータ

        Returns:
            更新されたアカウント情報。見つからない場合はNone
        """
        try:
            # 既存のアイテムを確認
            existing = self.get_by_id(admin_id)
            if not existing:
                return None

            now = datetime.utcnow().isoformat() + 'Z'

            # 更新する属性を構築
            update_expression = "SET "
            expression_values = {}
            expression_names = {}

            fields = ['username', 'name', 'email', 'role', 'companyId', 'companyName', 'storeId', 'storeName']

            for field in fields:
                if field in account_data:
                    update_expression += f"#{field} = :{field}, "
                    expression_values[f":{field}"] = account_data[field]
                    expression_names[f"#{field}"] = field

            # パスワードが指定されている場合はハッシュ化
            if 'password' in account_data and account_data['password']:
                password_hash = bcrypt.hashpw(
                    account_data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                update_expression += "#passwordHash = :passwordHash, "
                expression_values[":passwordHash"] = password_hash
                expression_names["#passwordHash"] = "passwordHash"

            update_expression += "#updatedAt = :updatedAt"
            expression_values[":updatedAt"] = now
            expression_names["#updatedAt"] = "updatedAt"

            response = self.table.update_item(
                Key={'adminId': admin_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ReturnValues='ALL_NEW'
            )

            updated_item = response.get('Attributes')

            # パスワードハッシュを削除してから返す
            if updated_item and 'passwordHash' in updated_item:
                del updated_item['passwordHash']

            logger.info(f"Account updated successfully: {admin_id}")
            return updated_item

        except Exception as e:
            logger.error(f"Failed to update account {admin_id}: {str(e)}")
            raise

    def delete_account(self, admin_id: str) -> bool:
        """
        アカウントを削除

        Args:
            admin_id: 管理者ID

        Returns:
            削除に成功した場合True
        """
        try:
            self.table.delete_item(Key={'adminId': admin_id})
            logger.info(f"Account deleted successfully: {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete account {admin_id}: {str(e)}")
            return False
