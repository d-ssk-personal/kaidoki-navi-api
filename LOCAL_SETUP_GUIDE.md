# ローカル環境セットアップガイド

開拓ナビ管理者APIをローカルで起動してテストするための完全ガイドです。

## 📋 前提条件

以下がインストールされていることを確認してください：

- ✅ Docker Desktop（起動済み）
- ✅ AWS CLI
- ✅ AWS SAM CLI
- ✅ Python 3.12

## 🚀 起動手順（初回）

### ステップ1: Dockerコンテナを起動

```bash
./scripts/start-local.sh
```

**確認方法:**
- DynamoDB Admin GUI: http://localhost:8002 にアクセス
- テーブル一覧が表示されればOK（まだテーブルは空）

### ステップ2: DynamoDBテーブルを初期化

```bash
./scripts/init-dynamodb.sh
```

**確認方法:**
- http://localhost:8002 で以下のテーブルが表示されることを確認
  - admins
  - articles
  - companies
  - stores
  - flyers

### ステップ3: テストデータを投入

```bash
./scripts/seed-data.sh
```

**確認方法:**
- http://localhost:8002 で各テーブルにデータが入っていることを確認
  - admins: 3件
  - articles: 3件
  - companies: 1件
  - stores: 1件

### ステップ4: SAM Local APIを起動（別ターミナル）

**新しいターミナルを開いて以下を実行:**

```bash
./scripts/start-sam-local.sh
```

または

```bash
sam local start-api --env-vars env.json --docker-network lambda-local
```

**確認方法:**
```bash
# 別のターミナルで
curl http://localhost:3000/admin/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

成功すると、JWTトークンが返ってきます：
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "adminId": "admin001",
    "username": "admin",
    "role": "system_admin",
    ...
  }
}
```

## 🔄 起動手順（2回目以降）

Dockerコンテナとテーブルは既に作成されているので、以下の2つだけでOK：

### ターミナル1: Dockerコンテナ起動

```bash
# Dockerコンテナが停止している場合のみ
docker-compose up -d
```

または既に起動している場合は不要（`docker ps`で確認）

### ターミナル2: SAM Local起動

```bash
./scripts/start-sam-local.sh
```

## 🧪 動作確認

### 方法1: curlでテスト

```bash
# 1. ログイン
TOKEN=$(curl -s http://localhost:3000/admin/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.token')

echo "Token: $TOKEN"

# 2. コラム一覧取得
curl http://localhost:3000/admin/articles/list \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### 方法2: Talend API Testerでテスト

1. Chrome拡張機能「Talend API Tester」をインストール
2. `api-collection/Kaidoki-navi.postman_collection.json` をインポート
3. 「管理者ログイン」を実行
4. 「コラム一覧取得」などのAPIを実行

詳細は [api-collection/QUICKSTART.md](./api-collection/QUICKSTART.md) を参照

## 📊 各ポートの役割

| ポート | サービス | URL | 用途 |
|--------|----------|-----|------|
| 8000 | DynamoDB Local | http://localhost:8000 | DynamoDB API（直接アクセス不要） |
| 8002 | DynamoDB Admin | http://localhost:8002 | データベースGUI |
| 3000 | SAM Local API | http://localhost:3000 | 管理者API |

## ⚠️ よくあるエラーと解決方法

### エラー1: `Failed to connect to localhost port 3000`

**原因**: SAM Localが起動していない

**解決策**:
```bash
# 別ターミナルで
./scripts/start-sam-local.sh
```

### エラー2: `Table does not exist`

**原因**: DynamoDBテーブルが初期化されていない

**解決策**:
```bash
./scripts/init-dynamodb.sh
./scripts/seed-data.sh
```

### エラー3: `Authentication required`

**原因**: トークンが無効または期限切れ

**解決策**:
```bash
# 再度ログイン
curl -X POST http://localhost:3000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'
```

### エラー4: DynamoDB Adminでテーブルが見えない

**原因**: Dockerコンテナが起動していない

**解決策**:
```bash
# コンテナの状態確認
docker ps

# 起動していない場合
docker-compose up -d

# または
./scripts/start-local.sh
```

### エラー5: `Cannot connect to the Docker daemon`

**原因**: Docker Desktopが起動していない

**解決策**:
1. Docker Desktopを起動
2. 起動完了を待つ
3. 再度スクリプトを実行

## 🛑 環境の停止

### SAM Localを停止
実行中のターミナルで `Ctrl+C`

### Dockerコンテナを停止
```bash
docker-compose down

# データも削除する場合（初期化）
docker-compose down -v
```

## 🔄 環境のリセット

データベースを完全にリセットして初期状態に戻す場合：

```bash
# 1. 全て停止
# SAM LocalのターミナルでCtrl+C

# 2. Dockerコンテナとボリュームを削除
docker-compose down -v

# 3. 再セットアップ
./scripts/start-local.sh      # ターミナル1
./scripts/init-dynamodb.sh
./scripts/seed-data.sh
./scripts/start-sam-local.sh  # ターミナル2
```

## 📝 テストユーザー情報

| ユーザー名 | パスワード | 役割 | 権限 |
|-----------|----------|------|------|
| admin | password | system_admin | 全権限 |
| company | password | company_admin | 企業管理権限 |
| store | password | store_user | 店舗権限 |

## 📚 関連ドキュメント

- [API Collection QUICKSTART](./api-collection/QUICKSTART.md) - APIテストガイド
- [API Collection README](./api-collection/README.md) - APIドキュメント
- [Architecture](./docs/architecture.md) - アーキテクチャ設計
- [Testing Guide](./docs/testing.md) - テストガイド

## 💡 Tips

### バックグラウンドで起動

SAM Localをバックグラウンドで起動したい場合：

```bash
nohup sam local start-api --env-vars env.json --docker-network lambda-local > sam-local.log 2>&1 &

# ログを確認
tail -f sam-local.log

# 停止
pkill -f "sam local"
```

### ログの確認

```bash
# SAM Localのログ
# ターミナルに表示されます

# DynamoDBのログ
docker-compose logs -f dynamodb-local

# DynamoDB Adminのログ
docker-compose logs -f dynamodb-admin
```

### ポート番号の変更

ポート3000が使用中の場合：

```bash
# ポート3001で起動
sam local start-api --env-vars env.json --docker-network lambda-local --port 3001

# APIコレクションの環境変数も変更
# base_url: http://localhost:3001
```

## 🎯 次のステップ

環境が起動したら：

1. **Talend API Testerでテスト**: [api-collection/QUICKSTART.md](./api-collection/QUICKSTART.md)
2. **テストコードを実行**: [docs/testing.md](./docs/testing.md)
3. **新しいAPIを追加**: [docs/architecture.md](./docs/architecture.md)

Happy Coding! 🚀
