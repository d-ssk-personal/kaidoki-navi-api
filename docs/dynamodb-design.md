# DynamoDB テーブル設計

## テーブル一覧

### 1. Products テーブル
商品情報を格納

**テーブル名**: `kaidoki-navi-products`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| productId | String | PK | 商品ID (例: item-1) |
| name | String | - | 商品名 |
| category | String | GSI-PK | カテゴリ |
| currentPrice | Number | - | 現在価格 |
| previousPrice | Number | - | 前回価格 |
| shop | String | - | 販売店 |
| description | String | - | 商品説明 |
| imageUrl | String | - | 画像URL |
| createdAt | String | - | 作成日時 |
| updatedAt | String | GSI-SK | 更新日時 |

**GSI**: category-updatedAt-index
- パーティションキー: category
- ソートキー: updatedAt

**用途**: カテゴリでフィルタリングし、更新日時でソート

---

### 2. PriceHistory テーブル
価格履歴を格納

**テーブル名**: `kaidoki-navi-price-history`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| productId | String | PK | 商品ID |
| date | String | SK | 日付 (YYYY-MM-DD) |
| price | Number | - | 価格 |
| shop | String | - | 販売店 |
| timestamp | String | - | 記録日時 |

**用途**: 特定商品の価格履歴を日付順に取得

---

### 3. Users テーブル
ユーザー情報を格納

**テーブル名**: `kaidoki-navi-users`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| userId | String | PK | ユーザーID (UUID) |
| email | String | GSI-PK | メールアドレス |
| lineUserId | String | - | LINE User ID |
| createdAt | String | - | 作成日時 |
| updatedAt | String | - | 更新日時 |

**GSI**: email-index
- パーティションキー: email

**用途**: メールアドレスでユーザーを検索

---

### 4. Favorites テーブル
お気に入り情報を格納

**テーブル名**: `kaidoki-navi-favorites`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| userId | String | PK | ユーザーID |
| productId | String | SK | 商品ID |
| createdAt | String | - | 追加日時 |

**用途**: ユーザーのお気に入り商品を取得

---

### 5. NotificationSettings テーブル
通知設定を格納

**テーブル名**: `kaidoki-navi-notification-settings`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| userId | String | PK | ユーザーID |
| categories | List | - | 通知対象カテゴリ |
| frequency | String | - | 通知頻度 |
| priceChangeThreshold | Number | - | 価格変動閾値(%) |
| lineConnected | Boolean | - | LINE連携状態 |
| webPushEnabled | Boolean | - | WebPush有効/無効 |
| updatedAt | String | - | 更新日時 |

**用途**: ユーザーごとの通知設定を管理

---

### 6. Categories テーブル
カテゴリマスタ

**テーブル名**: `kaidoki-navi-categories`

| 属性名 | 型 | キー | 説明 |
|--------|-----|------|------|
| categoryId | String | PK | カテゴリID |
| name | String | - | カテゴリ名 |
| displayOrder | Number | - | 表示順 |
| productCount | Number | - | 商品数 |
| createdAt | String | - | 作成日時 |

**用途**: カテゴリ一覧の取得

---

## インデックス戦略

### Products テーブル
- **プライマリキー**: productId
- **GSI**: category-updatedAt-index
  - 用途: カテゴリでフィルタリングし、更新日時でソート
  - クエリ例: `category = "飲料" AND updatedAt > "2025-01-01"`

### PriceHistory テーブル
- **プライマリキー**: productId (PK) + date (SK)
  - 用途: 特定商品の価格履歴を日付順に取得
  - クエリ例: `productId = "item-1" AND date >= "2025-01-01"`

### Users テーブル
- **プライマリキー**: userId
- **GSI**: email-index
  - 用途: メールアドレスでユーザーを検索
  - クエリ例: `email = "user@example.com"`

### Favorites テーブル
- **プライマリキー**: userId (PK) + productId (SK)
  - 用途: ユーザーのお気に入り商品を取得
  - クエリ例: `userId = "user-123"`

---

## アクセスパターン

### 商品関連
1. **全商品を取得**: Scan on Products
2. **カテゴリで絞り込み**: Query on category-updatedAt-index
3. **商品詳細を取得**: GetItem on Products (productId)
4. **価格履歴を取得**: Query on PriceHistory (productId, date range)

