#!/bin/bash

# DynamoDB Local テーブル初期化スクリプト

ENDPOINT="http://localhost:8000"
REGION="ap-northeast-1"

echo "DynamoDB Localのテーブルを作成します..."

# 管理者テーブル
echo "Creating Admins table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-admins \
  --attribute-definitions \
    AttributeName=adminId,AttributeType=S \
    AttributeName=username,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
    AttributeName=role,AttributeType=S \
  --key-schema AttributeName=adminId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"UsernameIndex\",
        \"KeySchema\": [{\"AttributeName\":\"username\",\"KeyType\":\"HASH\"}],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      },
      {
        \"IndexName\": \"CompanyIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"companyId\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"role\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Admins table already exists"

# コラムテーブル
echo "Creating Articles table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-articles \
  --attribute-definitions \
    AttributeName=articleId,AttributeType=N \
    AttributeName=status,AttributeType=S \
    AttributeName=publishedAt,AttributeType=S \
    AttributeName=category,AttributeType=S \
  --key-schema AttributeName=articleId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"StatusIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"status\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"publishedAt\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      },
      {
        \"IndexName\": \"CategoryIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"category\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"publishedAt\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Articles table already exists"

# 企業テーブル
echo "Creating Companies table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-companies \
  --attribute-definitions \
    AttributeName=companyId,AttributeType=S \
    AttributeName=contractStatus,AttributeType=S \
    AttributeName=contractPlan,AttributeType=S \
  --key-schema AttributeName=companyId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"ContractStatusIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"contractStatus\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"contractPlan\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Companies table already exists"

# 店舗テーブル
echo "Creating Stores table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-stores \
  --attribute-definitions \
    AttributeName=storeId,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
    AttributeName=prefecture,AttributeType=S \
    AttributeName=region,AttributeType=S \
  --key-schema AttributeName=storeId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"CompanyIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"companyId\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"storeId\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      },
      {
        \"IndexName\": \"RegionIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"prefecture\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"region\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Stores table already exists"

# チラシテーブル
echo "Creating Flyers table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-flyers \
  --attribute-definitions \
    AttributeName=flyerId,AttributeType=S \
    AttributeName=storeId,AttributeType=S \
    AttributeName=validFrom,AttributeType=S \
    AttributeName=prefecture,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
  --key-schema AttributeName=flyerId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"StoreIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"storeId\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"validFrom\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      },
      {
        \"IndexName\": \"RegionIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"prefecture\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"validFrom\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      },
      {
        \"IndexName\": \"CompanyIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"companyId\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"validFrom\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Flyers table already exists"

# ユーザーテーブル
echo "Creating Users table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=email,AttributeType=S \
  --key-schema AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"EmailIndex\",
        \"KeySchema\": [{\"AttributeName\":\"email\",\"KeyType\":\"HASH\"}],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Users table already exists"

# お気に入り店舗テーブル
echo "Creating FavoriteStores table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-favorite-stores \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=storeId,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=storeId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "FavoriteStores table already exists"

# レシピテーブル
echo "Creating Recipes table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-recipes \
  --attribute-definitions \
    AttributeName=flyerId,AttributeType=S \
  --key-schema AttributeName=flyerId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "Recipes table already exists"

# 共有レシピテーブル
echo "Creating SharedRecipes table..."
aws dynamodb create-table \
  --table-name chirashi-kitchen-shared-recipes \
  --attribute-definitions \
    AttributeName=sharedRecipeId,AttributeType=S \
    AttributeName=flyerId,AttributeType=S \
    AttributeName=sharedAt,AttributeType=S \
  --key-schema AttributeName=sharedRecipeId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[
      {
        \"IndexName\": \"FlyerIndex\",
        \"KeySchema\": [
          {\"AttributeName\":\"flyerId\",\"KeyType\":\"HASH\"},
          {\"AttributeName\":\"sharedAt\",\"KeyType\":\"RANGE\"}
        ],
        \"Projection\": {\"ProjectionType\":\"ALL\"}
      }
    ]" \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "SharedRecipes table already exists"

echo ""
echo "テーブル一覧:"
aws dynamodb list-tables --endpoint-url $ENDPOINT --region $REGION --no-cli-pager

echo ""
echo "DynamoDB Local の初期化が完了しました！"
echo "管理UI: http://localhost:8002"
