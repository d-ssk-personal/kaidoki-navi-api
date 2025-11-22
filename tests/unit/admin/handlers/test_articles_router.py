"""
articles_router ハンドラーテスト
Lambda関数ハンドラー層のテスト
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from src.admin.handlers.articles_router import (
    route_articles,
    list_articles,
    get_article,
    create_article,
    update_article,
    delete_article,
    bulk_update_status,
    bulk_delete_articles
)


@pytest.mark.unit
class TestArticlesRouter:
    """ルーティング機能のテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_route_articles_list(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        lambda_context
    ):
        """GET /admin/articles/list のルーティングを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.list_articles.return_value = ([], 0, 1)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'httpMethod': 'GET',
            'path': '/admin/articles/list',
            'pathParameters': None,
            'queryStringParameters': {},
            'headers': {'Authorization': f'Bearer {system_admin_token}'},
            'body': None
        }

        # Act
        response = route_articles(event, lambda_context)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'items' in body
        assert 'pagination' in body

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_route_articles_get(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_response,
        lambda_context
    ):
        """GET /admin/articles/list/{articleId} のルーティングを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.get_article.return_value = sample_article_response
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'httpMethod': 'GET',
            'path': '/admin/articles/list/1',
            'pathParameters': {'articleId': '1'},
            'queryStringParameters': None,
            'headers': {'Authorization': f'Bearer {system_admin_token}'},
            'body': None
        }

        # Act
        response = route_articles(event, lambda_context)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['articleId'] == 1

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_route_articles_create(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_data,
        sample_article_response,
        lambda_context
    ):
        """POST /admin/articles/add のルーティングを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.create_article.return_value = sample_article_response
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'httpMethod': 'POST',
            'path': '/admin/articles/add',
            'pathParameters': None,
            'queryStringParameters': None,
            'headers': {'Authorization': f'Bearer {system_admin_token}'},
            'body': json.dumps(sample_article_data)
        }

        # Act
        response = route_articles(event, lambda_context)

        # Assert
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['articleId'] == 1

    def test_route_articles_unsupported_route(self, lambda_context):
        """サポートされていないルートの場合400を返すことを確認"""
        # Arrange
        event = {
            'httpMethod': 'PATCH',
            'path': '/admin/articles/unknown',
            'pathParameters': None,
            'queryStringParameters': None,
            'headers': {},
            'body': None
        }

        # Act
        response = route_articles(event, lambda_context)

        # Assert
        assert response['statusCode'] == 400


@pytest.mark.unit
class TestListArticles:
    """コラム一覧取得ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_list_articles_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_response
    ):
        """コラム一覧取得が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.list_articles.return_value = ([sample_article_response], 1, 1)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'queryStringParameters': {
                'page': '1',
                'limit': '20',
                'status': 'published'
            },
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = list_articles(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['items']) == 1
        assert body['pagination']['currentPage'] == 1
        assert body['pagination']['totalPages'] == 1
        assert body['pagination']['totalItems'] == 1

    @patch('src.admin.handlers.articles_router.require_role')
    def test_list_articles_unauthorized(self, mock_require_role):
        """認証エラーの場合403を返すことを確認"""
        # Arrange
        mock_require_role.side_effect = ValueError("Authentication required")

        event = {
            'queryStringParameters': {},
            'headers': {}
        }

        # Act
        response = list_articles(event)

        # Assert
        assert response['statusCode'] == 403

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_list_articles_with_filters(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """フィルター条件が正しく渡されることを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.list_articles.return_value = ([], 0, 1)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'queryStringParameters': {
                'search': 'テスト',
                'status': 'published',
                'category': 'テクノロジー',
                'tags': 'AI,ML',
                'dateFrom': '2025-01-01',
                'dateTo': '2025-12-31'
            },
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = list_articles(event)

        # Assert
        assert response['statusCode'] == 200
        # フィルターが正しく渡されたことを確認
        call_args = mock_service.list_articles.call_args[0]
        filters = call_args[0]
        assert filters['search'] == 'テスト'
        assert filters['status'] == 'published'
        assert filters['category'] == 'テクノロジー'


