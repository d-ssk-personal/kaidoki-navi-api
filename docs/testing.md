# テストガイド

## テスト構成

```
tests/
├── conftest.py                          # 共通フィクスチャとモックユーティリティ
├── unit/                                # ユニットテスト
│   └── admin/
│       ├── services/
│       │   └── test_article_service.py  # ArticleServiceのテスト
│       └── handlers/
│           └── test_articles_router.py  # articles_routerのテスト
└── integration/                         # 統合テスト (将来追加予定)
```

## テスト環境のセットアップ

### 1. 依存関係のインストール

```bash
# 開発用の依存関係をインストール
pip install -r requirements-dev.txt
```

### 2. テストの実行

#### 全てのテストを実行

```bash
pytest
```

#### カバレッジレポート付きで実行

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

#### 特定のテストファイルのみ実行

```bash
# ArticleServiceのテストのみ
pytest tests/unit/admin/services/test_article_service.py

# articles_routerのテストのみ
pytest tests/unit/admin/handlers/test_articles_router.py
```

#### マーカーを使用した実行

```bash
# ユニットテストのみ
pytest -m unit

# 統合テストのみ
pytest -m integration

# 遅いテストを除外
pytest -m "not slow"
```

#### 詳細な出力で実行

```bash
pytest -v
```

#### 特定のテストクラスまたはメソッドのみ実行

```bash
# 特定のクラス
pytest tests/unit/admin/services/test_article_service.py::TestArticleService

# 特定のメソッド
pytest tests/unit/admin/services/test_article_service.py::TestArticleService::test_list_articles_success
```

## テストカバレッジ

テストカバレッジレポートは `pytest.ini` の設定に基づいて自動生成されます。

- **HTML レポート**: `htmlcov/index.html` を開く
- **ターミナル出力**: テスト実行時に自動表示

```bash
# カバレッジレポートを生成してブラウザで開く
pytest --cov=src --cov-report=html
open htmlcov/index.html  # macOS
# または
xdg-open htmlcov/index.html  # Linux
```

## テストの書き方

### ユニットテストの例

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.mark.unit
class TestMyService:
    """MyServiceのテストクラス"""

    @patch('src.admin.services.my_service.MyRepository')
    def test_my_method_success(self, mock_repo):
        """メソッドが正常に動作することを確認"""
        # Arrange (準備)
        mock_repo.return_value.get_data.return_value = {'id': 1}
        service = MyService()

        # Act (実行)
        result = service.my_method(1)

        # Assert (検証)
        assert result['id'] == 1
        mock_repo.return_value.get_data.assert_called_once_with(1)
```

### フィクスチャの使用

```python
def test_with_token(system_admin_token):
    """フィクスチャを使用したテスト"""
    # system_admin_tokenはconftest.pyで定義されている
    assert system_admin_token is not None
```

## 共通フィクスチャ

`tests/conftest.py` に定義されている主なフィクスチャ:

- `jwt_secret_key`: JWT秘密鍵
- `system_admin_token`: システム管理者のJWTトークン
- `company_admin_token`: 企業管理者のJWTトークン
- `expired_token`: 期限切れのJWTトークン
- `api_gateway_event_base`: API Gatewayイベントのベース
- `api_gateway_event_with_auth`: 認証付きAPI Gatewayイベント
- `mock_article_repository`: ArticleRepositoryのモック
- `sample_article_data`: サンプル記事データ
- `sample_article_response`: サンプル記事レスポンスデータ
- `lambda_context`: Lambda contextのモック

## テストの種類

### ユニットテスト (`@pytest.mark.unit`)

- 個々の関数やメソッドのテスト
- 外部依存をモック化
- 高速に実行可能
- コードカバレッジの向上

### 統合テスト (`@pytest.mark.integration`)

- 複数のコンポーネントの連携テスト
- DynamoDB Localなど外部サービスを使用
- 実際の環境に近いテスト

## CI/CDでのテスト実行

GitHub Actionsなどで自動テストを実行する場合:

```yaml
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## トラブルシューティング

### ImportError が発生する場合

```bash
# PYTHONPATHを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### DynamoDB Local関連のエラー

```bash
# Docker環境を起動
./scripts/start-local.sh

# DynamoDB_ENDPOINT_URLを設定
export DYNAMODB_ENDPOINT_URL=http://localhost:8000
pytest -m integration
```

### モジュールが見つからない場合

```bash
# 依存関係を再インストール
pip install -r requirements-dev.txt --upgrade
```

## ベストプラクティス

1. **AAA パターンを使用**: Arrange (準備), Act (実行), Assert (検証)
2. **テスト名は明確に**: `test_<機能>_<条件>_<期待結果>`
3. **1つのテストで1つのことを検証**: 各テストは1つの機能のみをテスト
4. **モックは必要最小限に**: 過度なモックは避ける
5. **テストデータは共通フィクスチャで管理**: 重複を避ける
6. **例外ケースもテスト**: 正常系だけでなく異常系もテスト

## テストカバレッジ目標

- **全体**: 80%以上
- **ビジネスロジック（Services層）**: 90%以上
- **ハンドラー層**: 85%以上
- **リポジトリ層**: 80%以上

## 参考リンク

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