### お気に入り関連
1. **ユーザーのお気に入り一覧**: Query on Favorites (userId)
2. **お気に入りに追加**: PutItem on Favorites
3. **お気に入りから削除**: DeleteItem on Favorites

### 通知設定関連
1. **通知設定を取得**: GetItem on NotificationSettings (userId)
2. **通知設定を更新**: PutItem on NotificationSettings

---

## 容量見積もり

### 想定データ量
- 商品数: 1,000件
- ユーザー数: 10,000人
- 1商品あたりの価格履歴: 180日分

### ストレージ見積もり

| テーブル | 1項目のサイズ | 項目数 | 合計 |
|---------|--------------|--------|------|
| Products | ~1KB | 1,000 | 1MB |
| PriceHistory | ~0.1KB | 180,000 | 18MB |
| Users | ~0.5KB | 10,000 | 5MB |
| Favorites | ~0.1KB | 100,000 | 10MB |
| NotificationSettings | ~0.5KB | 10,000 | 5MB |
| Categories | ~0.2KB | 10 | 0.002MB |

**合計**: 約40MB（無料枠内で十分対応可能）

### スループット見積もり

**開発環境**:
- Products: 5 RCU / 5 WCU
- Users: 5 RCU / 5 WCU
- その他: PAY_PER_REQUEST

**本番環境（月間1万ユーザー想定）**:
- Products: 10 RCU / 5 WCU
- PriceHistory: PAY_PER_REQUEST
- Users: 5 RCU / 5 WCU
- Favorites: PAY_PER_REQUEST
- NotificationSettings: PAY_PER_REQUEST
- Categories: 1 RCU / 1 WCU

---

## セキュリティ

### アクセス制御
- Lambda関数に最小権限のIAMロールを付与
- テーブルごとに必要な操作のみ許可
  - Products: Read のみ
  - PriceHistory: Read のみ
  - Users: Read/Write
  - Favorites: Read/Write
  - NotificationSettings: Read/Write
  - Categories: Read のみ

### データ保護
- 転送中の暗号化: HTTPS
- 保管時の暗号化: AWS KMS（オプション）
- バックアップ: Point-in-Time Recovery (PITR) 有効化（本番環境）

---

## パフォーマンス最適化

### キャッシング
- API Gatewayのキャッシング機能を活用
- 商品一覧、カテゴリ一覧などの読み取り頻度が高いエンドポイントでキャッシュ

### バッチ処理
- 価格データの一括更新にはBatchWriteItemを使用
- 1回のバッチで最大25項目まで処理可能

### パーティション分散
- productIdにUUIDを使用してホットパーティションを回避
- 日時ベースのソートキーで書き込みを分散

---

## モニタリング

### CloudWatch メトリクス
- ConsumedReadCapacityUnits
- ConsumedWriteCapacityUnits
- UserErrors (400系エラー)
- SystemErrors (500系エラー)
- Throttles

### アラート設定
- スロットリング発生時
- エラー率が閾値を超えた時
- RCU/WCUの使用率が80%を超えた時

---

## バックアップとリカバリ

### バックアップ戦略
- **開発環境**: オンデマンドバックアップ（手動）
- **本番環境**: 
  - Point-in-Time Recovery (PITR) 有効化
  - 日次の自動バックアップ
  - 35日間の保持期間

### リカバリ手順
1. PITRで特定時点に復元
2. 新しいテーブルが作成される
3. アプリケーションを新しいテーブルに切り替え
4. 旧テーブルを削除

---

## コスト最適化

### 推奨設定

**開発環境**:
- ProvisionedモードでRCU/WCUを最小限に設定
- オンデマンドバックアップのみ

**本番環境**:
- 読み取り頻度の高いテーブル: Provisioned（予約容量で20-30%割引）
- 書き込み頻度の高いテーブル: PAY_PER_REQUEST
- PITR有効化
- 自動スケーリング設定

### 月間コスト見積もり（東京リージョン）

**開発環境**: $1-3/月
**本番環境（1万ユーザー）**: $10-20/月