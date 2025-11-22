# 買いどきナビ API

チラシ情報管理システムのバックエンドAPI

## プロジェクト構成

```
kaidoki-navi-api/
├── src/
│   ├── admin/              # 管理者API
│   │   ├── handlers/       # Lambda関数ハンドラ
│   │   └── repositories/   # DynamoDBリポジトリ
│   ├── user/               # ユーザーAPI（未実装）
│   ├── utils/              # 共通ユーティリティ
│   └── config/             # 設定ファイル
├── scripts/
│   ├── deploy.sh           # AWS環境デプロイ
│   ├── destroy.sh          # AWS環境削除
│   ├── start-local.sh      # ローカル環境起動
│   ├── cleanup-docker.sh   # Docker環境クリーンアップ
│   ├── generate_init_script.py  # テーブル定義自動生成
│   └── seed-data.sh        # テストデータ投入
├── docs/                   # 設計書
│   ├── database-design.md  # データベース設計
│   └── api-design-admin.yaml  # API設計
├── template.yaml           # SAMテンプレート（テーブル定義の唯一の真実の源）
├── docker-compose.yml      # ローカル開発環境
├── env.json                # SAM Local環境変数
└── QUICKSTART.md          # クイックスタートガイド

## 🎯 特徴

- **テーブル定義の一元管理**: `template.yaml`を唯一の真実の源（Single Source of Truth）として、ローカル環境とAWS環境の両方で同じテーブル定義を使用
- **自動生成スクリプト**: `template.yaml`から`init-dynamodb.sh`を自動生成
- **ローカル開発環境**: DynamoDB LocalとDynamoDB Admin GUIで快適な開発
- **Python 3.12**: 最新のPythonランタイム
- **AWS SAM**: サーバーレスアプリケーションのデプロイとローカルテスト

## 🚀 クイックスタート

詳細な手順は[QUICKSTART.md](QUICKSTART.md)を参照してください。

### 前提条件

- Macbook (macOS)
- Docker Desktop
- AWS CLI
- AWS SAM CLI
- Python 3.12

### ローカル環境の起動

```bash
# Docker環境を起動してDynamoDBテーブルを作成
./scripts/start-local.sh

# SAM Localを起動
sam build
sam local start-api --docker-network lambda-local --env-vars env.json
```

DynamoDB Admin GUI: http://localhost:8002
SAM Local API: http://127.0.0.1:3000

### AWS環境へのデプロイ

```bash
# 開発環境にデプロイ
./scripts/deploy.sh development

# 本番環境にデプロイ
./scripts/deploy.sh production
```

## 📋 テーブル定義の管理

### 重要: テーブル定義は`template.yaml`で一元管理されています

テーブル定義を変更する場合の手順：

1. **`template.yaml`を編集**してテーブル定義を変更
2. **自動生成スクリプトを実行**してローカル環境用のスクリプトを更新:
   ```bash
   python scripts/generate_init_script.py
   ```
3. **ローカル環境を再起動**:
   ```bash
   ./scripts/cleanup-docker.sh
   ./scripts/start-local.sh
   ```

### テーブル名の規則

- **AWS環境**: `chirashi-kitchen-{table}-${Environment}` (例: `chirashi-kitchen-articles-development`)
- **ローカル環境**: `chirashi-kitchen-{table}` (例: `chirashi-kitchen-articles`)

### なぜ一元管理が重要か？

- **整合性**: ローカル環境とAWS環境で同じテーブル構造を保証
- **メンテナンス性**: 1箇所の変更で両環境に反映
- **バグ防止**: 定義のずれによるエラーを防止

## 🗄️ DynamoDBテーブル

現在実装されているテーブル：

- `chirashi-kitchen-admins` - 管理者ユーザー
- `chirashi-kitchen-articles` - コラム記事
- `chirashi-kitchen-companies` - 企業情報
- `chirashi-kitchen-stores` - 店舗情報
- `chirashi-kitchen-flyers` - チラシ情報
- `chirashi-kitchen-users` - エンドユーザー
- `chirashi-kitchen-favorite-stores` - お気に入り店舗
- `chirashi-kitchen-recipes` - レシピ
- `chirashi-kitchen-shared-recipes` - 共有レシピ

## 🔧 開発

### ディレクトリ構成

```
src/
├── admin/
│   ├── handlers/
│   │   ├── auth.py          # 認証
│   │   └── articles.py      # コラム管理
│   └── repositories/
│       ├── admin_repository.py
│       └── article_repository.py
├── utils/
│   ├── auth.py              # JWT認証
│   ├── response.py          # APIレスポンス
│   ├── logger.py            # ロギング
│   └── s3.py                # S3画像アップロード
└── config/
    └── settings.py          # 環境設定
```

### 環境変数

`env.json`でローカル環境の環境変数を設定：

- `DYNAMODB_ENDPOINT_URL`: DynamoDB Localのエンドポイント
- `ARTICLES_TABLE_NAME`: テーブル名
- `JWT_SECRET_KEY`: JWT署名キー

### テストアカウント

| ユーザー名 | パスワード | ロール |
|-----------|----------|-------|
| admin | password | システム管理者 |
| company | password | 企業管理者 |
| store | password | 店舗ユーザー |

## 📚 ドキュメント

- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [DEPLOYMENT.md](DEPLOYMENT.md) - デプロイメントガイド
- [docs/database-design.md](docs/database-design.md) - データベース設計書
- [docs/api-design-admin.yaml](docs/api-design-admin.yaml) - 管理者API設計書

## 🛠️ トラブルシューティング

### Docker環境がうまく起動しない

```bash
# 完全クリーンアップしてから再起動
./scripts/cleanup-docker.sh
./scripts/start-local.sh
```

### テーブル定義を変更したのに反映されない

```bash
# テーブル定義の自動生成スクリプトを実行
python scripts/generate_init_script.py

# Docker環境を再起動
./scripts/cleanup-docker.sh
./scripts/start-local.sh
```

### SAM Localでエラーが出る

```bash
# キャッシュをクリアして再ビルド
rm -rf .aws-sam
sam build
```

## 📝 ライセンス

非公開プロジェクト
