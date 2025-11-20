# Chirashi Kitchen API設計書

このディレクトリには、Chirashi KitchenのAPI設計書（OpenAPI 3.0形式）が格納されています。

## ファイル構成

- `api-design-user.yaml` - ユーザー側API設計書
- `api-design-admin.yaml` - 管理者側API設計書

## API概要

### ユーザー側API (`api-design-user.yaml`)

ユーザー向けの機能を提供するAPIです。

#### 主な機能分類

1. **チラシ関連**
   - チラシ一覧取得・検索
   - チラシ詳細表示
   - おすすめチラシ取得
   - **AIレシピ提案** (Cloud Vision API + OpenAI API)

2. **コラム関連**
   - コラム一覧取得
   - コラム詳細表示
   - 新着コラム取得

3. **マイページ関連**
   - ユーザー情報管理
   - お気に入り店舗管理（CRUD）
   - 通知設定管理

4. **商品関連**
   - 商品検索
   - 商品詳細・価格推移表示
   - AI分析レポート

5. **店舗関連**
   - 店舗検索
   - 店舗詳細表示
   - 店舗のチラシ一覧

6. **認証**
   - ユーザーログイン/ログアウト
   - ユーザー登録

### 管理者側API (`api-design-admin.yaml`)

管理者向けの管理機能を提供するAPIです。

#### 権限体系

| 権限 | 説明 | アクセス範囲 |
|------|------|-------------|
| **システム管理者** (system_admin) | 全機能へのアクセス権限 | 全リソース |
| **企業管理者** (company_admin) | 自社の管理機能 | 自社の店舗・チラシ・アカウント |
| **店舗ユーザー** (store_user) | 自店舗の管理機能 | 自店舗のチラシ・自分のアカウント |

#### 主な機能分類

1. **コラム管理** (システム管理者のみ)
   - CRUD操作
   - 一括ステータス変更
   - 一括削除

2. **企業管理** (システム管理者のみ)
   - CRUD操作
   - 契約管理
   - 一括ステータス変更

3. **店舗管理** (システム管理者・企業管理者)
   - CRUD操作
   - 権限によるデータフィルタリング

4. **チラシ管理** (全ての役割)
   - CRUD操作
   - 画像アップロード対応
   - 権限によるデータフィルタリング

5. **アカウント管理** (全ての役割)
   - CRUD操作
   - 権限管理
   - 権限によるデータフィルタリング

6. **認証**
   - 管理者ログイン

## APIパス命名規則

### 基本ルール
- 機能を先頭に配置: `/{機能名}/{操作}`
- 一覧取得: `/list`
- 追加: `/add`
- 詳細取得: `/list/{id}`
- 更新: `/update/{id}`
- 削除: `/delete/{id}`
- 一括操作: `/bulk-{操作名}`

### 例

#### 管理者側API
```
GET  /admin/articles/list              # コラム一覧取得
POST /admin/articles/add               # コラム追加
GET  /admin/articles/list/{articleId}  # コラム詳細取得
PUT  /admin/articles/update/{articleId} # コラム更新
DELETE /admin/articles/delete/{articleId} # コラム削除
PUT  /admin/articles/bulk-status       # コラム一括ステータス変更
DELETE /admin/articles/bulk-delete?articleIds=1,2,3 # コラム一括削除
```

#### ユーザー側API
```
GET  /flyers/list              # チラシ一覧取得
GET  /flyers/list/{flyerId}    # チラシ詳細取得
POST /flyers/recipe/{flyerId}  # AIレシピ提案
GET  /articles/list            # コラム一覧取得
GET  /products/list            # 商品一覧取得
```

## Swaggerでの表示方法

### オンラインエディタを使用

1. [Swagger Editor](https://editor.swagger.io/) にアクセス
2. 左側のエディタにYAMLファイルの内容を貼り付け
3. 右側にAPIドキュメントが表示されます

### VS Code拡張機能を使用

1. VS Codeに `Swagger Viewer` 拡張機能をインストール
2. YAMLファイルを開く
3. `Shift + Alt + P` でプレビューを表示

### ローカルでSwagger UIを起動

```bash
# Dockerを使用する場合
docker run -p 8080:8080 -e SWAGGER_JSON=/api/api-design-user.yaml \
  -v $(pwd):/api swaggerapi/swagger-ui

# ブラウザで http://localhost:8080 にアクセス
```

## 特記事項

### AIレシピ提案API (`POST /flyers/recipe/{flyerId}`)

このエンドポイントは以下の処理を行います：

1. **Cloud Vision API** でチラシ画像からテキスト抽出（OCR）
2. 抽出されたテキストから商品情報を解析
3. **OpenAI API** で商品に基づいたレシピを生成

**注意:** この処理には10〜30秒程度かかる場合があります。

### 権限によるデータフィルタリング

管理者側APIでは、ユーザーの権限に応じて自動的にデータがフィルタリングされます：

- **システム管理者**: すべてのデータにアクセス可能
- **企業管理者**: 自社（companyId）のデータのみアクセス可能
- **店舗ユーザー**: 自店舗（storeId）のデータのみアクセス可能

### エラーレスポンス

全てのAPIエンドポイントは以下のエラーレスポンスに対応しています：

- **400 Bad Request**: リクエストが不正
- **401 Unauthorized**: 認証が必要
- **403 Forbidden**: 権限不足
- **404 Not Found**: リソースが見つからない
- **500 Internal Server Error**: サーバー内部エラー

## 次のステップ

1. これらのYAMLファイルを確認
2. 必要に応じて修正・追加
3. APIの資産に移動
4. バックエンド実装時の参照として使用

## 変更履歴

- 2025-01-XX: APIパス命名規則を変更、500エラー追加、ログイン中の管理者情報取得API削除
  - **APIパス命名規則を変更**
    - 機能を先頭に配置: `/{機能名}/{操作}`
    - 一覧: `/list`、追加: `/add`、詳細: `/list/{id}`、更新: `/update/{id}`、削除: `/delete/{id}`
  - **500エラーレスポンスを全APIに追加**
    - 全エンドポイントで `InternalServerError` レスポンスに対応
  - **ログイン中の管理者情報取得API (`/auth/me`) を削除**
    - ログインAPIで情報を返却しているため不要
    - フロントエンドでの保持で十分
  - **「新規作成」を「追加」に統一**
    - summary を「◯◯追加」に変更
    - ユーザー登録は「登録」のまま
  - **DELETEリクエストのrequestBodyエラーを修正**
    - 一括削除APIをクエリパラメータ方式に変更

- 2024-01-XX: 管理者ログアウトAPI削除
  - フロントエンドでトークン削除により対応
  - ステートレスなJWT認証のためサーバー側の処理不要

- 2024-01-XX: 初版作成
  - ユーザー側API設計
  - 管理者側API設計
  - 権限体系の定義
