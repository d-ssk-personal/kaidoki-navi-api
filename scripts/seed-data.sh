#!/bin/bash

# DynamoDB Local テストデータ投入スクリプト

ENDPOINT="http://localhost:8000"
REGION="ap-northeast-1"

echo "テストデータを投入します..."

# 管理者データの投入（パスワード: password のbcryptハッシュ）
echo "Creating admin users..."

# システム管理者
aws dynamodb put-item \
  --table-name admins \
  --item '{
    "adminId": {"S": "admin001"},
    "username": {"S": "admin"},
    "passwordHash": {"S": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqN8VqVqWu"},
    "name": {"S": "システム管理者"},
    "email": {"S": "admin@example.com"},
    "role": {"S": "system_admin"},
    "createdAt": {"S": "2025-01-01T00:00:00Z"},
    "updatedAt": {"S": "2025-01-01T00:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

# 企業管理者
aws dynamodb put-item \
  --table-name admins \
  --item '{
    "adminId": {"S": "admin002"},
    "username": {"S": "company"},
    "passwordHash": {"S": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqN8VqVqWu"},
    "name": {"S": "企業管理者"},
    "email": {"S": "company@example.com"},
    "role": {"S": "company_admin"},
    "companyId": {"S": "COMP001"},
    "companyName": {"S": "サンプル企業"},
    "createdAt": {"S": "2025-01-01T00:00:00Z"},
    "updatedAt": {"S": "2025-01-01T00:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

# 店舗ユーザー
aws dynamodb put-item \
  --table-name admins \
  --item '{
    "adminId": {"S": "admin003"},
    "username": {"S": "store"},
    "passwordHash": {"S": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqN8VqVqWu"},
    "name": {"S": "店舗ユーザー"},
    "email": {"S": "store@example.com"},
    "role": {"S": "store_user"},
    "companyId": {"S": "COMP001"},
    "companyName": {"S": "サンプル企業"},
    "storeId": {"S": "STORE001"},
    "storeName": {"S": "サンプル店舗"},
    "createdAt": {"S": "2025-01-01T00:00:00Z"},
    "updatedAt": {"S": "2025-01-01T00:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

echo "Admin users created (username/password):"
echo "  - admin/password (システム管理者)"
echo "  - company/password (企業管理者)"
echo "  - store/password (店舗ユーザー)"
echo ""

# サンプルコラムの投入
echo "Creating sample articles..."

aws dynamodb put-item \
  --table-name articles \
  --item '{
    "articleId": {"N": "1"},
    "title": {"S": "2025年1月の値上げ情報まとめ"},
    "content": {"S": "2025年1月から、食品メーカー各社が値上げを実施します。小麦粉製品を中心に、平均5-10%の値上げが予定されています。早めの買い溜めがおすすめです。"},
    "category": {"S": "値上げ情報"},
    "status": {"S": "published"},
    "images": {"L": [
      {"S": "https://example.com/image1.jpg"}
    ]},
    "tags": {"L": [
      {"S": "値上げ"},
      {"S": "食品"},
      {"S": "節約"}
    ]},
    "publishedAt": {"S": "2025-01-15T09:00:00Z"},
    "createdBy": {"S": "admin001"},
    "updatedBy": {"S": "admin001"},
    "createdAt": {"S": "2025-01-15T09:00:00Z"},
    "updatedAt": {"S": "2025-01-15T09:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

aws dynamodb put-item \
  --table-name articles \
  --item '{
    "articleId": {"N": "2"},
    "title": {"S": "今週の特売情報：スーパー各社で鶏肉が安い！"},
    "content": {"S": "今週は鶏肉が各スーパーで特売となっています。イオンでは100g 98円、イトーヨーカドーでは100g 88円と非常にお得です。この機会にまとめ買いして冷凍保存がおすすめです。"},
    "category": {"S": "特売情報"},
    "status": {"S": "published"},
    "images": {"L": [
      {"S": "https://example.com/image2.jpg"},
      {"S": "https://example.com/image3.jpg"}
    ]},
    "tags": {"L": [
      {"S": "特売"},
      {"S": "鶏肉"},
      {"S": "まとめ買い"}
    ]},
    "publishedAt": {"S": "2025-01-20T10:30:00Z"},
    "createdBy": {"S": "admin001"},
    "updatedBy": {"S": "admin001"},
    "createdAt": {"S": "2025-01-20T10:30:00Z"},
    "updatedAt": {"S": "2025-01-20T10:30:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

aws dynamodb put-item \
  --table-name articles \
  --item '{
    "articleId": {"N": "3"},
    "title": {"S": "【下書き】節約レシピ特集"},
    "content": {"S": "この記事は下書きです。まだ公開されていません。"},
    "category": {"S": "節約術"},
    "status": {"S": "draft"},
    "tags": {"L": [
      {"S": "レシピ"},
      {"S": "節約"}
    ]},
    "createdBy": {"S": "admin001"},
    "updatedBy": {"S": "admin001"},
    "createdAt": {"S": "2025-01-21T14:00:00Z"},
    "updatedAt": {"S": "2025-01-21T14:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

echo "Sample articles created"
echo ""

# 企業データの投入
echo "Creating sample company..."
aws dynamodb put-item \
  --table-name companies \
  --item '{
    "companyId": {"S": "COMP001"},
    "name": {"S": "サンプル企業"},
    "contractStatus": {"S": "active"},
    "contractPlan": {"S": "standard"},
    "createdAt": {"S": "2025-01-01T00:00:00Z"},
    "updatedAt": {"S": "2025-01-01T00:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

echo "Sample company created"
echo ""

# 店舗データの投入
echo "Creating sample store..."
aws dynamodb put-item \
  --table-name stores \
  --item '{
    "storeId": {"S": "STORE001"},
    "companyId": {"S": "COMP001"},
    "name": {"S": "サンプル店舗"},
    "prefecture": {"S": "東京都"},
    "region": {"S": "関東"},
    "address": {"S": "東京都渋谷区..."},
    "createdAt": {"S": "2025-01-01T00:00:00Z"},
    "updatedAt": {"S": "2025-01-01T00:00:00Z"}
  }' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null

echo "Sample store created"
echo ""

echo "テストデータの投入が完了しました！"
echo ""
echo "テストログイン情報:"
echo "  システム管理者: admin / password"
echo "  企業管理者: company / password"
echo "  店舗ユーザー: store / password"
