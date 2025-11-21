#!/bin/bash

# ローカル開発環境起動スクリプト

set -e

RESET_DATA=false

# オプション解析
while [[ $# -gt 0 ]]; do
  case $1 in
    --reset)
      RESET_DATA=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--reset]"
      echo "  --reset: DynamoDBのデータを削除して初期化します"
      exit 1
      ;;
  esac
done

echo "=================================="
echo "ローカル開発環境を起動します"
echo "=================================="
echo ""

# Dockerが起動しているか確認
if ! docker info > /dev/null 2>&1; then
  echo "❌ Dockerが起動していません。Dockerを起動してから再度実行してください。"
  exit 1
fi

# --reset オプションが指定された場合、データを削除
if [ "$RESET_DATA" = true ]; then
  echo "⚠️  データをリセットします..."
  docker-compose down -v
  echo ""
fi

# 1. Docker Composeでバックエンドサービスを起動
echo "🚀 DynamoDB Local と DynamoDB Admin を起動中..."
docker-compose up -d

# DynamoDB Localの起動を待つ
echo "⏳ DynamoDB Local の起動を待機中..."
sleep 5

# 2. DynamoDBテーブルの存在確認
ENDPOINT="http://localhost:8000"
TABLE_NAME="chirashi-kitchen-articles-local"

echo ""
echo "🔍 既存のテーブルを確認中..."

# テーブルが存在するかチェック
if aws dynamodb describe-table \
  --table-name $TABLE_NAME \
  --endpoint-url $ENDPOINT \
  --region ap-northeast-1 \
  --no-cli-pager > /dev/null 2>&1; then

  echo "✅ テーブルは既に存在します。データは保持されています。"
  echo ""
  echo "💡 ヒント: データをリセットしたい場合は以下のコマンドを実行してください:"
  echo "   ./scripts/start-local.sh --reset"

else
  # テーブルが存在しない場合のみ初期化
  echo "📦 DynamoDB テーブルを初期化中..."
  cd scripts
  sh init-dynamodb.sh
  cd ..

  # 3. テストデータを投入
  echo ""
  read -p "テストデータを投入しますか？ (y/N): " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd scripts
    sh seed-data.sh
    cd ..
  fi
fi

echo ""
echo "=================================="
echo "✅ ローカル開発環境の起動が完了しました！"
echo "=================================="
echo ""
echo "📍 サービスURL:"
echo "  - DynamoDB Local:  http://localhost:8000"
echo "  - DynamoDB Admin:  http://localhost:8002"
echo ""
echo "💾 データの永続化:"
echo "  データはDocker volumeに保存されており、コンテナを停止しても保持されます。"
echo "  データをリセットするには: ./scripts/start-local.sh --reset"
echo ""
echo "🚀 SAM Local API を起動するには:"
echo "  sam build"
echo "  sam local start-api --docker-network lambda-local --env-vars env.json --parameter-overrides file://env.json"
echo ""
echo "📌 起動後、APIは http://127.0.0.1:3000 で利用可能になります"
echo ""
echo "🛑 停止するには:"
echo "  docker-compose stop      # データを保持したまま停止"
echo "  docker-compose down      # コンテナを削除（データは保持）"
echo "  docker-compose down -v   # コンテナとデータを完全削除"
echo ""