@pytest.mark.unit
class TestGetArticle:
    """コラム詳細取得ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_get_article_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_response
    ):
        """コラム詳細取得が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.get_article.return_value = sample_article_response
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '1'},
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = get_article(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['articleId'] == 1
        mock_service.get_article.assert_called_once_with(1)

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_get_article_not_found(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """存在しない記事の場合404を返すことを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.get_article.return_value = None
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '999'},
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = get_article(event)

        # Assert
        assert response['statusCode'] == 404

    @patch('src.admin.handlers.articles_router.require_role')
    def test_get_article_invalid_id(self, mock_require_role, system_admin_token):
        """不正なIDの場合400を返すことを確認"""
        # Arrange
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': 'invalid'},
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = get_article(event)

        # Assert
        assert response['statusCode'] == 400


@pytest.mark.unit
class TestCreateArticle:
    """コラム作成ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_create_article_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_data,
        sample_article_response
    ):
        """コラム作成が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.create_article.return_value = sample_article_response
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps(sample_article_data),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = create_article(event)

        # Assert
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['articleId'] == 1

    @patch('src.admin.handlers.articles_router.require_role')
    def test_create_article_missing_required_field(
        self,
        mock_require_role,
        system_admin_token
    ):
        """必須フィールドが欠けている場合400を返すことを確認"""
        # Arrange
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps({'title': 'テスト'}),  # contentなど必須フィールドが欠けている
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = create_article(event)

        # Assert
        assert response['statusCode'] == 400

    @patch('src.admin.handlers.articles_router.require_role')
    def test_create_article_invalid_json(self, mock_require_role, system_admin_token):
        """不正なJSONの場合400を返すことを確認"""
        # Arrange
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': 'invalid json{',
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = create_article(event)

        # Assert
        assert response['statusCode'] == 400


@pytest.mark.unit
class TestUpdateArticle:
    """コラム更新ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_update_article_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token,
        sample_article_response
    ):
        """コラム更新が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.update_article.return_value = sample_article_response
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '1'},
            'body': json.dumps({'title': '更新されたタイトル'}),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = update_article(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['articleId'] == 1

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_update_article_not_found(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """存在しない記事の更新時404を返すことを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.update_article.return_value = None
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '999'},
            'body': json.dumps({'title': '更新'}),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = update_article(event)

        # Assert
        assert response['statusCode'] == 404


@pytest.mark.unit
class TestDeleteArticle:
    """コラム削除ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_delete_article_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """コラム削除が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.delete_article.return_value = True
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '1'},
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = delete_article(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'message' in body

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_delete_article_not_found(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """存在しない記事の削除時404を返すことを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.delete_article.return_value = False
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'pathParameters': {'articleId': '999'},
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = delete_article(event)

        # Assert
        assert response['statusCode'] == 404


@pytest.mark.unit
class TestBulkUpdateStatus:
    """ステータス一括更新ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_bulk_update_status_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """ステータス一括更新が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.bulk_update_status.return_value = (3, 0)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps({
                'articleIds': [1, 2, 3],
                'status': 'published'
            }),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = bulk_update_status(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successCount'] == 3
        assert body['failedCount'] == 0

    @patch('src.admin.handlers.articles_router.require_role')
    def test_bulk_update_status_missing_fields(
        self,
        mock_require_role,
        system_admin_token
    ):
        """必須フィールドが欠けている場合400を返すことを確認"""
        # Arrange
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps({'articleIds': [1, 2, 3]}),  # statusがない
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = bulk_update_status(event)

        # Assert
        assert response['statusCode'] == 400


@pytest.mark.unit
class TestBulkDeleteArticles:
    """記事一括削除ハンドラーのテスト"""

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_bulk_delete_articles_success(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """記事一括削除が正常に動作することを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.bulk_delete_articles.return_value = (3, 0)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps({'articleIds': [1, 2, 3]}),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = bulk_delete_articles(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successCount'] == 3
        assert body['failedCount'] == 0

    @patch('src.admin.handlers.articles_router.require_role')
    @patch('src.admin.handlers.articles_router.ArticleService')
    def test_bulk_delete_articles_partial_failure(
        self,
        mock_service_class,
        mock_require_role,
        system_admin_token
    ):
        """一部失敗する場合も正しく結果を返すことを確認"""
        # Arrange
        mock_service = MagicMock()
        mock_service.bulk_delete_articles.return_value = (2, 1)
        mock_service_class.return_value = mock_service
        mock_require_role.return_value = {'adminId': 1, 'role': 'system_admin'}

        event = {
            'body': json.dumps({'articleIds': [1, 2, 3]}),
            'headers': {'Authorization': f'Bearer {system_admin_token}'}
        }

        # Act
        response = bulk_delete_articles(event)

        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successCount'] == 2
        assert body['failedCount'] == 1
