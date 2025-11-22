"""
コラム管理サービス
ビジネスロジックを担当
"""
from typing import Dict, Any, List, Tuple, Optional
from src.admin.repositories.article_repository import ArticleRepository
from src.utils.logger import get_logger
from src.utils.s3 import upload_image, delete_image

logger = get_logger(__name__)


class ArticleService:
    """コラム管理のビジネスロジック"""

    def __init__(self):
        self.article_repo = ArticleRepository()

    def list_articles(
        self,
        filters: Dict[str, Any],
        page: int,
        limit: int
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        コラム一覧を取得

        Args:
            filters: フィルター条件
            page: ページ番号
            limit: 1ページあたりの件数

        Returns:
            (記事リスト, 総件数, 総ページ数)
        """
        articles, total = self.article_repo.list_articles(filters, page, limit)
        total_pages = (total + limit - 1) // limit if total > 0 else 1

        return articles, total, total_pages

    def get_article(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        コラム詳細を取得

        Args:
            article_id: コラムID

        Returns:
            コラム情報（見つからない場合はNone）
        """
        return self.article_repo.get_by_id(article_id)

    def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        コラムを作成

        Args:
            article_data: コラムデータ

        Returns:
            作成されたコラム情報
        """
        # 画像アップロード処理
        if 'image' in article_data and article_data['image']:
            image_url = upload_image(
                article_data['image'],
                'articles',
                'jpg'
            )
            article_data['imageUrl'] = image_url
            del article_data['image']

        # 記事を作成
        article = self.article_repo.create(article_data)
        logger.info(f"Created article: {article.get('articleId')}")

        return article

    def update_article(
        self,
        article_id: int,
        article_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        コラムを更新

        Args:
            article_id: コラムID
            article_data: 更新データ

        Returns:
            更新されたコラム情報（見つからない場合はNone）
        """
        # 既存記事の確認
        existing_article = self.article_repo.get_by_id(article_id)
        if not existing_article:
            return None

        # 画像アップロード処理
        if 'image' in article_data and article_data['image']:
            # 古い画像を削除
            if existing_article.get('imageUrl'):
                delete_image(existing_article['imageUrl'])

            # 新しい画像をアップロード
            image_url = upload_image(
                article_data['image'],
                'articles',
                'jpg'
            )
            article_data['imageUrl'] = image_url
            del article_data['image']

        # 記事を更新
        updated_article = self.article_repo.update(article_id, article_data)
        logger.info(f"Updated article: {article_id}")

        return updated_article

    def delete_article(self, article_id: int) -> bool:
        """
        コラムを削除

        Args:
            article_id: コラムID

        Returns:
            削除成功ならTrue、見つからない場合はFalse
        """
        # 既存記事の確認
        existing_article = self.article_repo.get_by_id(article_id)
        if not existing_article:
            return False

        # 画像を削除
        if existing_article.get('imageUrl'):
            delete_image(existing_article['imageUrl'])

        # 記事を削除
        success = self.article_repo.delete(article_id)

        if success:
            logger.info(f"Deleted article: {article_id}")

        return success

    def bulk_update_status(
        self,
        article_ids: List[int],
        status: str
    ) -> Tuple[int, int]:
        """
        複数コラムのステータスを一括更新

        Args:
            article_ids: コラムIDのリスト
            status: 新しいステータス

        Returns:
            (成功件数, 失敗件数)
        """
        success_count = 0
        failed_count = 0

        for article_id in article_ids:
            try:
                result = self.article_repo.update(article_id, {'status': status})
                if result:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to update article {article_id}: {str(e)}")
                failed_count += 1

        logger.info(
            f"Bulk update status: success={success_count}, failed={failed_count}"
        )

        return success_count, failed_count

    def bulk_delete_articles(self, article_ids: List[int]) -> Tuple[int, int]:
        """
        複数コラムを一括削除

        Args:
            article_ids: コラムIDのリスト

        Returns:
            (成功件数, 失敗件数)
        """
        success_count = 0
        failed_count = 0

        for article_id in article_ids:
            try:
                # 記事情報を取得（画像削除のため）
                article = self.article_repo.get_by_id(article_id)
                if article and article.get('imageUrl'):
                    delete_image(article['imageUrl'])

                # 記事を削除
                if self.article_repo.delete(article_id):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Failed to delete article {article_id}: {str(e)}")
                failed_count += 1

        logger.info(
            f"Bulk delete articles: success={success_count}, failed={failed_count}"
        )

        return success_count, failed_count
