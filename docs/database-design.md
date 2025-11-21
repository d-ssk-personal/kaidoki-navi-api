# Chirashi Kitchen データベース設計書

## 概要

このドキュメントは、Chirashi KitchenのDynamoDB設計を定義します。

### 技術スタック
- **データベース**: AWS DynamoDB
- **バックエンド**: AWS Lambda (Python 3.12)
- **認証**: JWT

### 設計方針
- **マルチテーブル設計**: 各エンティティの独立性が高いため、マルチテーブル設計を採用
- **アクセスパターン最適化**: 主要なクエリパターンに基づいてGSIを設計
- **非正規化**: パフォーマンス向上のため、必要に応じてデータを重複させる

---

## DynamoDBの基本概念とGSIの必要性

### DynamoDBの検索制限

DynamoDBは高速なNoSQLデータベースですが、RDB（MySQL、PostgreSQLなど）と異なり、**検索方法に制限**があります。

#### プライマリキー（PK）だけでは検索できないケース

DynamoDBのテーブルは、以下の方法でしか検索できません：

1. **パーティションキー（PK）による完全一致検索**
   - 例: `userId = "user_001"` でユーザー情報を取得

2. **パーティションキー + ソートキー（SK）による範囲検索**
   - 例: `productId = "prod_001"` かつ `timestamp` が「2024-01-01～2024-01-31」の価格履歴を取得

#### 問題点: 別の属性で検索したい場合

例えば、`users` テーブルのPKが `userId` の場合：
- ✅ `userId` で検索できる
- ❌ `email` で検索できない（ログイン時に必要！）

RDBなら `SELECT * FROM users WHERE email = 'user@example.com'` で簡単に検索できますが、**DynamoDBではPK以外の属性で検索できません**。

### GSI（Global Secondary Index）とは？

GSIは、**別の属性を使って検索できるようにする仕組み**です。

#### GSIの仕組み

GSIを作成すると、元のテーブルとは別に「検索用のテーブル」が自動的に作成されます。

```
元のテーブル（users）:
PK: userId
--------------------
userId | email           | name
001    | user@example.com | 山田太郎
002    | test@example.com | 佐藤花子

GSI-1 (EmailIndex):
PK: email
--------------------
email           | userId | name
user@example.com | 001    | 山田太郎
test@example.com | 002    | 佐藤花子
```

これにより、`email` で検索できるようになります。

#### GSIのコスト

- **読み取り・書き込み容量**: GSI分の追加コストが発生
- **ストレージ**: GSI分のデータが複製されるため、ストレージコストも増加

そのため、**本当に必要なGSIだけを作成する**ことが重要です。

---

## テーブル一覧

