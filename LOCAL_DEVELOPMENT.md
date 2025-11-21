# ローカル開発環境セットアップガイド

このガイドでは、Chirashi Kitchen APIのローカル開発環境を構築する手順を説明します。

## 必要な環境

- Docker Desktop
- AWS SAM CLI
- AWS CLI
- Python 3.12

## セットアップ手順

### 1. Dockerネットワークの作成（初回のみ）

```bash
docker network create lambda-local
```

### 2. DynamoDB LocalとDynamoDB Adminの起動

```bash
# ワンコマンドで起動（推奨）
./scripts/start-local.sh
```

または、手動で起動する場合：

```bash
# Docker Composeでサービスを起動
docker-compose up -d

# DynamoDB Localの起動を待つ（5秒程度）
sleep 5

# DynamoDBテーブルを初期化
./scripts/init-dynamodb.sh

# テストデータを投入（オプション）
./scripts/seed-data.sh
```

### 3. SAM Local APIの起動

```bash
# ビルド
sam build

# ローカルAPIサーバーを起動
sam local start-api --docker-network lambda-local --env-vars env.json --parameter-overrides file://env.json
```

起動すると以下のようなメッセージが表示されます：

```
Mounting AdminLoginFunction at http://127.0.0.1:3000/admin/auth/login [POST]
Mounting ArticlesListFunction at http://127.0.0.1:3000/admin/articles/list [GET]
...
You can now browse to the above endpoints to invoke your functions.
You do not need to restart/reload SAM CLI while working on your functions,
changes will be reflected instantly/automatically. If you used sam build before,
you will need to re-run sam build for the changes to be picked up.
```

## 確認

### DynamoDB Admin GUIで確認

ブラウザで以下のURLを開きます：

```
http://localhost:8002
```

以下のテーブルが表示されていればOKです：

- chirashi-kitchen-articles-local
- chirashi-kitchen-admins-local
- chirashi-kitchen-companies-local
- chirashi-kitchen-stores-local
- chirashi-kitchen-flyers-local
- chirashi-kitchen-users-local
- 他...

### APIの動作確認

#### 1. 管理者ログイン

```bash
curl -X POST http://127.0.0.1:3000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

レスポンス例：

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": "admin001",
    "username": "admin",
    "name": "システム管理者",
    "role": "system_admin"
  }
}
```

#### 2. コラム一覧取得

上記で取得したトークンを使用：

```bash
TOKEN="<取得したトークン>"

curl -X GET "http://127.0.0.1:3000/admin/articles/list" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. コラム追加

```bash
curl -X POST http://127.0.0.1:3000/admin/articles/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "テストコラム",
    "content": "これはテストコラムです。",
    "category": "節約術",
    "status": "published",
    "tags": ["テスト", "サンプル"]
  }'
```

#### 4. DynamoDB Adminで確認

http://localhost:8002 を開き、`chirashi-kitchen-articles-local` テーブルを確認すると、追加したコラムが表示されます。

## テストログイン情報

テストデータを投入した場合、以下のアカウントが使用できます：

| ユーザー名 | パスワード | 役割 |
|---------|---------|------|
| admin | password | システム管理者 |
| company | password | 企業管理者 |
| store | password | 店舗ユーザー |

## トラブルシューティング

### ポートが既に使用されている

```bash
# 使用中のポートを確認
lsof -i :3000
lsof -i :8000
lsof -i :8002

# Dockerコンテナを停止
docker-compose down
```

### DynamoDBテーブルが作成されない

```bash
# DynamoDB Localが起動しているか確認
docker ps | grep dynamodb-local

# 手動でテーブルを作成
./scripts/init-dynamodb.sh
```

### SAM Buildエラー

```bash
# キャッシュをクリアして再ビルド
sam build --use-container --cached
```

### Dockerネットワークエラー

```bash
# ネットワークを削除して再作成
docker network rm lambda-local
docker network create lambda-local

# Dockerコンテナを再起動
docker-compose down
docker-compose up -d
```

## 停止方法

```bash
# SAM Local APIを停止
Ctrl + C

# Docker Composeのサービスを停止
docker-compose down

# データを保持したまま停止
docker-compose stop

# データも含めて完全に削除
docker-compose down -v
```

## ディレクトリ構造

```
kaidoki-navi-api/
├── docker-compose.yml          # DynamoDB Local + Admin
├── env.json                     # SAM Local用環境変数
├── .env.local                   # 環境変数（参考用）
├── scripts/
│   ├── start-local.sh          # ワンコマンド起動スクリプト
│   ├── init-dynamodb.sh        # テーブル初期化
│   └── seed-data.sh            # テストデータ投入
├── src/
│   ├── admin/                  # 管理者機能
│   └── user/                   # ユーザー機能
└── template.yaml               # SAM テンプレート
```

## 開発ワークフロー

1. コードを修正
2. SAM Localが自動的に変更を検知（Pythonファイルの変更はリロード不要）
3. APIをテスト
4. DynamoDB Adminでデータを確認

**注意**: `template.yaml` や新しいLambda関数を追加した場合は `sam build` を再実行してください。

## 次のステップ

- [API設計書](docs/api/api-design-admin.yaml) を確認
- [データベース設計書](docs/database-design.md) を確認
- フロントエンド（kaidoki-naviリポジトリ）と連携
