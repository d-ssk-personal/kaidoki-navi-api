#!/bin/bash

# AWSデプロイ自動化スクリプト (MacBook用)
# 使用方法: bash scripts/deploy.sh [environment]
# 例: bash scripts/deploy.sh development

set -e

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 環境を引数から取得（デフォルト: development）
ENVIRONMENT=${1:-development}

# 環境名のバリデーション
case $ENVIRONMENT in
  development|staging|production)
    ;;
  *)
    echo -e "${RED}✗ 無効な環境名: ${ENVIRONMENT}${NC}"
    echo "使用可能な環境: development, staging, production"
    echo "使用例: bash scripts/deploy.sh development"
    exit 1
    ;;
esac

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  買いどきナビ AWSデプロイ (MacBook)${NC}"
echo -e "${BLUE}  環境: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# AWS プロファイルの確認
if [ ! -z "$AWS_PROFILE" ]; then
    echo -e "${YELLOW}使用するAWSプロファイル: ${AWS_PROFILE}${NC}"
    echo ""
fi

# 前提条件チェック
echo -e "${YELLOW}[1/8] 前提条件をチェック中...${NC}"

# Homebrew のチェック
if ! command -v brew &> /dev/null; then
    echo -e "${RED}✗ Homebrew がインストールされていません${NC}"
    echo "以下のコマンドでインストールしてください:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi
echo -e "${GREEN}  ✓ Homebrew: インストール済み${NC}"

# AWS CLI のチェック
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}  AWS CLI がインストールされていません。インストールしますか? (y/n)${NC}"
    read -p "  " install_aws
    if [ "$install_aws" = "y" ]; then
        brew install awscli
        echo -e "${GREEN}  ✓ AWS CLI: インストール完了${NC}"
    else
        exit 1
    fi
else
    echo -e "${GREEN}  ✓ AWS CLI: $(aws --version)${NC}"
fi

# SAM CLI のチェック
if ! command -v sam &> /dev/null; then
    echo -e "${YELLOW}  SAM CLI がインストールされていません。インストールしますか? (y/n)${NC}"
    read -p "  " install_sam
    if [ "$install_sam" = "y" ]; then
        brew tap aws/tap
        brew install aws-sam-cli
        echo -e "${GREEN}  ✓ SAM CLI: インストール完了${NC}"
    else
        exit 1
    fi
else
    echo -e "${GREEN}  ✓ SAM CLI: $(sam --version)${NC}"
fi

# AWS認証情報のチェック
echo ""
echo -e "${YELLOW}AWS認証情報を確認中...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS認証情報が設定されていません${NC}"
    echo ""
    echo "以下のコマンドで設定してください:"
    echo -e "${BLUE}aws configure${NC}"
    echo ""
    echo "必要な情報:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region name: ap-northeast-1"
    echo "  - Default output format: json"
    echo ""
    read -p "今すぐ設定しますか? (y/n): " configure_now
    if [ "$configure_now" = "y" ]; then
        aws configure
    else
        exit 1
    fi
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CURRENT_USER=$(aws sts get-caller-identity --query Arn --output text)
echo -e "${GREEN}  ✓ AWS Account ID: ${ACCOUNT_ID}${NC}"
echo -e "${GREEN}  ✓ Current User: ${CURRENT_USER}${NC}"
echo ""

# 設定値の確認
echo -e "${YELLOW}[2/8] デプロイ設定を確認中...${NC}"

STACK_NAME="kaidoki-navi-api-${ENVIRONMENT}"
AWS_REGION="ap-northeast-1"
S3_BUCKET="kaidoki-navi-sam-deploy-${ACCOUNT_ID}-${ENVIRONMENT}"

echo "  スタック名: ${STACK_NAME}"
echo "  リージョン: ${AWS_REGION}"
echo "  S3バケット: ${S3_BUCKET}"
echo ""

# JWT Secret Key の生成
if [ -z "$JWT_SECRET_KEY" ]; then
    echo -e "${YELLOW}JWT Secret Key を生成中...${NC}"
    JWT_SECRET_KEY=$(openssl rand -base64 32 | tr -d '\n')
    echo -e "${GREEN}  ✓ JWT Secret Key: 生成完了${NC}"
    echo "  Key: ${JWT_SECRET_KEY:0:20}... (省略)"
else
    echo -e "${GREEN}  ✓ JWT Secret Key: 環境変数から取得${NC}"
fi
echo ""

# 確認
echo -e "${YELLOW}上記の設定でデプロイを開始しますか?${NC}"
read -p "(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "デプロイを中止しました"
    exit 0
fi
echo ""

# S3バケットの作成
echo -e "${YELLOW}[3/8] S3バケットを作成中...${NC}"
if aws s3 ls "s3://${S3_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${S3_BUCKET}" --region ${AWS_REGION}
    echo -e "${GREEN}  ✓ S3バケット作成完了: ${S3_BUCKET}${NC}"
else
    echo -e "${GREEN}  ✓ S3バケット既に存在: ${S3_BUCKET}${NC}"
