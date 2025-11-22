"""
コラム記事リポジトリ
"""
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# DynamoDB接続設定（ローカル開発環境対応）
dynamodb_config = {'region_name': settings.AWS_REGION}
if settings.DYNAMODB_ENDPOINT_URL:
    dynamodb_config['endpoint_url'] = settings.DYNAMODB_ENDPOINT_URL
    logger.info(f"Using DynamoDB endpoint: {settings.DYNAMODB_ENDPOINT_URL}")

dynamodb = boto3.resource('dynamodb', **dynamodb_config)


class ArticleRepository:
    """コラム記事のDynamoDBリポジトリ"""

    def __init__(self):
        self.table = dynamodb.Table(settings.ARTICLES_TABLE_NAME)

    def get_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        IDでコラムを取得

        Args:
            article_id: コラムID

        Returns:
            コラム情報の辞書。見つからない場合はNone
        """
        try:
            response = self.table.get_item(Key={'articleId': article_id})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get article {article_id}: {str(e)}")
            return None

    def list_articles(self, filters: Dict[str, Any], page: int = 1,
                     limit: int = 20) -> Tuple[List[Dict[str, Any]], int]:
        """
        コラム一覧を取得（フィルター対応）

        Args:
            filters: フィルター条件
                - search: キーワード検索（タイトル・本文）
                - status: ステータス（published/draft）
                - category: カテゴリ
                - tags: タグ（カンマ区切り）
                - dateFrom: 公開日の開始日
                - dateTo: 公開日の終了日
            page: ページ番号
            limit: 1ページあたりの件数

        Returns:
            (コラムリスト, 総件数)
        """
        try:
            items = []

            # ステータスでフィルター（GSI-1を使用）
            if filters.get('status'):
                response = self.table.query(
                    IndexName='StatusIndex',
                    KeyConditionExpression=Key('status').eq(filters['status']),
                    ScanIndexForward=False  # 新しい順
                )
                items = response.get('Items', [])
            # カテゴリでフィルター（GSI-2を使用）
            elif filters.get('category'):
                response = self.table.query(
                    IndexName='CategoryIndex',
                    KeyConditionExpression=Key('category').eq(filters['category']),
                    ScanIndexForward=False  # 新しい順
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
                    if search in item.get('title', '').lower() or
                       search in item.get('content', '').lower()
                ]

            # タグフィルター
            if filters.get('tags'):
                tags = [t.strip() for t in filters['tags'].split(',')]
                filtered_items = [
                    item for item in filtered_items
                    if any(tag in item.get('tags', []) for tag in tags)
                ]

            # 日付範囲フィルター
            if filters.get('dateFrom'):
                filtered_items = [
                    item for item in filtered_items
                    if item.get('publishedAt', '') >= filters['dateFrom']
                ]

            if filters.get('dateTo'):
                filtered_items = [
                    item for item in filtered_items
                    if item.get('publishedAt', '') <= filters['dateTo']
                ]

            # ソート（publishedAtで新しい順）
            filtered_items.sort(
                key=lambda x: x.get('publishedAt', ''),
                reverse=True
            )

            # ページネーション
            total = len(filtered_items)
            start = (page - 1) * limit
            end = start + limit
            paginated_items = filtered_items[start:end]

            return paginated_items, total

        except Exception as e:
            logger.error(f"Failed to list articles: {str(e)}")
            return [], 0

    def create(self, article_data: Dict[str, Any], admin_id: str) -> Dict[str, Any]:
        """
        新しいコラムを作成

        Args:
            article_data: コラムデータ
            admin_id: 作成者の管理者ID

        Returns:
            作成されたコラム情報
        """
        try:
            # 新しいIDを生成（既存の最大ID + 1）
            response = self.table.scan(
                ProjectionExpression='articleId'
            )
            items = response.get('Items', [])
            max_id = max([int(item['articleId']) for item in items], default=0)
            new_id = max_id + 1

            now = datetime.utcnow().isoformat() + 'Z'

            item = {
                'articleId': new_id,
                'title': article_data['title'],
                'content': article_data['content'],
                'category': article_data['category'],
                'status': article_data.get('status', 'draft'),
                'images': article_data.get('images', []),
                'tags': article_data.get('tags', []),
                'publishedAt': article_data.get('publishedAt', now if article_data.get('status') == 'published' else None),
                'createdBy': admin_id,
                'updatedBy': admin_id,
                'createdAt': now,
                'updatedAt': now
            }

            self.table.put_item(Item=item)

            logger.info(f"Article created successfully: {new_id}")
            return item

        except Exception as e:
            logger.error(f"Failed to create article: {str(e)}")
            raise

    def update(self, article_id: int, article_data: Dict[str, Any],
               admin_id: str) -> Optional[Dict[str, Any]]:
        """
        既存のコラムを更新

        Args:
            article_id: コラムID
            article_data: 更新するコラムデータ
            admin_id: 更新者の管理者ID

        Returns:
            更新されたコラム情報。見つからない場合はNone
        """
        try:
            # 既存のアイテムを確認
            existing = self.get_by_id(article_id)
            if not existing:
                return None

            now = datetime.utcnow().isoformat() + 'Z'

            # 更新する属性を構築
            update_expression = "SET "
            expression_values = {}
            expression_names = {}

            fields = ['title', 'content', 'category', 'status', 'images', 'tags', 'publishedAt']

            for field in fields:
                if field in article_data:
                    update_expression += f"#{field} = :{field}, "
                    expression_values[f":{field}"] = article_data[field]
                    expression_names[f"#{field}"] = field

            update_expression += "#updatedBy = :updatedBy, #updatedAt = :updatedAt"
            expression_values[":updatedBy"] = admin_id
            expression_values[":updatedAt"] = now
            expression_names["#updatedBy"] = "updatedBy"
            expression_names["#updatedAt"] = "updatedAt"

            response = self.table.update_item(
                Key={'articleId': article_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ReturnValues='ALL_NEW'
            )

            logger.info(f"Article updated successfully: {article_id}")
            return response.get('Attributes')

        except Exception as e:
            logger.error(f"Failed to update article {article_id}: {str(e)}")
            raise

    def delete(self, article_id: int) -> bool:
        """
        コラムを削除

        Args:
            article_id: コラムID

        Returns:
            削除に成功した場合True
        """
        try:
            self.table.delete_item(Key={'articleId': article_id})
            logger.info(f"Article deleted successfully: {article_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete article {article_id}: {str(e)}")
            return False

    def bulk_update_status(self, article_ids: List[int], status: str, admin_id: str) -> int:
        """
        複数のコラムのステータスを一括更新

        Args:
            article_ids: コラムIDのリスト
            status: 新しいステータス
            admin_id: 更新者の管理者ID

        Returns:
            更新された件数
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            updated_count = 0

            for article_id in article_ids:
                try:
                    self.table.update_item(
                        Key={'articleId': article_id},
                        UpdateExpression="SET #status = :status, #updatedBy = :updatedBy, #updatedAt = :updatedAt",
                        ExpressionAttributeNames={
                            '#status': 'status',
                            '#updatedBy': 'updatedBy',
                            '#updatedAt': 'updatedAt'
                        },
                        ExpressionAttributeValues={
                            ':status': status,
                            ':updatedBy': admin_id,
                            ':updatedAt': now
                        }
                    )
                    updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update article {article_id}: {str(e)}")

            logger.info(f"Bulk updated {updated_count} articles")
            return updated_count

        except Exception as e:
            logger.error(f"Failed to bulk update articles: {str(e)}")
            return 0

    def bulk_delete(self, article_ids: List[int]) -> int:
        """
        複数のコラムを一括削除

        Args:
            article_ids: コラムIDのリスト

        Returns:
            削除された件数
        """
        try:
            deleted_count = 0

            for article_id in article_ids:
                try:
                    self.table.delete_item(Key={'articleId': article_id})
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete article {article_id}: {str(e)}")

            logger.info(f"Bulk deleted {deleted_count} articles")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to bulk delete articles: {str(e)}")
            return 0
