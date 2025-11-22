#!/bin/bash

# DynamoDB Local テーブル初期化スクリプト
# このファイルは自動生成されています
# 手動で編集しないでください
# 生成元: template.yaml
# 生成スクリプト: scripts/generate_init_script.py

ENDPOINT="http://localhost:8000"
REGION="ap-northeast-1"

echo "DynamoDB Localのテーブルを作成します..."
echo "(テーブル定義はtemplate.yamlから自動生成されています)"
echo ""

# Adminsテーブル
echo "Creating admins table..."
aws dynamodb create-table \
  --table-name admins \
  --attribute-definitions \
    AttributeName=adminId,AttributeType=S \
    AttributeName=username,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
    AttributeName=role,AttributeType=S \
  --key-schema AttributeName=adminId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "UsernameIndex", "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}], "Projection": {"ProjectionType": "ALL"}}, {"IndexName": "CompanyIndex", "KeySchema": [{"AttributeName": "companyId", "KeyType": "HASH"}, {"AttributeName": "role", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "admins table already exists"

# Articlesテーブル
echo "Creating articles table..."
aws dynamodb create-table \
  --table-name articles \
  --attribute-definitions \
    AttributeName=articleId,AttributeType=N \
    AttributeName=status,AttributeType=S \
    AttributeName=publishedAt,AttributeType=S \
    AttributeName=category,AttributeType=S \
  --key-schema AttributeName=articleId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "StatusIndex", "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}, {"AttributeName": "publishedAt", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}, {"IndexName": "CategoryIndex", "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}, {"AttributeName": "publishedAt", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "articles table already exists"

# Companiesテーブル
echo "Creating companies table..."
aws dynamodb create-table \
  --table-name companies \
  --attribute-definitions \
    AttributeName=companyId,AttributeType=S \
    AttributeName=contractStatus,AttributeType=S \
    AttributeName=contractPlan,AttributeType=S \
  --key-schema AttributeName=companyId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "ContractStatusIndex", "KeySchema": [{"AttributeName": "contractStatus", "KeyType": "HASH"}, {"AttributeName": "contractPlan", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "companies table already exists"

# Storesテーブル
echo "Creating stores table..."
aws dynamodb create-table \
  --table-name stores \
  --attribute-definitions \
    AttributeName=storeId,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
    AttributeName=prefecture,AttributeType=S \
    AttributeName=region,AttributeType=S \
  --key-schema AttributeName=storeId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "CompanyIndex", "KeySchema": [{"AttributeName": "companyId", "KeyType": "HASH"}, {"AttributeName": "storeId", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}, {"IndexName": "RegionIndex", "KeySchema": [{"AttributeName": "prefecture", "KeyType": "HASH"}, {"AttributeName": "region", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "stores table already exists"

# Flyersテーブル
echo "Creating flyers table..."
aws dynamodb create-table \
  --table-name flyers \
  --attribute-definitions \
    AttributeName=flyerId,AttributeType=S \
    AttributeName=storeId,AttributeType=S \
    AttributeName=validFrom,AttributeType=S \
    AttributeName=prefecture,AttributeType=S \
    AttributeName=companyId,AttributeType=S \
  --key-schema AttributeName=flyerId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "StoreIndex", "KeySchema": [{"AttributeName": "storeId", "KeyType": "HASH"}, {"AttributeName": "validFrom", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}, {"IndexName": "RegionIndex", "KeySchema": [{"AttributeName": "prefecture", "KeyType": "HASH"}, {"AttributeName": "validFrom", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}, {"IndexName": "CompanyIndex", "KeySchema": [{"AttributeName": "companyId", "KeyType": "HASH"}, {"AttributeName": "validFrom", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "flyers table already exists"

# Usersテーブル
echo "Creating users table..."
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=email,AttributeType=S \
  --key-schema AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "EmailIndex", "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "users table already exists"

# Favorite Storesテーブル
echo "Creating favorite-stores table..."
aws dynamodb create-table \
  --table-name favorite-stores \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=storeId,AttributeType=S \
  --key-schema AttributeName=userId,KeyType=HASH AttributeName=storeId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST\
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "favorite-stores table already exists"

# Recipesテーブル
echo "Creating recipes table..."
aws dynamodb create-table \
  --table-name recipes \
  --attribute-definitions \
    AttributeName=flyerId,AttributeType=S \
  --key-schema AttributeName=flyerId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST\
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "recipes table already exists"

# Shared Recipesテーブル
echo "Creating shared-recipes table..."
aws dynamodb create-table \
  --table-name shared-recipes \
  --attribute-definitions \
    AttributeName=sharedRecipeId,AttributeType=S \
    AttributeName=flyerId,AttributeType=S \
    AttributeName=sharedAt,AttributeType=S \
  --key-schema AttributeName=sharedRecipeId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    '[{"IndexName": "FlyerIndex", "KeySchema": [{"AttributeName": "flyerId", "KeyType": "HASH"}, {"AttributeName": "sharedAt", "KeyType": "RANGE"}], "Projection": {"ProjectionType": "ALL"}}]' \
  --endpoint-url $ENDPOINT \
  --region $REGION \
  --no-cli-pager 2>/dev/null || echo "shared-recipes table already exists"


echo ""
echo "テーブル一覧:"
aws dynamodb list-tables --endpoint-url $ENDPOINT --region $REGION --no-cli-pager

echo ""
echo "DynamoDB Local の初期化が完了しました！"
echo "管理UI: http://localhost:8002"