1. [Users](#1-users---ユーザー)
2. [Admins](#2-admins---管理者)
3. [Companies](#3-companies---企業)
4. [Stores](#4-stores---店舗)
5. [Flyers](#5-flyers---チラシ)
6. [Articles](#6-articles---コラム)
7. [FavoriteStores](#7-favoritstores---お気に入り店舗)
8. [Recipes](#8-recipes---aiレシピキャッシュ)
9. [SharedRecipes](#9-sharedrecipes---共有レシピ)

---

## 1. Users - ユーザー

### テーブル名
`users`

### 説明
一般ユーザーの情報を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| userId | String | PK (Partition Key) | ユーザーID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: EmailIndex
- **Purpose**: メールアドレスでユーザーを検索（ログイン時）
- **PK**: email (String)
- **Projection**: ALL

**なぜ必要？**
ユーザーログイン時、メールアドレスとパスワードで認証を行います。しかし、テーブルのPKは `userId` なので、メールアドレスで検索できません。

**GSIなしの場合の問題:**
```python
# ❌ メールアドレスで検索できない（Scanが必要 = 非効率）
# テーブル全体をスキャン → 遅い、コスト高
response = table.scan(
    FilterExpression='email = :email',
    ExpressionAttributeValues={':email': 'user@example.com'}
)
```

**GSIありの場合:**
```python
# ✅ GSI-1を使って高速検索
response = table.query(
    IndexName='EmailIndex',
    KeyConditionExpression='email = :email',
    ExpressionAttributeValues={':email': 'user@example.com'}
)
```

**結論**: ログイン機能を実装するために必須のGSIです。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| userId | String | ○ | ユーザーID（UUID） | `user_a1b2c3d4` |
| email | String | ○ | メールアドレス（一意） | `user@example.com` |
| name | String | ○ | ユーザー名 | `山田太郎` |
| passwordHash | String | ○ | パスワードハッシュ（bcrypt） | `$2b$12$...` |
| favoriteStoreIds | List<String> |  | お気に入り店舗IDリスト | `["store_001", "store_002"]` |
| notificationFrequency | String |  | 通知頻度 | `realtime` / `morning` / `evening` |
| createdAt | String | ○ | 作成日時（ISO 8601） | `2024-01-01T00:00:00Z` |
| updatedAt | String | ○ | 更新日時（ISO 8601） | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. ユーザーIDでユーザー情報取得（PK）
2. メールアドレスでユーザー検索（GSI-1）
3. ユーザー情報更新（PK）

---

## 2. Admins - 管理者

### テーブル名
`admins`

### 説明
管理者アカウント情報を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| adminId | String | PK (Partition Key) | 管理者ID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: UsernameIndex
- **Purpose**: ユーザー名でログイン
- **PK**: username (String)
- **Projection**: ALL

**なぜ必要？**
管理者ログイン時、ユーザー名（ログインID）とパスワードで認証します。テーブルのPKは `adminId` なので、ユーザー名で検索するためにGSIが必要です。

**使用例:**
```python
# 管理者ログイン処理
response = table.query(
    IndexName='UsernameIndex',
    KeyConditionExpression='username = :username',
    ExpressionAttributeValues={':username': 'admin001'}
)
```

#### GSI-2: CompanyIndex
- **Purpose**: 企業IDで管理者一覧取得
- **PK**: companyId (String)
- **SK**: role (String)
- **Projection**: ALL

**なぜ必要？**
管理画面の「アカウント管理」機能で、以下のような検索が必要です：
1. 企業IDで所属する管理者一覧を取得
2. 役割（system_admin、company_admin、store_user）で絞り込み

**GSIなしの場合の問題:**
```python
# ❌ 企業IDで管理者を検索できない
# Scanでテーブル全体を検索 → 遅い
```

**GSIありの場合:**
```python
# ✅ 企業IDで管理者一覧を取得
response = table.query(
    IndexName='CompanyIndex',
    KeyConditionExpression='companyId = :companyId',
    ExpressionAttributeValues={':companyId': 'company_001'}
)

# ✅ 企業ID + 役割で絞り込み
response = table.query(
    IndexName='CompanyIndex',
    KeyConditionExpression='companyId = :companyId AND role = :role',
    ExpressionAttributeValues={
        ':companyId': 'company_001',
        ':role': 'company_admin'
    }
)
```

**結論**: 管理画面のアカウント管理機能で、企業ごとの管理者を効率的に取得するために必要です。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| adminId | String | ○ | 管理者ID（UUID） | `admin_001` |
| username | String | ○ | ユーザー名（ログインID） | `admin001` |
| name | String | ○ | 表示名 | `管理者太郎` |
| email | String | ○ | メールアドレス | `admin@example.com` |
| passwordHash | String | ○ | パスワードハッシュ | `$2b$12$...` |
| role | String | ○ | 役割 | `system_admin` / `company_admin` / `store_user` |
| companyId | String |  | 所属企業ID（company_admin, store_userの場合） | `company_001` |
| companyName | String |  | 所属企業名（非正規化） | `スーパーAグループ` |
| storeId | String |  | 所属店舗ID（store_userの場合） | `store_001` |
| storeName | String |  | 所属店舗名（非正規化） | `スーパーA 新宿店` |
| lastLoginAt | String |  | 最終ログイン日時 | `2024-01-15T10:00:00Z` |
| createdAt | String | ○ | 作成日時 | `2024-01-01T00:00:00Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. 管理者IDで管理者情報取得（PK）
2. ユーザー名でログイン（GSI-1）
3. 企業IDで管理者一覧取得（GSI-2）
4. 役割で絞り込み（GSI-2のSK）

---

## 3. Companies - 企業

### テーブル名
`companies`

### 説明
企業情報を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| companyId | String | PK (Partition Key) | 企業ID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: ContractStatusIndex
- **Purpose**: 契約状態で企業を検索・フィルタリング
- **PK**: contractStatus (String)
- **SK**: contractPlan (String)
- **Projection**: ALL

**なぜ必要？**
管理画面の「企業管理」機能で、契約状態やプランでフィルタリングする必要があります。

**使用例:**
```python
# ✅ 契約中（active）の企業一覧を取得
response = table.query(
    IndexName='ContractStatusIndex',
    KeyConditionExpression='contractStatus = :status',
    ExpressionAttributeValues={':status': 'active'}
)

# ✅ 契約中 + プレミアムプランの企業を取得
response = table.query(
    IndexName='ContractStatusIndex',
    KeyConditionExpression='contractStatus = :status AND contractPlan = :plan',
    ExpressionAttributeValues={
        ':status': 'active',
        ':plan': 'premium'
    }
)

# ✅ 契約期限切れ（expired）の企業を取得（督促対象）
response = table.query(
    IndexName='ContractStatusIndex',
    KeyConditionExpression='contractStatus = :status',
    ExpressionAttributeValues={':status': 'expired'}
)
```

**結論**: 契約管理業務（契約状況の確認、プラン別の統計、期限切れ企業の抽出など）に必要です。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| companyId | String | ○ | 企業ID（UUID） | `company_001` |
| name | String | ○ | 企業名 | `スーパーAグループ` |
| contactPerson | String | ○ | 担当者氏名 | `山田太郎` |
| email | String | ○ | 連絡先メールアドレス | `contact@superA.com` |
| phone | String | ○ | 電話番号 | `03-1234-5678` |
| address | String | ○ | 住所 | `東京都千代田区1-1-1` |
| contractStatus | String | ○ | 契約状態 | `active` / `expired` / `suspended` |
| contractPlan | String | ○ | 契約プラン | `basic` / `standard` / `premium` |
| contractStartDate | String | ○ | 契約開始日 | `2023-01-01` |
| contractEndDate | String | ○ | 契約終了日 | `2024-12-31` |
| storeCount | Number |  | 登録店舗数（計算値） | `15` |
| createdAt | String | ○ | 作成日時 | `2023-01-01T00:00:00Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. 企業IDで企業情報取得（PK）
2. 契約状態で企業一覧取得（GSI-1）
3. 契約プランで絞り込み（GSI-1のSK）

---

## 4. Stores - 店舗

### テーブル名
`stores`

### 説明
店舗情報を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| storeId | String | PK (Partition Key) | 店舗ID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: CompanyIndex
- **Purpose**: 企業IDで店舗一覧取得
- **PK**: companyId (String)
- **SK**: storeId (String)
- **Projection**: ALL

**なぜ必要？**
管理画面の「店舗管理」機能で、企業ごとの店舗一覧を表示する必要があります。また、権限制御にも使用されます。

**使用例:**
```python
# ✅ 企業「company_001」の店舗一覧を取得
response = table.query(
    IndexName='CompanyIndex',
    KeyConditionExpression='companyId = :companyId',
    ExpressionAttributeValues={':companyId': 'company_001'}
)
```

**権限制御での使用:**
- **system_admin**: 全店舗を表示（GSI不要）
- **company_admin**: 自社の店舗のみ表示（GSI-1で検索）
- **store_user**: 自店舗のみ表示（PKで検索）

**結論**: 企業ごとの店舗管理と、権限に応じたデータフィルタリングに必要です。

#### GSI-2: RegionIndex
- **Purpose**: 地域で店舗検索
- **PK**: prefecture (String)
- **SK**: region (String)
- **Projection**: ALL

**なぜ必要？**
ユーザー側のアプリで「地域から店舗を検索」する機能があります。

**使用例:**
```python
# ✅ 東京都の店舗を検索
response = table.query(
    IndexName='RegionIndex',
    KeyConditionExpression='prefecture = :prefecture',
    ExpressionAttributeValues={':prefecture': '東京都'}
)

# ✅ 関東地方の店舗を検索（FilterExpressionと併用）
response = table.query(
    IndexName='RegionIndex',
    KeyConditionExpression='prefecture = :prefecture',
    FilterExpression='region = :region',
    ExpressionAttributeValues={
        ':prefecture': '東京都',
        ':region': '関東'
    }
)
```

**結論**: ユーザーが地域から店舗を探す機能を実装するために必要です。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| storeId | String | ○ | 店舗ID（UUID） | `store_001` |
| companyId | String | ○ | 所属企業ID | `company_001` |
| companyName | String | ○ | 所属企業名（非正規化） | `スーパーAグループ` |
| name | String | ○ | 店舗名 | `スーパーA 新宿店` |
| logo | String |  | ロゴURL | `https://example.com/logos/store_001.png` |
| address | String | ○ | 住所 | `東京都新宿区新宿1-1-1` |
| prefecture | String | ○ | 都道府県 | `東京都` |
| region | String | ○ | 地方 | `関東` |
| phone | String | ○ | 電話番号 | `03-1234-5678` |
| openingHours | String |  | 営業時間 | `9:00-21:00` |
| salePeriod | String |  | セール期間 | `毎週金曜日はポイント5倍` |
| createdAt | String | ○ | 作成日時 | `2023-01-01T00:00:00Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. 店舗IDで店舗情報取得（PK）
2. 企業IDで店舗一覧取得（GSI-1）
3. 都道府県で店舗検索（GSI-2）
4. 地方で絞り込み（GSI-2のSK）

---

## 5. Flyers - チラシ

### テーブル名
`flyers`

### 説明
チラシ情報を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| flyerId | String | PK (Partition Key) | チラシID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: StoreIndex
- **Purpose**: 店舗IDでチラシ一覧取得
- **PK**: storeId (String)
- **SK**: validFrom (String)
- **Projection**: ALL

**なぜ必要？**
ユーザー側のアプリで「店舗ごとのチラシ一覧」を表示する機能があります。また、掲載開始日で新しい順に並べる必要があります。

**使用例:**
```python
# ✅ 店舗「store_001」のチラシを新しい順に取得
response = table.query(
    IndexName='StoreIndex',
    KeyConditionExpression='storeId = :storeId',
    ExpressionAttributeValues={':storeId': 'store_001'},
    ScanIndexForward=False  # 降順ソート（新しい順）
)

# ✅ 特定期間のチラシを取得（範囲検索）
response = table.query(
    IndexName='StoreIndex',
    KeyConditionExpression='storeId = :storeId AND validFrom BETWEEN :start AND :end',
    ExpressionAttributeValues={
        ':storeId': 'store_001',
        ':start': '2024-01-01',
        ':end': '2024-01-31'
    }
)
```

**SK（validFrom）の役割:**
- 新しいチラシを上位表示（降順ソート）
- 期間指定でチラシを検索（範囲クエリ）

**結論**: 店舗ごとのチラシ一覧表示と、日付による並べ替え・絞り込みに必要です。

#### GSI-2: RegionIndex
- **Purpose**: 地域でチラシ検索
- **PK**: prefecture (String)
- **SK**: validFrom (String)
- **Projection**: ALL

**なぜ必要？**
ユーザー側のアプリで「地域からチラシを検索」する機能があります。「東京都のチラシ一覧」を新しい順に表示するなど。

**使用例:**
```python
# ✅ 東京都のチラシを新しい順に取得
response = table.query(
    IndexName='RegionIndex',
    KeyConditionExpression='prefecture = :prefecture',
    ExpressionAttributeValues={':prefecture': '東京都'},
    ScanIndexForward=False  # 降順ソート
)
```

**結論**: 地域検索機能を実装するために必要です。

#### GSI-3: CompanyIndex
- **Purpose**: 企業IDでチラシ一覧取得（管理画面用）
- **PK**: companyId (String)
- **SK**: validFrom (String)
- **Projection**: ALL

**なぜ必要？**
管理画面で、企業ごとのチラシ管理を行います。権限制御にも使用されます。

**使用例:**
```python
# ✅ 企業「company_001」のチラシ一覧を取得
response = table.query(
    IndexName='CompanyIndex',
    KeyConditionExpression='companyId = :companyId',
    ExpressionAttributeValues={':companyId': 'company_001'},
    ScanIndexForward=False  # 新しい順
)
```

**権限制御での使用:**
- **system_admin**: 全チラシを表示（GSI不要）
- **company_admin**: 自社のチラシのみ表示（GSI-3で検索）
- **store_user**: 自店舗のチラシのみ表示（GSI-1で検索）

**結論**: 企業ごとのチラシ管理と、権限に応じたデータフィルタリングに必要です。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| flyerId | String | ○ | チラシID（UUID） | `flyer_001` |
| storeId | String | ○ | 店舗ID | `store_001` |
| storeName | String | ○ | 店舗名（非正規化） | `スーパーA 新宿店` |
| storeLogo | String |  | 店舗ロゴURL（非正規化） | `https://example.com/logos/store_001.png` |
| companyId | String | ○ | 企業ID（非正規化） | `company_001` |
| companyName | String | ○ | 企業名（非正規化） | `スーパーAグループ` |
| imageUrl | String | ○ | チラシ画像URL（S3） | `https://s3.../flyers/flyer_001.jpg` |
| validFrom | String | ○ | 掲載開始日 | `2024-01-15` |
| validUntil | String | ○ | 掲載終了日 | `2024-01-21` |
| address | String | ○ | 店舗住所（非正規化） | `東京都新宿区新宿1-1-1` |
| prefecture | String | ○ | 都道府県（非正規化） | `東京都` |
| region | String | ○ | 地方（非正規化） | `関東` |
| phone | String |  | 店舗電話番号（非正規化） | `03-1234-5678` |
| openingHours | String |  | 営業時間（非正規化） | `9:00-21:00` |
| description | String |  | チラシ説明 | `新春大セール開催中！` |
| createdBy | String | ○ | 作成者（管理者ID） | `admin_001` |
| createdAt | String | ○ | 作成日時 | `2024-01-15T00:00:00Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. チラシIDでチラシ詳細取得（PK）
2. 店舗IDでチラシ一覧取得（GSI-1）
3. 都道府県でチラシ検索（GSI-2）
4. 企業IDでチラシ一覧取得（GSI-3）

---

## 6. Articles - コラム

### テーブル名
`articles`

### 説明
コラム記事を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| articleId | Number | PK (Partition Key) | コラムID（自動採番） |

### GSI（Global Secondary Index）

#### GSI-1: StatusIndex
- **Purpose**: ステータスで記事を検索・絞り込み
- **PK**: status (String)
- **SK**: publishedAt (String)
- **Projection**: ALL

**なぜ必要？**
ユーザー側では「公開済み（published）」の記事のみ表示し、管理画面では「下書き（draft）」も表示する必要があります。

**使用例:**
```python
# ✅ 公開済み記事を新しい順に取得（ユーザー側）
response = table.query(
    IndexName='StatusIndex',
    KeyConditionExpression='status = :status',
    ExpressionAttributeValues={':status': 'published'},
    ScanIndexForward=False  # 降順ソート（新しい順）
)

# ✅ 下書き記事を取得（管理画面）
response = table.query(
    IndexName='StatusIndex',
    KeyConditionExpression='status = :status',
    ExpressionAttributeValues={':status': 'draft'}
)
```

**SK（publishedAt）の役割:**
- 公開日時で新しい順に並べ替え
- **Sparse Index（疎なインデックス）**: `publishedAt` が存在する記事のみGSIに含まれる（下書きには `publishedAt` がないため）

**結論**: ステータス別の記事一覧表示と、公開日時による並べ替えに必要です。

#### GSI-2: CategoryIndex
- **Purpose**: カテゴリで記事を検索
- **PK**: category (String)
- **SK**: publishedAt (String)
- **Projection**: ALL

**なぜ必要？**
ユーザー側のアプリで「カテゴリ別の記事一覧」を表示する機能があります（例: 「値上げ情報」カテゴリの記事のみ表示）。

**使用例:**
```python
# ✅ 「値上げ情報」カテゴリの記事を新しい順に取得
response = table.query(
    IndexName='CategoryIndex',
    KeyConditionExpression='category = :category',
    ExpressionAttributeValues={':category': '値上げ情報'},
    ScanIndexForward=False  # 降順ソート
)
```

**結論**: カテゴリ別の記事検索機能を実装するために必要です。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| articleId | Number | ○ | コラムID（自動採番） | `1` |
| title | String | ○ | タイトル | `2024年の食品値上げ情報まとめ` |
| content | String | ○ | 本文 | `2024年も多くの食品が...` |
| images | List<String> |  | 画像URLリスト | `["https://...jpg"]` |
| publishedAt | String |  | 公開日時 | `2024-01-15T10:00:00Z` |
| category | String | ○ | カテゴリ | `値上げ情報` / `特売情報` / `節約術` / `レシピ` / `その他` |
| tags | List<String> |  | タグリスト | `["食品", "値上げ", "2024年"]` |
| status | String | ○ | ステータス | `published` / `draft` |
| createdBy | String | ○ | 作成者（管理者ID） | `admin_001` |
| updatedBy | String | ○ | 更新者（管理者ID） | `admin_001` |
| createdAt | String | ○ | 作成日時 | `2024-01-10T00:00:00Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-15T00:00:00Z` |

### アクセスパターン
1. コラムIDで詳細取得（PK）
2. ステータスで記事一覧取得（GSI-1）
3. カテゴリで記事検索（GSI-2）
4. 公開日時の降順でソート（GSI-1, GSI-2のSK）

---

## 7. FavoriteStores - お気に入り店舗

### テーブル名
`favorite-stores`

### 説明
ユーザーのお気に入り店舗を管理

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| userId | String | PK (Partition Key) | ユーザーID |
| storeId | String | SK (Sort Key) | 店舗ID |

### GSI（Global Secondary Index）
なし（PKとSKで効率的にクエリ可能）

**なぜGSIが不要？**

このテーブルは、**ユーザーごとのお気に入り店舗を管理する**ためのものです。必要なクエリは「ユーザーIDでお気に入り一覧を取得」だけなので、GSIは不要です。

**アクセスパターン:**
```python
# ✅ ユーザー「user_001」のお気に入り店舗一覧を取得
response = table.query(
    KeyConditionExpression='userId = :userId',
    ExpressionAttributeValues={':userId': 'user_001'}
)

# ✅ ユーザー「user_001」が店舗「store_001」をお気に入りに追加しているか確認
response = table.get_item(
    Key={
        'userId': 'user_001',
        'storeId': 'store_001'
    }
)

# ✅ お気に入りに追加
table.put_item(
    Item={
        'userId': 'user_001',
        'storeId': 'store_001',
        'storeName': 'スーパーA 新宿店',
        ...
    }
)

# ✅ お気に入りから削除
table.delete_item(
    Key={
        'userId': 'user_001',
        'storeId': 'store_001'
    }
)
```

**重要な設計ポイント:**
- **PK**: ユーザーIDで、同じユーザーのお気に入りをまとめて取得
- **SK**: 店舗IDで、特定のお気に入り関係を一意に識別

**非正規化のメリット:**
店舗名やロゴなどの情報を非正規化して保存することで、Storesテーブルへの追加クエリが不要になり、パフォーマンスが向上します。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| userId | String | ○ | ユーザーID | `user_a1b2c3d4` |
| storeId | String | ○ | 店舗ID | `store_001` |
| storeName | String | ○ | 店舗名（非正規化） | `スーパーA 新宿店` |
| storeLogo | String |  | 店舗ロゴURL（非正規化） | `https://example.com/logos/store_001.png` |
| address | String | ○ | 住所（非正規化） | `東京都新宿区新宿1-1-1` |
| phone | String |  | 電話番号（非正規化） | `03-1234-5678` |
| notificationEnabled | Boolean | ○ | 新着チラシ通知有効フラグ | `true` |
| addedAt | String | ○ | 追加日時 | `2024-01-01T00:00:00Z` |

### アクセスパターン
1. ユーザーIDでお気に入り店舗一覧取得（PK）
2. ユーザーIDと店舗IDで特定のお気に入り取得（PK + SK）
3. お気に入り店舗の追加・削除・更新（PK + SK）

---

## 8. Recipes - AIレシピ（キャッシュ）

### テーブル名
`recipes`

### 説明
AIが生成したレシピを一時的にキャッシュ（共有されていないレシピは30日後に自動削除）

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| flyerId | String | PK (Partition Key) | チラシID |

### GSI（Global Secondary Index）
なし（チラシIDで直接アクセス）

**なぜGSIが不要？**

このテーブルは、**チラシIDに対して1:1でレシピを保存する**ためのものです。必要なクエリは「チラシIDでレシピを取得」だけなので、GSIは不要です。

**アクセスパターン:**
```python
# ✅ チラシ「flyer_001」のレシピを取得（キャッシュチェック）
response = table.get_item(
    Key={'flyerId': 'flyer_001'}
)

if response.get('Item'):
    # キャッシュあり → そのまま返す
    return response['Item']['recipeText']
else:
    # キャッシュなし → AIで生成して保存
    recipe = generate_recipe_with_ai(flyer_id)
    table.put_item(
        Item={
            'flyerId': 'flyer_001',
            'recipeText': recipe,
            'generatedAt': '2024-01-15T12:34:56Z',
            'ttl': calculate_ttl(30)  # 30日後
        }
    )
    return recipe
```

**重要な設計ポイント:**
- **PK**: チラシID（flyerId）のみで、1チラシに1レシピの関係
- **TTL**: 30日後に自動削除されるため、古いレシピが溜まらない
- **キャッシュ機能**: 同じチラシに対して何度もAI生成しないため、コスト削減とレスポンス速度向上

**TTL（Time To Live）とは？**
DynamoDBの機能で、指定した時刻（Unix timestamp）になると、アイテムが自動的に削除されます。
```python
import time

# 30日後のUnix timestampを計算
ttl = int(time.time()) + (30 * 24 * 60 * 60)
```

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| flyerId | String | ○ | チラシID | `flyer_001` |
| recipeText | String | ○ | レシピ本文（Markdown） | `# おすすめレシピ\n\n## 豚バラ肉と...` |
| ingredients | List<Map> |  | 食材リスト | `[{"name": "豚バラ肉", "price": 298}]` |
| generatedAt | String | ○ | 生成日時 | `2024-01-15T12:34:56Z` |
| ttl | Number |  | TTL（30日後に自動削除） | `1706097600` (Unix timestamp) |

### アクセスパターン
1. チラシIDでレシピ取得（PK）
2. レシピキャッシュ（再生成を避けるため）

### 備考
- TTL（Time To Live）を設定し、30日後に自動削除
- 同じチラシに対して再度レシピ生成を依頼された場合、キャッシュから返却
- **このテーブルは一時キャッシュ専用**。SNS共有されたレシピは `SharedRecipes` テーブルに永続化される

---

## 9. SharedRecipes - 共有レシピ

### テーブル名
`shared-recipes`

### 説明
SNS共有されたレシピを永続的に保存（TTLなし）

### キー設計

| 属性名 | 型 | キー種別 | 説明 |
|--------|-----|----------|------|
| sharedRecipeId | String | PK (Partition Key) | 共有レシピID（UUID） |

### GSI（Global Secondary Index）

#### GSI-1: FlyerIndex
- **Purpose**: 同じチラシから生成された共有レシピを検索
- **PK**: flyerId (String)
- **SK**: sharedAt (String)
- **Projection**: ALL

**なぜ必要？**
同じチラシから複数のレシピが生成・共有される可能性があります。チラシページで「このチラシから共有されたレシピ一覧」を表示する際に使用します。

**使用例:**
```python
# ✅ チラシ「flyer_001」から共有されたレシピ一覧を取得
response = table.query(
    IndexName='FlyerIndex',
    KeyConditionExpression='flyerId = :flyerId',
    ExpressionAttributeValues={':flyerId': 'flyer_001'},
    ScanIndexForward=False  # 新しい順
)
```

**結論**: チラシページで「このチラシから生成された人気レシピ」を表示する機能に使用します。

### 属性

| 属性名 | 型 | 必須 | 説明 | 例 |
|--------|-----|------|------|-----|
| sharedRecipeId | String | ○ | 共有レシピID（UUID） | `shared_recipe_abc123` |
| flyerId | String | ○ | 元となったチラシID | `flyer_001` |
| recipeText | String | ○ | レシピ本文（Markdown） | `# おすすめレシピ\n\n## 豚バラ肉と...` |
| ingredients | List<Map> |  | 食材リスト | `[{"name": "豚バラ肉", "price": 298}]` |
| storeInfo | Map | ○ | 店舗情報のスナップショット | 以下参照 |
| imageUrl | String |  | レシピ画像URL（OGP用） | `https://s3.../shared-recipes/abc123.jpg` |
| sharedAt | String | ○ | 共有日時 | `2024-01-15T12:34:56Z` |
| sharedByUserId | String |  | 共有したユーザーID（任意） | `user_a1b2c3d4` |
| viewCount | Number | ○ | 閲覧数 | `152` |
| createdAt | String | ○ | 作成日時 | `2024-01-15T12:34:56Z` |
| updatedAt | String | ○ | 更新日時 | `2024-01-20T10:00:00Z` |

#### storeInfo の構造
```json
{
  "storeId": "store_001",
  "storeName": "スーパーA 新宿店",
  "storeLogo": "https://example.com/logos/store_001.png",
  "storeAddress": "東京都新宿区新宿1-1-1",
  "flyerValidFrom": "2024-01-15",
  "flyerValidUntil": "2024-01-21"
}
```

### アクセスパターン
1. 共有レシピIDで取得（PK） - SNS共有URLからのアクセス
2. チラシIDで共有レシピ一覧取得（GSI-1） - チラシページからの関連レシピ表示
3. 閲覧数の更新（PK + UpdateItem）

### 共有レシピの作成フロー

```python
# 1. ユーザーが「共有」ボタンをクリック
# 2. Recipesテーブルからレシピを取得
recipe = table.get_item(Key={'flyerId': 'flyer_001'})

# 3. Storesテーブルから店舗情報を取得（スナップショット用）
store = get_store_info(store_id)

# 4. SharedRecipesテーブルに新規作成
shared_recipe_id = str(uuid.uuid4())
table.put_item(
    Item={
        'sharedRecipeId': shared_recipe_id,
        'flyerId': recipe['flyerId'],
        'recipeText': recipe['recipeText'],
        'ingredients': recipe['ingredients'],
        'storeInfo': {
            'storeId': store['storeId'],
            'storeName': store['name'],
            'storeLogo': store['logo'],
            'storeAddress': store['address'],
            'flyerValidFrom': flyer['validFrom'],
            'flyerValidUntil': flyer['validUntil']
        },
        'sharedAt': datetime.now().isoformat(),
        'sharedByUserId': current_user_id or None,
        'viewCount': 0,
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
)

# 5. 共有URLを生成
share_url = f"https://chirashi-kitchen.com/shared-recipe/{shared_recipe_id}"
return share_url
```

### 備考
- **TTLなし**: 共有レシピは永続的に保存される
- **店舗情報のスナップショット**: チラシや店舗が削除されても、共有レシピは文脈を保持
- **ログイン不要でアクセス可能**: SNS経由のユーザーも閲覧できる
- **OGP対応**: `imageUrl` を使ってSNSでリッチプレビューを表示
- **閲覧数トラッキング**: 人気レシピのランキング表示などに活用可能

---

## 通知設定の管理

### 実装方法

通知設定は2つのテーブルで管理します：

1. **Usersテーブル**: グローバルな通知頻度設定
   - `notificationFrequency` (String): 通知頻度（`realtime` / `morning` / `evening`）

2. **FavoriteStoresテーブル**: 店舗ごとの通知トグル
   - `notificationEnabled` (Boolean): 店舗ごとに通知を有効/無効にする

### 通知頻度の詳細

| 値 | ラベル | 説明 |
|---|---|---|
| `realtime` | リアルタイム | 新着チラシが追加されたらすぐに通知 |
| `morning` | 毎朝 | 毎朝8時に前日の新着をまとめて通知 |
| `evening` | 毎夕 | 毎夕18時にその日の新着をまとめて通知 |

### 通知の動作

通知は以下の条件を **すべて満たす** 場合に送信されます：
1. ユーザーが通知頻度を設定している（`notificationFrequency`が設定されている）
2. 店舗がお気に入りに登録されている（`favorite-stores`テーブルにエントリが存在）
3. その店舗の通知が有効になっている（`notificationEnabled = true`）
4. 設定された頻度のタイミングで新着チラシがある

---

## DynamoDB設計のベストプラクティス

### 1. パーティションキーの選択
- 均等に分散されるキーを選択（hotspot回避）
- ユーザーID、店舗ID、商品IDなどのUUIDを使用

### 2. ソートキーの活用
- 範囲クエリが必要な場合はソートキーを使用（タイムスタンプ、日付など）
- PriceHistory: timestamp をソートキーにして期間指定クエリを実現

### 3. GSI（Global Secondary Index）の設計
- 主要なクエリパターンに基づいて設計
- プロジェクションタイプは通常 `ALL` を選択（読み取りコスト削減）

### 4. 非正規化
- JOINができないため、頻繁にアクセスするデータは非正規化して保存
- 例: Flyersテーブルに店舗名、企業名を保存

### 5. TTL（Time To Live）の活用
- 一時的なデータ（AIレシピなど）は自動削除
- コスト削減とストレージ管理の自動化

### 6. Sparse Index
- 特定の属性が存在する場合のみGSIに含める
- publishedAt が存在する記事のみ公開記事として検索可能

---

## データ整合性の管理

### 非正規化データの更新
企業名や店舗名を変更した場合、関連するテーブルのデータも更新する必要があります。

#### 更新が必要なケース
1. **企業名変更**
   - Admins テーブルの companyName
   - Stores テーブルの companyName
   - Flyers テーブルの companyName

2. **店舗名・情報変更**
   - Admins テーブルの storeName
   - Flyers テーブルの storeName
   - FavoriteStores テーブルの storeName

#### 実装方法
- Lambda関数で一括更新を実行
- DynamoDB Streams + Lambda で自動更新（推奨）

---

## インデックス戦略

### 読み取りパターンの最適化
1. **完全一致検索**: パーティションキー
2. **範囲検索**: ソートキー
3. **複数属性での検索**: GSI
4. **テキスト検索**: FilterExpression または Amazon OpenSearch Service

### コスト最適化
- GSIのプロジェクションタイプを適切に選択
- 不要なGSIは作成しない
- On-Demand課金 vs プロビジョニング課金を検討

---

## セキュリティ

### アクセス制御
- IAMロールによる最小権限の原則
- Lambda実行ロールに必要な権限のみ付与

### データ暗号化
- DynamoDB暗号化（AWS managed key または CMK）
- パスワードはbcryptでハッシュ化
- JWTトークンで認証

### 監査ログ
- DynamoDB Streams + CloudWatch Logs
- 重要な操作（管理者操作など）をログ記録

---

## パフォーマンス最適化

### 1. バッチ処理
- BatchGetItem / BatchWriteItem を使用
- 最大25件まで一括処理可能

### 2. パラレルスキャン
- 大量データのスキャンが必要な場合
- 通常は避けるべき（GSIで代替）

### 3. DAX（DynamoDB Accelerator）
- 読み取り負荷が高い場合に検討
- マイクロ秒単位のレイテンシ

### 4. キャッシング戦略
- Lambda内でキャッシュ（グローバル変数）
- ElastiCache（Redis/Memcached）の利用

---

## バックアップとリカバリ

### Point-in-Time Recovery（PITR）
- 35日間のバックアップ保持
- 秒単位でのリストア可能

### On-Demand Backup
- 手動バックアップの作成
- 長期保存が必要な場合

---

## モニタリング

### CloudWatch メトリクス
- ConsumedReadCapacityUnits
- ConsumedWriteCapacityUnits
- ThrottledRequests
- UserErrors
- SystemErrors

### アラート設定
- スロットリング発生時
- エラー率が閾値を超えた時
- 読み取り/書き込みキャパシティ使用率

---

## 移行・拡張性

### 将来の拡張
1. **地域拡大**: グローバルテーブルの検討
2. **データ量増加**: パーティション戦略の見直し
3. **新機能追加**: GSIの追加や属性の拡張

### データ移行
- DynamoDB Import/Export（S3経由）
- AWS Data Pipeline
- カスタムスクリプト（SDK）

---

## まとめ

このDB設計は、Chirashi Kitchenのフロント機能とAPI設計に基づいて作成されています。DynamoDBの特性を最大限活用し、以下の点を重視しています：

1. **アクセスパターン最適化**: 主要なクエリをGSIで効率化
2. **非正規化**: パフォーマンス向上のためデータを重複
3. **スケーラビリティ**: パーティションキーの均等分散
4. **コスト最適化**: 適切なインデックス設計とTTL活用

レビュー後、必要に応じて調整・拡張してください。
