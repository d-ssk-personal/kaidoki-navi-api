# アーキテクチャ設計

## レイヤードアーキテクチャ

このプロジェクトは、以下のレイヤードアーキテクチャを採用しています。

```
┌─────────────────────────────────────┐
│         API Gateway                 │
│   (ルーティング・認証・検証)         │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│      Handlers (Router層)            │
│  - リクエスト受取                    │
│  - レスポンス返却                    │
│  - 認証チェック                      │
│  - バリデーション                    │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│       Services層                     │
│  - ビジネスロジック                  │
│  - トランザクション制御              │
│  - 画像アップロード処理              │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│     Repositories層                   │
│  - データベースアクセス              │
│  - CRUD操作                          │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         DynamoDB                     │
└─────────────────────────────────────┘
```

## ディレクトリ構成

```
src/
├── admin/                 # 管理者API
│   ├── handlers/         # Lambda関数ハンドラ
│   │   ├── auth.py                      # 認証
│   │   └── articles_router.py           # コラム管理ルーター
│   ├── services/         # ビジネスロジック
│   │   └── article_service.py           # コラム管理サービス
│   └── repositories/     # データベースアクセス
│       ├── admin_repository.py          # 管理者テーブル
│       └── article_repository.py        # 記事テーブル
├── user/                  # ユーザーAPI（未実装）
├── utils/                 # 共通ユーティリティ
│   ├── auth.py           # JWT認証
│   ├── response.py       # APIレスポンス
│   ├── logger.py         # ロギング
│   └── s3.py             # S3画像アップロード
└── config/               # 設定
    └── settings.py       # 環境設定
```

## 各レイヤーの役割

### 1. Handlers層（Router）

**役割**: API Gatewayからのリクエストを受け取り、レスポンスを返却

**責務**:
- リクエストの受取
- 認証チェック
- リクエストパラメータのバリデーション
- Services層への委譲
- レスポンスの整形と返却
- エラーハンドリング

**例**:
```python
# handlers/articles_router.py
def route_articles(event, context):
    """ルーティング処理"""
    # パスとメソッドで振り分け
    if http_method == 'GET' and path.endswith('/list'):
        return list_articles(event)
    # ...

def list_articles(event):
    """薄いハンドラー"""
    # 1. 認証チェック
    admin = require_role(event, ['system_admin'])

    # 2. パラメータ取得
    params = event.get('queryStringParameters') or {}

    # 3. Services層に委譲
    service = ArticleService()
    articles, total, total_pages = service.list_articles(...)

    # 4. レスポンス返却
    return success_response({...})
```

### 2. Services層

**役割**: ビジネスロジックの実装

**責務**:
- ビジネスルールの適用
- 複数のRepositoryの組み合わせ
- トランザクション制御
- 外部サービス連携（S3など）

**例**:
```python
# services/article_service.py
class ArticleService:
    def create_article(self, article_data):
        # 1. 画像アップロード
        if 'image' in article_data:
            image_url = upload_image(...)
            article_data['imageUrl'] = image_url

        # 2. データ作成
        article = self.article_repo.create(article_data)

        # 3. ログ記録
        logger.info(f"Created article: {article['articleId']}")

        return article
```

### 3. Repositories層

**役割**: データベースアクセスの抽象化

**責務**:
- DynamoDBへのCRUD操作
- クエリの構築と実行
- データの変換（DynamoDB ↔ Python辞書）

**例**:
```python
# repositories/article_repository.py
class ArticleRepository:
    def list_articles(self, filters, page, limit):
        # DynamoDBクエリを実行
        response = self.table.scan(...)
        return items, total_count
```

## コールドスタート対策

### 問題

AWS Lambdaでは、関数が初めて呼ばれる時（または長時間使用されていない後）にコールドスタートが発生し、レスポンスが遅くなります。

### 解決策: Lambda関数の統合

**変更前**: 7つのLambda関数
```
- ArticlesListFunction
- ArticleGetFunction
- ArticleCreateFunction
- ArticleUpdateFunction
- ArticleDeleteFunction
- ArticleBulkStatusFunction
- ArticleBulkDeleteFunction
```

**変更後**: 1つのLambda関数
```
- ArticlesApiFunction (全てのエンドポイントを処理)
```

### メリット

1. **コールドスタートの削減**
   - Lambda関数数: 7 → 1
   - コールドスタート発生頻度が大幅に減少

2. **管理の簡素化**
   - デプロイが簡単
   - ログの一元管理

3. **コスト削減**
   - Lambda関数の実行料金が削減される可能性

### デメリットと対策

**デメリット1**: 1つのエンドポイントが遅いと、他にも影響
- **対策**: タイムアウト設定を適切に設定

**デメリット2**: デプロイパッケージサイズが大きくなる
- **対策**: 必要な依存関係のみをインストール

## API呼び出しフロー

### 例: コラム一覧取得

```
1. クライアント
   ↓ GET /admin/articles/list?page=1&limit=10

2. API Gateway
   ↓ ArticlesApiFunction を呼び出し

3. Handlers (articles_router.py)
   ↓ route_articles() → list_articles()
   ├─ 認証チェック: require_role()
   ├─ パラメータ取得: filters, page, limit
   └─ Services層に委譲

4. Services (article_service.py)
   ↓ ArticleService.list_articles()
   ├─ ビジネスロジック: ページネーション計算
   └─ Repository層に委譲

5. Repositories (article_repository.py)
   ↓ ArticleRepository.list_articles()
   └─ DynamoDBクエリ実行

6. DynamoDB
   ↓ データ取得

7. Repositories
   ↓ データを返す

8. Services
   ↓ ページネーション情報を追加

9. Handlers
   ↓ レスポンスを整形

10. API Gateway
    ↓ JSONレスポンス

11. クライアント
    ← { "items": [...], "pagination": {...} }
```

## 設計原則

### 1. 単一責任の原則（SRP）

各レイヤーは明確な責任を持ち、それ以外のことはしない。

- **Handler**: リクエスト受取とレスポンス返却のみ
- **Service**: ビジネスロジックのみ
- **Repository**: データベースアクセスのみ

### 2. 依存性逆転の原則（DIP）

上位レイヤーは下位レイヤーに依存するが、具体実装ではなくインターフェースに依存する。

```
Handler → Service → Repository
  (抽象)   (抽象)     (具体)
```

### 3. 開放閉鎖の原則（OCP）

新機能追加時は既存コードを変更せず、新しいコードを追加する。

例: 新しいAPIを追加する場合
1. Serviceに新しいメソッドを追加
2. Handlerに新しい関数を追加
3. Routerにルーティングを追加
4. template.yamlにイベントを追加

## テストの方針

### ユニットテスト

各レイヤーを独立してテスト可能。

```python
# Services層のテスト
def test_create_article():
    # Repositoryをモック化
    repo_mock = Mock()
    repo_mock.create.return_value = {'articleId': 1}

    service = ArticleService()
    service.article_repo = repo_mock

    result = service.create_article({'title': 'Test'})
    assert result['articleId'] == 1
```

### 統合テスト

SAM Localを使用してローカルでAPIをテスト。

```bash
sam local start-api
curl http://localhost:3000/admin/articles/list
```

## まとめ

- **レイヤードアーキテクチャ**: Handler → Service → Repository
- **Handler層は薄く**: リクエスト受取とレスポンス返却のみ
- **ビジネスロジックはServices層**: 再利用可能で テスト可能
- **コールドスタート対策**: 関連APIを1つのLambda関数に統合
- **明確な責任分離**: 各レイヤーの役割を明確に

この設計により、保守性・拡張性・テスタビリティの高いAPIを実現できます。
