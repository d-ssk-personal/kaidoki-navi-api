# クイックスタートガイド - APIテスト

このガイドでは、Talend API Testerを使って開拓ナビ管理者APIをテストする手順を説明します。

## 🚀 5分で始めるAPIテスト

### ステップ1: ローカル環境を起動

```bash
# 1. Dockerコンテナを起動
cd /path/to/kaidoki-navi-api
./scripts/start-local.sh

# 2. SAM Localを起動（別ターミナル）
sam local start-api --env-vars env.json --docker-network lambda-local
```

✅ 起動確認:
- DynamoDB Admin: http://localhost:8002
- SAM Local API: http://localhost:3000

### ステップ2: テストデータを投入

```bash
# DynamoDBテーブルを初期化
./scripts/init-dynamodb.sh

# テストデータを投入
./scripts/seed-data.sh
```

✅ 確認: http://localhost:8002 で以下のテーブルにデータがあることを確認
- `admins` テーブル: 3件のユーザー
- `articles` テーブル: 3件のコラム
- `companies` テーブル: 1件の企業
- `stores` テーブル: 1件の店舗

### ステップ3: Talend API Testerをセットアップ

#### 3-1. 拡張機能のインストール

1. Chromeを開く
2. [Talend API Tester](https://chrome.google.com/webstore/detail/talend-api-tester-free-ed/aejoelaoggembcahagimdiliamlcdmfm) にアクセス
3. 「Chromeに追加」をクリック

#### 3-2. コレクションをインポート

1. Talend API Testerを開く
2. 左上の「**Project**」タブを選択
3. 「**Import**」ボタンをクリック
4. `api-collection/Kaidoki-navi.postman_collection.json` を選択
5. 「**Kaidoki-navi**」プロジェクトが作成されます

#### 3-3. 環境変数を設定（オプション）

1. 右上の「**Environments**」ドロップダウンをクリック
2. 「**Manage environments**」を選択
3. 「**Import**」をクリック
4. `api-collection/Local.postman_environment.json` を選択
5. 「**Local**」環境を選択

または、手動で設定:
1. 「**New Environment**」をクリック
2. 名前: `Local`
3. 変数を追加:
   - `base_url`: `http://localhost:3000`
   - `access_token`: （空欄）

### ステップ4: APIをテストする

#### 4-1. ログイン

1. 左サイドバーの **Kaidoki-navi** を展開
2. **admin-auth** フォルダを展開
3. 「**管理者ログイン**」をクリック
4. 「**Send**」ボタンをクリック

**期待されるレスポンス:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "adminId": "admin001",
    "username": "admin",
    "role": "system_admin",
    "name": "システム管理者",
    "email": "admin@example.com"
  }
}
```

✅ トークンが自動的に `access_token` 変数に保存されます

#### 4-2. コラム一覧を取得

1. **admin-articles** フォルダを展開
2. 「**コラム一覧取得**」をクリック
3. 「**Send**」ボタンをクリック

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
    },
    ...
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 1,
    "totalItems": 2,
    "limit": 20
  }
}
```

#### 4-3. コラムを作成

1. 「**コラム作成**」をクリック
2. Bodyを確認（必要に応じて編集）
3. 「**Send**」ボタンをクリック

**期待されるレスポンス:**
```json
{
  "articleId": 4,
  "title": "新しいコラムのタイトル",
  "content": "これはコラムの本文です...",
  "status": "draft",
  ...
}
```

#### 4-4. その他のAPI

同様に以下のAPIをテストできます:
- コラム詳細取得
- コラム更新
- コラム削除
- ステータス一括更新
- 記事一括削除

## 📝 利用可能なテストユーザー

| ユーザー名 | パスワード | 役割 | 説明 |
|-----------|----------|------|------|
| admin | password | system_admin | システム管理者（全権限） |
| company | password | company_admin | 企業管理者（企業内の権限） |
| store | password | store_user | 店舗ユーザー（店舗内の権限） |

## 🔍 APIエンドポイント一覧

### 認証
- `POST /admin/auth/login` - 管理者ログイン

### コラム管理
- `GET /admin/articles/list` - コラム一覧取得
- `GET /admin/articles/list/{articleId}` - コラム詳細取得
- `POST /admin/articles/add` - コラム作成
- `PUT /admin/articles/update/{articleId}` - コラム更新
- `DELETE /admin/articles/delete/{articleId}` - コラム削除
- `PUT /admin/articles/bulk-status` - ステータス一括更新
- `DELETE /admin/articles/bulk-delete` - 記事一括削除

## 💡 便利なTips

### フィルター機能を試す

コラム一覧取得のクエリパラメータを変更:
```
?page=1&limit=20&status=published&category=値上げ情報
```

Talend API Testerでは、URLのクエリパラメータにカーソルを合わせると、個別に有効/無効を切り替えられます。

### リクエストを複製してバリエーションを作る

1. リクエストを右クリック
2. 「**Duplicate**」を選択
3. 名前を変更（例: 「コラム作成 - 公開済み」）
4. Bodyのstatusを `"published"` に変更

### レスポンスをJSONフォーマットで見やすく

レスポンスタブで「**Pretty**」ボタンをクリックすると、JSONが整形されて表示されます。

## ⚠️ トラブルシューティング

### エラー: "Failed to fetch"

**原因**: SAM Localが起動していない

**解決策**:
```bash
sam local start-api --env-vars env.json --docker-network lambda-local
```

### エラー: "Authentication required" (401)

**原因**: トークンが設定されていないか期限切れ

**解決策**:
1. 「管理者ログイン」を再度実行
2. トークンが `access_token` 変数に保存されることを確認

### エラー: "Table does not exist"

**原因**: DynamoDBテーブルが初期化されていない

**解決策**:
```bash
./scripts/init-dynamodb.sh
./scripts/seed-data.sh
```

### DynamoDB Adminでテーブルが見えない

**原因**: Dockerコンテナが起動していない

**解決策**:
```bash
./scripts/start-local.sh
```

http://localhost:8002 でテーブルが表示されることを確認

## 📚 次のステップ

- [API Collection README](./README.md) - 詳細なドキュメント
- [Architecture](../docs/architecture.md) - アーキテクチャ設計
- [Testing Guide](../docs/testing.md) - テストガイド

## 🎯 APIテストのベストプラクティス

1. **まずログインする**: 全てのAPI呼び出しの前に認証トークンを取得
2. **順番にテストする**: 作成 → 一覧取得 → 詳細取得 → 更新 → 削除
3. **エラーケースも試す**: 存在しないID、不正なパラメータなど
4. **フィルターを活用**: status、category、searchなど様々な条件で検索
5. **レスポンスを確認**: ステータスコード、データ構造、エラーメッセージ

Happy Testing! 🚀
