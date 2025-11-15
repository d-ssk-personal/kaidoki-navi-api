# 買いどきナビ API設計書の説明とガイド

## 📋 概要

OpenAPI 3.0形式で作成されたAPI設計書です。

### API エンドポイント一覧

| カテゴリ | メソッド | エンドポイント | 説明 | 認証 |
|---------|---------|---------------|------|-----|
| **商品** | GET | `/products` | 商品一覧取得 | 不要 |
| | GET | `/products/{productId}` | 商品詳細取得 | 不要 |
| | GET | `/products/{productId}/price-history` | 価格履歴取得 | 不要 |
| **カテゴリ** | GET | `/categories` | カテゴリ一覧取得 | 不要 |
| **お気に入り** | GET | `/favorites` | お気に入り一覧取得 | 必要 |
| | POST | `/favorites` | お気に入り追加 | 必要 |
| | DELETE | `/favorites/{productId}` | お気に入り削除 | 必要 |
| **通知設定** | GET | `/notifications/settings` | 通知設定取得 | 必要 |
| | PUT | `/notifications/settings` | 通知設定更新 | 必要 |
| | POST | `/notifications/line/connect` | LINE連携 | 必要 |
| | POST | `/notifications/line/disconnect` | LINE連携解除 | 必要 |
| **お問い合わせ** | POST | `/contact` | お問い合わせ送信 | 不要 |

## 🔑 認証方式

JWT (JSON Web Token) によるBearer認証を使用します。

### リクエスト例
```bash
curl -H "Authorization: Bearer {JWT_TOKEN}" \
  https://api.kaidoki-navi.example.com/v1/favorites
```

## 📊 主要なエンドポイント詳細

### 1. 商品一覧取得 `GET /products`

#### クエリパラメータ
- `keyword`: 検索キーワード（商品名で部分一致）
- `category`: カテゴリフィルター
- `sort`: ソート順
  - `price_asc`: 価格昇順
  - `price_desc`: 価格降順
  - `name_asc`: 名前昇順
  - `name_desc`: 名前降順
  - `updated_desc`: 更新日時降順（デフォルト）
- `limit`: 取得件数（1-100、デフォルト20）
- `offset`: 取得開始位置（デフォルト0）

#### リクエスト例
```bash
GET /v1/products?keyword=牛乳&category=飲料&limit=10
```

#### レスポンス例
```json
{
  "products": [
    {
      "id": "item-1",
      "name": "牛乳",
      "category": "飲料",
      "currentPrice": 240,
      "previousPrice": 250,
      "priceChange": -10,
      "priceChangePercent": -4.0,
      "shop": "スーパーA",
      "lastUpdated": "2025-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

### 2. 商品詳細取得 `GET /products/{productId}`

#### レスポンス例
```json
{
  "id": "item-1",
  "name": "牛乳",
  "category": "飲料",
  "currentPrice": 240,
  "previousPrice": 250,
  "priceChange": -10,
  "priceChangePercent": -4.0,
  "shop": "スーパーA",
  "description": "新鮮な牛乳です",
  "imageUrl": "https://example.com/images/milk.jpg",
  "lastUpdated": "2025-01-15T10:30:00Z",
  "priceHistory": [
    {
      "date": "2025-01-15",
      "price": 240,
      "shop": "スーパーA"
    }
  ],
  "aiSummary": {
    "lowestPrice": "直近30日で最安値は230円です",
    "trend": "来週火曜日に値下げの傾向があります",
    "recommendation": "今週末の購入がお得です"
  }
}
```

### 3. 価格履歴取得 `GET /products/{productId}/price-history`

#### クエリパラメータ
- `days`: 取得日数（7, 30, 60, 90, 180）デフォルト30

#### レスポンス例
```json
{
  "productId": "item-1",
  "history": [
    {
      "date": "2025-01-01",
      "price": 250,
      "shop": "スーパーA"
    },
    {
      "date": "2025-01-02",
      "price": 245,
      "shop": "スーパーA"
    }
  ]
}
```

### 4. お気に入り追加 `POST /favorites`

#### リクエスト例
```json
{
  "productId": "item-1"
}
```

#### レスポンス例
```json
{
  "message": "お気に入りに追加しました",
  "productId": "item-1"
}
```

### 5. 通知設定更新 `PUT /notifications/settings`

#### リクエスト例
```json
{
  "categories": ["飲料", "生鮮食品"],
  "frequency": "realtime",
  "priceChangeThreshold": 5,
  "webPushEnabled": true
}
```

#### レスポンス例
```json
{
  "message": "通知設定を更新しました",
  "settings": {
    "categories": ["飲料", "生鮮食品"],
    "frequency": "realtime",
    "priceChangeThreshold": 5,
    "lineConnected": false,
    "webPushEnabled": true
  }
}
```

### 6. お問い合わせ送信 `POST /contact`

#### リクエスト例
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com",
  "category": "service",
  "message": "サービスの使い方について質問があります。"
}
```

