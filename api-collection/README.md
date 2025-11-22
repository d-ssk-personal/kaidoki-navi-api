# API コレクション

開拓ナビ管理者APIのテスト用コレクションです。

## 📁 ファイル

- **Kaidoki-navi.postman_collection.json**: APIコレクション（全エンドポイント）
- **Local.postman_environment.json**: ローカル環境設定

## 🚀 使用方法

### Talend API Testerでのインポート

1. **Chrome拡張機能をインストール**
   - Chrome Web Storeで「Talend API Tester」を検索してインストール

2. **コレクションをインポート**
   - Talend API Testerを開く
   - 左上の「Import」ボタンをクリック
   - `Kaidoki-navi.postman_collection.json` を選択してインポート

3. **環境変数をインポート（オプション）**
   - 「Environments」タブを開く
   - 「Import」をクリック
   - `Local.postman_environment.json` を選択してインポート
   - 「Local」環境を選択

### Postmanでのインポート

1. **Postmanをインストール**
   - https://www.postman.com/downloads/ からダウンロード

2. **コレクションをインポート**
   - Postmanを開く
   - 左上の「Import」ボタンをクリック
   - `Kaidoki-navi.postman_collection.json` をドラッグ&ドロップ

3. **環境変数をインポート**
   - 「Environments」タブを開く
   - 「Import」をクリック
   - `Local.postman_environment.json` を選択
   - 右上のドロップダウンから「Local」環境を選択

## 📋 コレクション構造

```
Kaidoki-navi/
├── admin-auth/
│   └── 管理者ログイン (POST /admin/auth/login)
└── admin-articles/
    ├── コラム一覧取得 (GET /admin/articles/list)
    ├── コラム詳細取得 (GET /admin/articles/list/{articleId})
    ├── コラム作成 (POST /admin/articles/add)
    ├── コラム更新 (PUT /admin/articles/update/{articleId})
    ├── コラム削除 (DELETE /admin/articles/delete/{articleId})
    ├── ステータス一括更新 (PUT /admin/articles/bulk-status)
    └── 記事一括削除 (DELETE /admin/articles/bulk-delete)
```

## 🔑 認証の流れ

### 1. ローカル環境を起動

```bash
# Dockerコンテナを起動
./scripts/start-local.sh

# SAM Localを起動（別ターミナル）
sam local start-api --env-vars env.json --docker-network lambda-local
```

### 2. 管理者ログイン

1. `admin-auth` フォルダの「管理者ログイン」を実行
2. レスポンスからJWTトークンが自動的に `access_token` 変数に保存されます
3. 以降のリクエストでは自動的にトークンが使用されます

**デフォルトの認証情報:**
```json
{
  "username": "admin",
  "password": "password"
}
```

> ⚠️ **注意**: ローカル環境では管理者データをシードする必要があります。
> `scripts/seed-data.sh` を実行してテストデータを投入してください。

### 3. APIを実行

- `admin-articles` フォルダ内の任意のAPIを実行できます
- 全てのリクエストに自動的に `Authorization: Bearer {{access_token}}` ヘッダーが付与されます

## 🔧 環境変数

### Local 環境

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| base_url | http://localhost:3000 | SAM LocalのエンドポイントURL |
| access_token | (自動設定) | JWTトークン（ログイン時に自動保存） |

### カスタム環境の作成

AWS環境など別の環境を追加する場合:

1. Talend API Tester / Postmanで新しい環境を作成
2. 以下の変数を設定:
   - `base_url`: APIのベースURL（例: https://api.example.com）
   - `access_token`: （空欄、ログイン時に自動保存されます）

## 📝 APIリクエスト例

### コラム一覧取得（フィルター付き）

```
GET {{base_url}}/admin/articles/list?page=1&limit=20&status=published&category=テクノロジー
Authorization: Bearer {{access_token}}
```

### コラム作成

```
POST {{base_url}}/admin/articles/add
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "title": "新しいコラム",
  "content": "コラムの本文です",
  "category": "テクノロジー",
  "status": "draft",
  "tags": ["AI", "機械学習"],
  "publishedAt": "2025-01-15T00:00:00Z"
}
```

### ステータス一括更新

```
PUT {{base_url}}/admin/articles/bulk-status
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "articleIds": [1, 2, 3],
  "status": "published"
}
```

## 🧪 テストデータの準備

ローカル環境でテストする前に、以下のスクリプトでテストデータを投入してください:

```bash
# DynamoDBテーブルを初期化
./scripts/init-dynamodb.sh

# テストデータを投入
./scripts/seed-data.sh
```

## 📚 関連ドキュメント

- [アーキテクチャ設計](../docs/architecture.md)
- [テストガイド](../docs/testing.md)
- [クイックスタート](../QUICKSTART.md)

## ⚠️ トラブルシューティング

### エラー: "Authentication required"

- ログインAPIを実行して `access_token` を取得してください
- トークンの有効期限（24時間）が切れている可能性があります

### エラー: "Failed to connect"

- SAM Localが起動しているか確認してください: `http://localhost:3000`
- Dockerコンテナが起動しているか確認してください: `docker ps`

### エラー: "Table does not exist"

- DynamoDBテーブルを初期化してください: `./scripts/init-dynamodb.sh`

### トークンが自動保存されない

Talend API Testerの場合:
1. 「管理者ログイン」リクエストの「Tests」タブを確認
2. 以下のスクリプトが設定されているか確認:
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set('access_token', response.token);
}
```

## 💡 Tips

### リクエストの複製

同じAPIで異なるパラメータをテストしたい場合:
1. リクエストを右クリック
2. 「Duplicate」を選択
3. パラメータを変更して保存

### フォルダの整理

新しいAPI群を追加する場合:
1. コレクション内で右クリック
2. 「Add Folder」を選択
3. フォルダ名を入力（例: `admin-companies`）

### クエリパラメータの有効/無効切り替え

URLのクエリパラメータは個別にチェックボックスで有効/無効を切り替えられます。
フィルターのテストに便利です。
