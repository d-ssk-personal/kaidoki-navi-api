# クイックスタートガイド

開拓ナビ管理者APIを5分でローカル起動するガイドです。

## 📋 前提条件

以下がインストールされて起動していることを確認してください：

- ✅ **Docker Desktop** (起動済み)
- ✅ **AWS CLI**
- ✅ **AWS SAM CLI**
- ✅ **Python 3.12**

## 🚀 起動手順

### ⚡️ 初回セットアップ（3ステップ）

#### ステップ1: Dockerコンテナを起動（ターミナル1）

```bash
./scripts/start-local.sh
```

**何が起こる:**
- DynamoDB LocalとAdmin GUIが起動
- ポート8000（DynamoDB API）とポート8002（Admin GUI）が開く

**確認:** http://localhost:8002 でDynamoDB Admin GUIが開く

#### ステップ2: テーブルを初期化してデータ投入

```bash
./scripts/init-dynamodb.sh
./scripts/seed-data.sh
```

**何が起こる:**
- 5つのテーブルが作成される（admins, articles, companies, stores, flyers）
- テストデータが投入される（管理者3件、コラム3件など）

**確認:** http://localhost:8002 でテーブルとデータが表示される

#### ステップ3: SAM Local APIを起動（ターミナル2 - 別ターミナルを開く）

```bash
# 新しいターミナルを開いて実行
./scripts/start-sam-local.sh
```

または

```bash
sam local start-api --env-vars env.json --docker-network lambda-local
```

**何が起こる:**
- ポート3000でAPIが起動
- 管理者APIのエンドポイントが利用可能になる

**確認:** 以下のメッセージが表示されます
```
Mounting AdminLoginFunction at http://127.0.0.1:3000/admin/auth/login [POST]
Mounting ArticlesApiFunction at http://127.0.0.1:3000/admin/articles/list [GET]
...
Running on http://127.0.0.1:3000/
```

### ⚡️ 2回目以降の起動（2ステップ）

データは既にあるので、2つのサービスを起動するだけ：

```bash
# ターミナル1: Dockerコンテナ起動（停止している場合のみ）
docker-compose up -d

# ターミナル2: SAM Local起動
./scripts/start-sam-local.sh
```

## ✅ 動作確認

### 方法1: curlでテスト

```bash
# 1. ログイン
curl -X POST http://localhost:3000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

**期待されるレスポンス:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "adminId": "admin001",
    "username": "admin",
    "role": "system_admin",
    "name": "システム管理者"
  }
}
```

```bash
# 2. トークンを環境変数に保存
TOKEN="<上記で取得したトークン>"

# 3. コラム一覧を取得
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/admin/articles/list
```

**期待されるレスポンス:**
```json
{
  "items": [
    {
      "articleId": 1,
      "title": "2025年1月の値上げ情報まとめ",
      "category": "値上げ情報",
      "status": "published",
      ...
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 1,
    "totalItems": 2,
    "limit": 20
  }
}
```

### 方法2: Talend API Testerでテスト（推奨）

1. Chrome拡張機能「Talend API Tester」をインストール
2. `api-collection/Kaidoki-navi.postman_collection.json` をインポート
3. 「管理者ログイン」を実行（トークンが自動保存される）
4. 各種APIを実行

**詳細:** [api-collection/QUICKSTART.md](./api-collection/QUICKSTART.md)

## 🎯 起動後に確認すべき3つのURL

| サービス | URL | 説明 |
|---------|-----|------|
| DynamoDB Admin | http://localhost:8002 | データベースGUI（テーブルとデータを確認） |
| API Gateway | http://localhost:3000 | 管理者APIエンドポイント |
| DynamoDB API | http://localhost:8000 | DynamoDB Local（直接アクセス不要） |

## ⚠️ よくあるエラーと解決方法

### ❌ `Failed to connect to localhost port 3000`

**原因:** SAM Localが起動していない

**解決策:**
```bash
# 別のターミナルを開いて
./scripts/start-sam-local.sh
```

> **重要:** SAM Localは `start-local.sh` とは**別のターミナル**で起動する必要があります！

### ❌ `Table does not exist` / `ResourceNotFoundException`

**原因:** DynamoDBテーブルが初期化されていない

**解決策:**
```bash
./scripts/init-dynamodb.sh
./scripts/seed-data.sh
```

### ❌ `Authentication required` (401)

**原因:** トークンが無効または期限切れ

**解決策:** 再度ログインしてトークンを取得
```bash
curl -X POST http://localhost:3000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

### ❌ DynamoDB Adminでテーブルが見えない

**原因:** Dockerコンテナが起動していない

**解決策:**
```bash
# コンテナの状態確認
docker ps

# 停止している場合
docker-compose up -d
```

### ❌ `Cannot connect to the Docker daemon`

**原因:** Docker Desktopが起動していない

**解決策:** Docker Desktopを起動して、緑のアイコンになるまで待つ

## 📝 テストユーザー情報

| ユーザー名 | パスワード | 役割 | 権限 |
|-----------|----------|------|------|
| admin | password | system_admin | 全権限 |
| company | password | company_admin | 企業管理 |
| store | password | store_user | 店舗管理 |

## 🛑 環境の停止

```bash
# SAM Local停止: 実行中のターミナルでCtrl+C

# Dockerコンテナ停止
docker-compose down

# データも削除する場合（完全リセット）
docker-compose down -v
```

## 🔄 環境のリセット

データベースを完全に初期化したい場合：

```bash
# 1. 全て停止してデータ削除
docker-compose down -v

# 2. 再セットアップ
./scripts/start-local.sh
./scripts/init-dynamodb.sh
./scripts/seed-data.sh

# 3. SAM Local起動（別ターミナル）
./scripts/start-sam-local.sh
```

## 📚 次のステップ

環境が起動したら：

1. **APIをテストする**
   - [api-collection/QUICKSTART.md](./api-collection/QUICKSTART.md) - Talend API Testerでテスト

2. **開発環境の詳細を確認**
   - [LOCAL_SETUP_GUIDE.md](./LOCAL_SETUP_GUIDE.md) - 詳細なセットアップガイド

3. **アーキテクチャを理解する**
   - [docs/architecture.md](./docs/architecture.md) - システム設計

4. **テストを実行する**
   - [docs/testing.md](./docs/testing.md) - テストガイド

## 💡 ワンライナーで起動（上級者向け）

```bash
# ターミナル1（バックグラウンド）
docker-compose up -d && sleep 5 && ./scripts/init-dynamodb.sh && ./scripts/seed-data.sh

# ターミナル2
./scripts/start-sam-local.sh
```

## 📊 プロジェクト構成

```
kaidoki-navi-api/
├── src/admin/              # 管理者API実装
│   ├── handlers/           # Lambda関数ハンドラー
│   ├── services/           # ビジネスロジック
│   └── repositories/       # データアクセス層
├── scripts/                # 起動・管理スクリプト
├── api-collection/         # APIテスト用コレクション
├── docs/                   # ドキュメント
├── template.yaml           # SAM設定（インフラ定義）
└── docker-compose.yml      # Docker設定
```

Happy Coding! 🚀
