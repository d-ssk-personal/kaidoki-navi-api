# クイックスタートガイド

## 前提条件

- **Macbook** (macOS)
- **Docker Desktop** がインストールされて起動していること
- **AWS CLI** がインストールされていること
- **AWS SAM CLI** がインストールされていること
- **Python 3.12**

## 1. 環境のクリーンアップ（初回または問題がある場合）

```bash
# 既存のDocker環境を完全にクリーンアップ
./scripts/cleanup-docker.sh
```

これにより以下が削除されます：
- すべてのDynamoDBコンテナ
- すべてのDockerボリューム
- lambda-localネットワーク

## 2. ローカル環境の起動

```bash
# DynamoDB LocalとDynamoDB Admin GUIを起動
./scripts/start-local.sh
```

このスクリプトは自動的に：
1. Docker Desktopが起動しているか確認
2. lambda-localネットワークを作成
3. DynamoDB LocalとDynamoDB Adminを起動
4. DynamoDBテーブルを作成
5. テストデータを投入

## 3. 動作確認

### DynamoDB Admin GUI（port 8002）

ブラウザで以下のURLを開く：

```
http://localhost:8002
```

以下のテーブルが表示されればOK：
- `chirashi-kitchen-articles-local`
- `chirashi-kitchen-admins-local`
- `chirashi-kitchen-companies-local`
- `chirashi-kitchen-stores-local`
- など

**重要**:
- ポート8000（http://localhost:8000）をブラウザで開くと400エラーが出ますが、これは正常です
- ポート8000はDynamoDB APIエンドポイントであり、Webページではありません

### AWS CLIで確認

```bash
# テーブル一覧を取得
aws dynamodb list-tables \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1

# articlesテーブルの内容を確認
aws dynamodb scan \
  --table-name chirashi-kitchen-articles-local \
  --endpoint-url http://localhost:8000 \
  --region ap-northeast-1 \
  --max-items 5
```

## 4. SAM Localの起動

```bash
# Lambdaコードをビルド
sam build

# SAM Local APIを起動
sam local start-api \
  --docker-network lambda-local \
  --env-vars env.json
```

起動すると以下のように表示されます：

```
Mounting AdminLogin at http://127.0.0.1:3000/admin/auth/login [POST]
Mounting ListArticles at http://127.0.0.1:3000/admin/articles [GET]
...
Running on http://127.0.0.1:3000/
```

## 5. APIのテスト

### 管理者ログイン

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
  "token": "eyJ...",
  "admin": {
    "adminId": "admin-001",
    "username": "admin",
    "role": "system_admin"
  }
}
```

### 記事一覧の取得

```bash
# 上記で取得したトークンを使用
TOKEN="eyJ..."

curl -X GET "http://127.0.0.1:3000/admin/articles?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 記事の作成

```bash
curl -X POST http://127.0.0.1:3000/admin/articles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新しいコラム記事",
    "content": "これはテスト記事です。",
    "category": "health",
    "status": "draft",
    "tags": ["テスト", "サンプル"]
  }'
```

### DynamoDB Admin GUIで確認

1. ブラウザで http://localhost:8002 を開く
2. `chirashi-kitchen-articles-local` テーブルをクリック
3. 作成した記事が表示されることを確認

## トラブルシューティング

### ポート8002が開けない

```bash
# DynamoDB Adminを再起動
docker-compose restart dynamodb-admin

# 10秒待ってからブラウザでアクセス
sleep 10
```

または：

```bash
# 完全に再起動
./scripts/cleanup-docker.sh
./scripts/start-local.sh
```

### DynamoDB Localが起動しない

```bash
# ログを確認
docker logs dynamodb
# エラーが出ている場合は完全クリーンアップ
./scripts/cleanup-docker.sh
./scripts/start-local.sh
```

### SAM Localがエラーを出す

```bash
# キャッシュをクリアして再ビルド
rm -rf .aws-sam
sam build
```

## ディレクトリ構成

```
kaidoki-navi-api/
├── src/
│   ├── admin/           # 管理者API
│   │   ├── handlers/    # Lambdaハンドラ
│   │   └── repositories/# DynamoDBリポジトリ
│   ├── user/            # ユーザーAPI（未実装）
│   ├── utils/           # 共通ユーティリティ
│   └── config/          # 設定ファイル
├── scripts/
│   ├── start-local.sh   # 環境起動スクリプト
│   ├── cleanup-docker.sh # クリーンアップスクリプト
│   ├── init-dynamodb.sh # テーブル作成スクリプト
│   └── seed-data.sh     # テストデータ投入
├── docs/                # 設計書
├── template.yaml        # SAM テンプレート
├── docker-compose.yml   # Docker設定
└── env.json            # 環境変数
```

## 停止方法

### DynamoDBだけ停止（データは失われる - インメモリモード）

```bash
docker-compose down
```

### SAM Localを停止

`Ctrl+C` で停止

## 次のステップ

1. `docs/api-design-admin.yaml` でAPI仕様を確認
2. `docs/database-design.md` でDB設計を確認
3. 追加のAPI機能を実装
4. AWSへのデプロイ準備（deploy.sh, destroy.sh使用）

## テストアカウント

| ユーザー名 | パスワード | ロール |
|-----------|----------|-------|
| admin | password | システム管理者 |
| company | password | 企業管理者 |
| store | password | 店舗ユーザー |
