"""
ArticleService ユニットテスト
ビジネスロジック層のテスト
"""
import pytest
from unittest.mock import patch, MagicMock, call
from src.admin.services.article_service import ArticleService


@pytest.mark.unit
class TestArticleService:
    """ArticleServiceのテストクラス"""

    def test_list_articles_success(self, mock_article_repository):
        """コラム一覧取得が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            filters = {'status': 'published'}
            page = 1
            limit = 20

            # Act
            articles, total, total_pages = service.list_articles(filters, page, limit)

            # Assert
            assert len(articles) == 1
            assert total == 1
            assert total_pages == 1
            assert articles[0]['title'] == 'テスト記事'
            mock_article_repository.list_articles.assert_called_once_with(filters, page, limit)

    def test_list_articles_pagination(self, mock_article_repository):
        """ページネーション計算が正しく動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.list_articles.return_value = ([], 45)
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            articles, total, total_pages = service.list_articles({}, 1, 20)

            # Assert
            assert total == 45
            assert total_pages == 3  # 45 / 20 = 2.25 -> 3

    def test_list_articles_empty(self, mock_article_repository):
        """記事が0件の場合でも正しく動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.list_articles.return_value = ([], 0)
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            articles, total, total_pages = service.list_articles({}, 1, 20)

            # Assert
            assert len(articles) == 0
            assert total == 0
            assert total_pages == 1

    def test_get_article_success(self, mock_article_repository):
        """コラム詳細取得が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            article = service.get_article(1)

            # Assert
            assert article is not None
            assert article['articleId'] == 1
            assert article['title'] == 'テスト記事'
            mock_article_repository.get_by_id.assert_called_once_with(1)

    def test_get_article_not_found(self, mock_article_repository):
        """存在しない記事の取得時にNoneを返すことを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.get_by_id.return_value = None
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            article = service.get_article(999)

            # Assert
            assert article is None
            mock_article_repository.get_by_id.assert_called_once_with(999)

    @patch('src.admin.services.article_service.upload_image')
    def test_create_article_with_image(self, mock_upload_image, mock_article_repository):
        """画像付きコラム作成が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            mock_upload_image.return_value = 'https://s3.example.com/articles/new-image.jpg'

            service = ArticleService()
            article_data = {
                'title': '新しい記事',
                'content': '記事の内容',
                'category': 'テクノロジー',
                'status': 'draft',
                'image': 'base64encodedimagedata'
            }

            # Act
            result = service.create_article(article_data)

            # Assert
            assert result is not None
            mock_upload_image.assert_called_once_with('base64encodedimagedata', 'articles', 'jpg')
            # imageフィールドが削除され、imageUrlが追加されることを確認
            assert 'image' not in article_data
            assert 'imageUrl' in article_data
            mock_article_repository.create.assert_called_once()

    def test_create_article_without_image(self, mock_article_repository):
        """画像なしコラム作成が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_data = {
                'title': '新しい記事',
                'content': '記事の内容',
                'category': 'テクノロジー',
                'status': 'draft'
            }

            # Act
            result = service.create_article(article_data)

            # Assert
            assert result is not None
            mock_article_repository.create.assert_called_once_with(article_data)

    @patch('src.admin.services.article_service.delete_image')
    @patch('src.admin.services.article_service.upload_image')
    def test_update_article_replace_image(
        self,
        mock_upload_image,
        mock_delete_image,
        mock_article_repository
    ):
        """画像を置き換える更新が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            mock_upload_image.return_value = 'https://s3.example.com/articles/updated-image.jpg'

            service = ArticleService()
            update_data = {
                'title': '更新された記事',
                'image': 'base64newimagedata'
            }

            # Act
            result = service.update_article(1, update_data)

            # Assert
            assert result is not None
            # 古い画像が削除されることを確認
            mock_delete_image.assert_called_once_with('https://s3.example.com/articles/test.jpg')
            # 新しい画像がアップロードされることを確認
            mock_upload_image.assert_called_once_with('base64newimagedata', 'articles', 'jpg')
            mock_article_repository.update.assert_called_once()

    def test_update_article_not_found(self, mock_article_repository):
        """存在しない記事の更新時にNoneを返すことを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.get_by_id.return_value = None
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            result = service.update_article(999, {'title': '更新'})

            # Assert
            assert result is None
            mock_article_repository.update.assert_not_called()

    @patch('src.admin.services.article_service.delete_image')
    def test_delete_article_with_image(self, mock_delete_image, mock_article_repository):
        """画像付き記事の削除が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            result = service.delete_article(1)

            # Assert
            assert result is True
            # 画像が削除されることを確認
            mock_delete_image.assert_called_once_with('https://s3.example.com/articles/test.jpg')
            mock_article_repository.delete.assert_called_once_with(1)

    def test_delete_article_not_found(self, mock_article_repository):
        """存在しない記事の削除時にFalseを返すことを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.get_by_id.return_value = None
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            # Act
            result = service.delete_article(999)

            # Assert
            assert result is False
            mock_article_repository.delete.assert_not_called()

    def test_bulk_update_status_success(self, mock_article_repository):
        """ステータス一括更新が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.update.return_value = {'articleId': 1}
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_ids = [1, 2, 3]
            status = 'published'

            # Act
            success_count, failed_count = service.bulk_update_status(article_ids, status)

            # Assert
            assert success_count == 3
            assert failed_count == 0
            assert mock_article_repository.update.call_count == 3

    def test_bulk_update_status_partial_failure(self, mock_article_repository):
        """一部失敗するステータス一括更新を確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            # 1件目成功、2件目失敗、3件目成功
            mock_article_repository.update.side_effect = [
                {'articleId': 1},
                None,
                {'articleId': 3}
            ]
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_ids = [1, 2, 3]
            status = 'published'

            # Act
            success_count, failed_count = service.bulk_update_status(article_ids, status)

            # Assert
            assert success_count == 2
            assert failed_count == 1

    @patch('src.admin.services.article_service.delete_image')
    def test_bulk_delete_articles_success(self, mock_delete_image, mock_article_repository):
        """記事一括削除が正常に動作することを確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            # 各記事の画像URLを返す
            mock_article_repository.get_by_id.side_effect = [
                {'articleId': 1, 'imageUrl': 'https://s3.example.com/1.jpg'},
                {'articleId': 2, 'imageUrl': 'https://s3.example.com/2.jpg'},
                {'articleId': 3, 'imageUrl': 'https://s3.example.com/3.jpg'}
            ]
            mock_article_repository.delete.return_value = True
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_ids = [1, 2, 3]

            # Act
            success_count, failed_count = service.bulk_delete_articles(article_ids)

            # Assert
            assert success_count == 3
            assert failed_count == 0
            assert mock_delete_image.call_count == 3
            assert mock_article_repository.delete.call_count == 3

    @patch('src.admin.services.article_service.delete_image')
    def test_bulk_delete_articles_partial_failure(self, mock_delete_image, mock_article_repository):
        """一部失敗する記事一括削除を確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.get_by_id.side_effect = [
                {'articleId': 1, 'imageUrl': 'https://s3.example.com/1.jpg'},
                {'articleId': 2, 'imageUrl': 'https://s3.example.com/2.jpg'},
                {'articleId': 3, 'imageUrl': 'https://s3.example.com/3.jpg'}
            ]
            # 1件目成功、2件目失敗、3件目成功
            mock_article_repository.delete.side_effect = [True, False, True]
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_ids = [1, 2, 3]

            # Act
            success_count, failed_count = service.bulk_delete_articles(article_ids)

            # Assert
            assert success_count == 2
            assert failed_count == 1

    def test_bulk_delete_articles_with_exception(self, mock_article_repository):
        """例外が発生した場合の一括削除を確認"""
        # Arrange
        with patch('src.admin.services.article_service.ArticleRepository') as MockRepo:
            mock_article_repository.get_by_id.side_effect = [
                {'articleId': 1},
                Exception('Database error'),
                {'articleId': 3}
            ]
            mock_article_repository.delete.return_value = True
            MockRepo.return_value = mock_article_repository
            service = ArticleService()

            article_ids = [1, 2, 3]

            # Act
            success_count, failed_count = service.bulk_delete_articles(article_ids)

            # Assert
            assert success_count == 2
            assert failed_count == 1
