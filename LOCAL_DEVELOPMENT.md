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

**データの永続化について:**
- データはDocker volumeに保存され、**コンテナを停止・再起動してもデータは保持されます**
- 2回目以降の起動時は、既存のテーブルとデータがそのまま使用されます
- テーブルの存在確認が行われ、既に存在する場合は初期化をスキップします

**データをリセットしたい場合:**

```bash
# オプション1: --reset オプションを使用（推奨）
./scripts/start-local.sh --reset

# オプション2: 手動でvolumeを削除
docker-compose down -v
./scripts/start-local.sh
```

または、手動で起動する場合：

```bash
# Docker Composeでサービスを起動
docker-compose up -d

# DynamoDB Localの起動を待つ（5秒程度）
sleep 5

# DynamoDBテーブルを初期化（既に存在する場合はスキップされます）
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

**重要: ポートについて**
- **ポート8000**: DynamoDB Local のAPIエンドポイント
  - ⚠️ ブラウザで開くと `400 Bad Request` が表示されますが、これは正常です
  - このポートはAWS APIコールを受け付けるためのもので、Webインターフェースではありません
  - AWS CLIやSDK（boto3）からアクセスするために使用します

- **ポート8002**: DynamoDB Admin の管理GUI
  - ✅ ブラウザでアクセスできます
  - テーブルの内容を視覚的に確認・編集できます

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

### 自動診断スクリプトを実行

問題が発生した場合、まず診断スクリプトを実行してください：

```bash
./scripts/troubleshoot-docker.sh
```

このスクリプトは以下を確認します：
- コンテナの起動状態
- ポートバインディング
- ログの内容
- ネットワーク設定
- DynamoDB APIへの接続

### ポート8002（DynamoDB Admin GUI）が開けない

**症状**: ブラウザでhttp://localhost:8002を開いても長時間読み込み中になる、またはエラーが出る

**解決方法**:

1. **コンテナのログを確認**:
   ```bash
   docker logs dynamodb-admin
   ```

2. **DynamoDB Adminコンテナを再起動**:
   ```bash
   docker-compose restart dynamodb-admin
   # 5秒待ってからブラウザでアクセス
   sleep 5
   ```

3. **ブラウザのキャッシュをクリア**:
   - ブラウザのキャッシュとCookieを削除
   - プライベートモード/シークレットモードで試す
   - 別のブラウザで試す

4. **完全に再起動**:
   ```bash
   docker-compose down
   docker-compose up -d
   sleep 5
   ```

5. **ポート競合の確認**:
   ```bash
   lsof -i :8002
   # 他のプロセスがポート8002を使用していないか確認
   ```

### ポート8000で400エラーが出る

**これは正常な動作です！** ポート8000はDynamoDB APIエンドポイントであり、ブラウザでアクセスするものではありません。

- ✅ 正常: AWS CLIやSDKから接続できる
- ❌ 期待しない: ブラウザで開くと400エラー

確認方法:
```bash
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region ap-northeast-1
```

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

### SAM Local APIを停止

```bash
Ctrl + C
```

### DynamoDB LocalとDynamoDB Adminを停止

**データを保持する場合（通常の停止）:**

```bash
# 方法1: コンテナを一時停止（再起動が速い）
docker-compose stop

# 方法2: コンテナを削除（volumeは保持される）
docker-compose down
```

**データを完全に削除する場合:**

```bash
# volumeも含めて完全削除
docker-compose down -v

# または、--resetオプションを使用して再起動
./scripts/start-local.sh --reset
```

### データ保持に関する重要な情報

| コマンド | コンテナ | データ | 用途 |
|---------|---------|-------|------|
| `docker-compose stop` | 停止 | **保持** | 一時的に停止（再起動が速い） |
| `docker-compose down` | 削除 | **保持** | 通常の停止（推奨） |
| `docker-compose down -v` | 削除 | **削除** | データをクリーンアップしたい時 |

💡 **ヒント:** 通常は `docker-compose down` を使用してください。データは保持され、次回起動時もそのまま利用できます。

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
