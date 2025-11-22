"""
共通のテストフィクスチャとユーティリティ
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import jwt
import pytest
from unittest.mock import MagicMock, Mock


# 環境変数の設定
os.environ['AWS_REGION'] = 'ap-northeast-1'
os.environ['DYNAMODB_ENDPOINT_URL'] = 'http://localhost:8000'
os.environ['ARTICLES_TABLE_NAME'] = 'articles'
os.environ['ADMINS_TABLE_NAME'] = 'admins'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'


@pytest.fixture
def jwt_secret_key():
    """JWT秘密鍵"""
    return 'test-secret-key'


@pytest.fixture
def system_admin_token(jwt_secret_key):
    """システム管理者のJWTトークン"""
    payload = {
        'adminId': 1,
        'username': 'system_admin',
        'role': 'system_admin',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, jwt_secret_key, algorithm='HS256')


@pytest.fixture
def company_admin_token(jwt_secret_key):
    """企業管理者のJWTトークン"""
    payload = {
        'adminId': 2,
        'username': 'company_admin',
        'role': 'company_admin',
        'companyId': 100,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, jwt_secret_key, algorithm='HS256')


@pytest.fixture
def expired_token(jwt_secret_key):
    """期限切れのJWTトークン"""
    payload = {
        'adminId': 1,
        'username': 'system_admin',
        'role': 'system_admin',
        'exp': datetime.utcnow() - timedelta(hours=1)
    }
    return jwt.encode(payload, jwt_secret_key, algorithm='HS256')


@pytest.fixture
def api_gateway_event_base():
    """API Gatewayイベントのベース"""
    return {
        'httpMethod': 'GET',
        'path': '/admin/articles/list',
        'pathParameters': None,
        'queryStringParameters': None,
        'headers': {},
        'body': None,
        'requestContext': {
            'requestId': 'test-request-id',
            'accountId': '123456789012',
            'stage': 'test'
        }
    }


@pytest.fixture
def api_gateway_event_with_auth(api_gateway_event_base, system_admin_token):
    """認証付きAPI Gatewayイベント"""
    event = api_gateway_event_base.copy()
    event['headers'] = {
        'Authorization': f'Bearer {system_admin_token}'
    }
    return event


def create_api_event(
    method: str = 'GET',
    path: str = '/admin/articles/list',
    path_params: Dict[str, Any] = None,
    query_params: Dict[str, Any] = None,
    body: Dict[str, Any] = None,
    token: str = None
) -> Dict[str, Any]:
    """API Gatewayイベントを生成するヘルパー関数"""
    import json

    event = {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_params,
        'queryStringParameters': query_params,
        'headers': {},
        'body': json.dumps(body) if body else None,
        'requestContext': {
            'requestId': 'test-request-id',
            'accountId': '123456789012',
            'stage': 'test'
        }
    }

    if token:
        event['headers']['Authorization'] = f'Bearer {token}'

    return event


@pytest.fixture
def mock_article_repository():
    """ArticleRepositoryのモック"""
    mock_repo = MagicMock()

    # デフォルトの記事データ
    mock_article = {
        'articleId': 1,
        'title': 'テスト記事',
        'content': 'これはテスト記事の内容です',
        'category': 'テクノロジー',
        'status': 'published',
        'imageUrl': 'https://s3.example.com/articles/test.jpg',
        'tags': ['テスト', 'サンプル'],
        'publishedAt': '2025-01-01T00:00:00Z',
        'createdAt': '2025-01-01T00:00:00Z',
        'updatedAt': '2025-01-01T00:00:00Z'
    }

    # list_articlesのモック
    mock_repo.list_articles.return_value = ([mock_article], 1)

    # get_by_idのモック
    mock_repo.get_by_id.return_value = mock_article

    # createのモック
    mock_repo.create.return_value = mock_article

    # updateのモック
    mock_repo.update.return_value = mock_article

    # deleteのモック
    mock_repo.delete.return_value = True

    return mock_repo


@pytest.fixture
def sample_article_data():
    """サンプル記事データ"""
    return {
        'title': 'テスト記事',
        'content': 'これはテスト記事の内容です',
        'category': 'テクノロジー',
        'status': 'draft',
        'tags': ['テスト', 'サンプル'],
        'publishedAt': '2025-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_article_response():
    """サンプル記事レスポンスデータ"""
    return {
        'articleId': 1,
        'title': 'テスト記事',
        'content': 'これはテスト記事の内容です',
        'category': 'テクノロジー',
        'status': 'published',
        'imageUrl': 'https://s3.example.com/articles/test.jpg',
        'tags': ['テスト', 'サンプル'],
        'publishedAt': '2025-01-01T00:00:00Z',
        'createdAt': '2025-01-01T00:00:00Z',
        'updatedAt': '2025-01-01T00:00:00Z'
    }


@pytest.fixture
def lambda_context():
    """Lambda contextのモック"""
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '$LATEST'
    context.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:123456789012:function:test-function'
    context.memory_limit_in_mb = 128
    context.aws_request_id = 'test-request-id'
    context.log_group_name = '/aws/lambda/test-function'
    context.log_stream_name = '2025/01/01/[$LATEST]test-stream'

    def get_remaining_time():
        return 300000  # 5分

    context.get_remaining_time_in_millis = get_remaining_time

    return context
