#!/bin/bash

# AWSリソース削除スクリプト (MacBook用)
# 使用方法: bash scripts/destroy.sh [environment]
# 例: bash scripts/destroy.sh development

set -e

# カラー設定
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 環境を引数から取得（デフォルト: development）
ENVIRONMENT=${1:-development}

echo -e "${RED}========================================${NC}"
echo -e "${RED}  AWSリソース削除${NC}"
echo -e "${RED}  環境: ${ENVIRONMENT}${NC}"
echo -e "${RED}========================================${NC}"
echo ""

# 警告
echo -e "${YELLOW}⚠️  警告: この操作は取り消せません！${NC}"
echo ""
echo "以下のリソースが削除されます:"
echo "  - CloudFormationスタック"
echo "  - DynamoDBテーブル（データも削除されます）"
echo "  - Lambda関数"
echo "  - API Gateway"
echo "  - IAMロール"
echo ""
echo -e "${YELLOW}本当に削除しますか?${NC}"
read -p "削除する場合は 'yes' と入力してください: " confirm

if [ "$confirm" != "yes" ]; then
    echo "削除を中止しました"
    exit 0
fi
echo ""

# 設定
STACK_NAME="kaidoki-navi-api-${ENVIRONMENT}"
AWS_REGION="ap-northeast-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
S3_BUCKET="kaidoki-navi-sam-deploy-${ACCOUNT_ID}-${ENVIRONMENT}"

echo -e "${YELLOW}[1/3] CloudFormationスタックを削除中...${NC}"
echo "  スタック名: ${STACK_NAME}"
echo ""

# スタックの存在確認
if aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${AWS_REGION} &> /dev/null; then
    # スタックを削除
    aws cloudformation delete-stack \
      --stack-name ${STACK_NAME} \
      --region ${AWS_REGION}
    
    echo "  削除を開始しました。完了まで待機中..."
    
    # 削除完了を待つ
    aws cloudformation wait stack-delete-complete \
      --stack-name ${STACK_NAME} \
      --region ${AWS_REGION} 2>/dev/null || true
    
    echo -e "${GREEN}  ✓ スタック削除完了${NC}"
else
    echo -e "${YELLOW}  スタックが見つかりません（既に削除済み）${NC}"
fi
echo ""

# S3バケットの削除（オプション）
echo -e "${YELLOW}[2/3] S3バケットを削除しますか?${NC}"
echo "  バケット名: ${S3_BUCKET}"
read -p "(y/n): " delete_s3

if [ "$delete_s3" = "y" ]; then
    if aws s3 ls "s3://${S3_BUCKET}" &> /dev/null; then
        # バケット内のオブジェクトを削除
        aws s3 rm "s3://${S3_BUCKET}" --recursive --region ${AWS_REGION}
        
        # バケットを削除
        aws s3 rb "s3://${S3_BUCKET}" --region ${AWS_REGION}
        
        echo -e "${GREEN}  ✓ S3バケット削除完了${NC}"
    else
        echo -e "${YELLOW}  S3バケットが見つかりません${NC}"
    fi
else
    echo "  S3バケットは保持されます"
fi
echo ""

# 確認
echo -e "${YELLOW}[3/3] 削除状況を確認中...${NC}"

# スタックが削除されたか確認
if ! aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${AWS_REGION} &> /dev/null; then
    echo -e "${GREEN}  ✓ CloudFormationスタックは削除されました${NC}"
else
    echo -e "${YELLOW}  ⚠ CloudFormationスタックがまだ存在します${NC}"
    echo "    削除には数分かかる場合があります"
fi
echo ""

# 完了メッセージ
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ リソースの削除が完了しました${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📊 削除されたリソース:"
echo "  - CloudFormationスタック: ${STACK_NAME}"
if [ "$delete_s3" = "y" ]; then
    echo "  - S3バケット: ${S3_BUCKET}"
fi
echo ""
echo "🔍 確認方法:"
echo "  AWS Console (CloudFormation):"
echo "    https://${AWS_REGION}.console.aws.amazon.com/cloudformation/home?region=${AWS_REGION}#/stacks"
echo ""
echo "💡 再デプロイする場合:"
echo "    bash scripts/deploy.sh ${ENVIRONMENT}"
echo ""