#### レスポンス例
```json
{
  "message": "お問い合わせを受け付けました",
  "contactId": "c1234567-89ab-cdef-0123-456789abcdef"
}
```

## 🎯 実装の優先順位

### Phase 1: 基本機能（MVP）
1. ✅ `GET /products` - 商品一覧取得
2. ✅ `GET /products/{productId}` - 商品詳細取得
3. ✅ `GET /products/{productId}/price-history` - 価格履歴取得
4. ✅ `GET /categories` - カテゴリ一覧取得

### Phase 2: ユーザー機能
5. ✅ `GET /favorites` - お気に入り一覧取得
6. ✅ `POST /favorites` - お気に入り追加
7. ✅ `DELETE /favorites/{productId}` - お気に入り削除
8. ✅ `GET /notifications/settings` - 通知設定取得
9. ✅ `PUT /notifications/settings` - 通知設定更新

### Phase 3: 外部連携
10. ✅ `POST /notifications/line/connect` - LINE連携
11. ✅ `POST /notifications/line/disconnect` - LINE連携解除

### Phase 4: その他
12. ✅ `POST /contact` - お問い合わせ送信

## 🛠️ Swagger UI での確認方法

### 方法1: Swagger Editor（オンライン）
1. https://editor.swagger.io/ にアクセス
2. 作成した `openapi.yaml` の内容をコピー&ペースト
3. 右側にAPI仕様書が表示されます

### 方法2: ローカルでSwagger UIを起動

```bash
# Docker を使用する場合
docker run -p 8080:8080 \
  -v $(pwd)/docs/openapi.yaml:/usr/share/nginx/html/openapi.yaml \
  -e SWAGGER_JSON=/usr/share/nginx/html/openapi.yaml \
  swaggerapi/swagger-ui

# ブラウザで http://localhost:8080 にアクセス
```

### 方法3: npm パッケージを使用

```bash
# インストール
npm install -g swagger-ui-express

# または、プロジェクトに追加
npm install swagger-ui-express --save
```

## 🔄 エラーレスポンス

すべてのエラーレスポンスは以下の形式で返されます：

```json
{
  "error": "ERROR_CODE",
  "message": "エラーメッセージ",
  "details": [
    {
      "field": "フィールド名",
      "message": "詳細メッセージ"
    }
  ]
}
```

### エラーコード一覧

| コード | HTTPステータス | 説明 |
|-------|--------------|------|
| BAD_REQUEST | 400 | リクエストパラメータが不正 |
| UNAUTHORIZED | 401 | 認証が必要 |
| FORBIDDEN | 403 | アクセスが拒否された |
| NOT_FOUND | 404 | リソースが見つからない |
| CONFLICT | 409 | リソースが既に存在する |
| VALIDATION_ERROR | 400 | 入力値が不正 |
| INTERNAL_SERVER_ERROR | 500 | サーバー内部エラー |

## 📁 ファイル配置

```
kaidoki-navi-api/
├── docs/
│   ├── openapi.yaml          # API設計書
│   ├── dynamodb-design.md    # DynamoDB設計書
│   └── api-design-doc.md     # このファイル
├── src/
│   ├── handlers/              # Lambda関数
│   ├── models/                # データモデル
│   ├── services/              # ビジネスロジック
│   └── utils/                 # ユーティリティ
└── tests/
```

## 📝 開発ワークフロー

### 1. API仕様の確認
```bash
# Swagger Editorで確認
open https://editor.swagger.io/
```

### 2. モックサーバーの起動
```bash
# Prismを使用したモックサーバー
npm install -g @stoplight/prism-cli
prism mock docs/openapi.yaml
```

### 3. ローカル開発
```bash
# Dockerでローカル環境を起動
docker-compose up -d

# APIをテスト
curl http://localhost:3000/products
```

### 4. テストの実行
```bash
# ユニットテスト
pytest tests/unit

# 統合テスト
pytest tests/integration
```

## 🔐 セキュリティ

### JWT認証
- アルゴリズム: HS256
- 有効期間: 24時間
- シークレットキー: 環境変数で管理

### CORS設定
- 許可するオリジン: フロントエンドのドメイン
- 許可するメソッド: GET, POST, PUT, DELETE, OPTIONS
- 許可するヘッダー: Content-Type, Authorization

### レート制限
- API Gateway のスロットリング機能を使用
- バースト: 5000リクエスト/秒
- 定常: 2000リクエスト/秒

## 📊 モニタリング

### CloudWatch メトリクス
- リクエスト数
- レイテンシー
- エラー率
- スロットリング数

### アラート設定
- エラー率が5%を超えた場合
- レイテンシーが3秒を超えた場合
- スロットリングが発生した場合

## 🚀 次のステップ

この設計書を確認いただき、問題なければ以下を進めます：

1. **DynamoDBのテーブル設計** ✅ 完了
2. **Lambda関数の実装** ✅ 完了
3. **API Gatewayの設定** ✅ 完了（SAMテンプレート）
4. **ローカルでのテスト** 🔄 進行中
5. **AWSへのデプロイ** ⏳ 次のステップ