fi
echo ""

# SAMビルド
echo -e "${YELLOW}[4/8] SAM アプリケーションをビルド中...${NC}"
sam build
echo -e "${GREEN}  ✓ ビルド完了${NC}"
echo ""

# SAMデプロイ
echo -e "${YELLOW}[5/8] SAM アプリケーションをデプロイ中...${NC}"
echo "  (初回デプロイは5-10分かかる場合があります)"
echo ""

sam deploy \
  --stack-name ${STACK_NAME} \
  --resolve-s3 \
  --region ${AWS_REGION} \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=${ENVIRONMENT} \
    JWTSecretKey=${JWT_SECRET_KEY} \
  --no-fail-on-empty-changeset \
  --no-confirm-changeset

echo -e "${GREEN}  ✓ デプロイ完了${NC}"
echo ""

# スタック情報の取得
echo -e "${YELLOW}[6/8] デプロイ情報を取得中...${NC}"

API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${AWS_REGION} \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

echo -e "${GREEN}  ✓ API Endpoint: ${API_ENDPOINT}${NC}"
echo ""

# DynamoDBテーブルの初期化
echo -e "${YELLOW}[7/8] DynamoDBテーブルにテストデータを投入しますか?${NC}"
read -p "(y/n): " seed_data

if [ "$seed_data" = "y" ]; then
    echo "  テストデータを投入中..."
    
    # 環境変数を設定してスクリプトを実行
    export AWS_DEFAULT_REGION=${AWS_REGION}
    export ENVIRONMENT=${ENVIRONMENT}
    
    # seed_data_aws.py を呼び出し（後で作成）
    if [ -f "scripts/seed_data_aws.py" ]; then
        python scripts/seed_data_aws.py
        echo -e "${GREEN}  ✓ テストデータ投入完了${NC}"
    else
        echo -e "${YELLOW}  ⚠ scripts/seed_data_aws.py が見つかりません${NC}"
        echo "  手動でデータを投入する場合は、AWS ConsoleのDynamoDBから操作してください"
    fi
fi
echo ""

# 疎通確認
echo -e "${YELLOW}[8/8] API疎通確認中...${NC}"

echo "  ヘルスチェックを実行..."
health_response=$(curl -s -w "\n%{http_code}" ${API_ENDPOINT}/health)
http_code=$(echo "$health_response" | tail -n1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}  ✓ ヘルスチェック成功 (HTTP 200)${NC}"
else
    echo -e "${RED}  ✗ ヘルスチェック失敗 (HTTP $http_code)${NC}"
fi

echo "  商品一覧APIを実行..."
products_response=$(curl -s -w "\n%{http_code}" ${API_ENDPOINT}/products)
http_code=$(echo "$products_response" | tail -n1)

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}  ✓ 商品一覧取得成功 (HTTP 200)${NC}"
else
    echo -e "${RED}  ✗ 商品一覧取得失敗 (HTTP $http_code)${NC}"
fi
echo ""

# 完了メッセージ
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ デプロイが完了しました！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📊 デプロイ情報:"
echo ""
echo -e "  ${BLUE}API Endpoint:${NC}"
echo "    ${API_ENDPOINT}"
echo ""
echo -e "  ${BLUE}AWS Console (CloudFormation):${NC}"
echo "    https://${AWS_REGION}.console.aws.amazon.com/cloudformation/home?region=${AWS_REGION}#/stacks"
echo ""
echo -e "  ${BLUE}AWS Console (DynamoDB):${NC}"
echo "    https://${AWS_REGION}.console.aws.amazon.com/dynamodbv2/home?region=${AWS_REGION}#tables"
echo ""
echo -e "  ${BLUE}AWS Console (Lambda):${NC}"
echo "    https://${AWS_REGION}.console.aws.amazon.com/lambda/home?region=${AWS_REGION}#/functions"
echo ""
echo "🧪 APIテスト:"
echo ""
echo "  # ヘルスチェック"
echo "  curl ${API_ENDPOINT}/health"
echo ""
echo "  # 商品一覧"
echo "  curl ${API_ENDPOINT}/products"
echo ""
echo "  # 商品詳細"
echo "  curl ${API_ENDPOINT}/products/item-1"
echo ""
echo "📝 次のステップ:"
echo ""
echo "  1. フロントエンドのAPI URLを更新"
echo "     frontend/src/services/api.js"
echo "     API_BASE_URL = '${API_ENDPOINT}'"
echo ""
echo "  2. LINE Messaging APIの設定 (オプション)"
echo "  3. OpenAI APIキーの設定 (オプション)"
echo ""
echo "🔧 設定を更新する場合:"
echo ""
echo "  sam deploy --parameter-overrides Environment=${ENVIRONMENT} JWTSecretKey=\${JWT_SECRET_KEY}"
echo ""
echo "🗑️  スタックを削除する場合:"
echo ""
echo "  aws cloudformation delete-stack --stack-name ${STACK_NAME} --region ${AWS_REGION}"
echo ""