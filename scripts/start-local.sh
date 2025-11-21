#!/bin/bash

# ローカル開発環境起動スクリプト

set -e

echo "=================================="
echo "ローカル開発環境を起動します"
echo "=================================="
echo ""

# Dockerが起動しているか確認
if ! docker info > /dev/null 2>&1; then
  echo "❌ Dockerが起動していません。Dockerを起動してから再度実行してください。"
  exit 1
fi

# 1. Docker Composeでバックエンドサービスを起動
echo "🚀 DynamoDB Local と DynamoDB Admin を起動中..."
docker-compose up -d

# DynamoDB Localの起動を待つ
echo "⏳ DynamoDB Local の起動を待機中..."
sleep 5

# 2. DynamoDBテーブルを初期化
echo ""
echo "📦 DynamoDB テーブルを初期化中..."
sh init-dynamodb.sh

# 3. テストデータを投入
echo ""
read -p "テストデータを投入しますか？ (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  sh seed-data.sh
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
echo "🚀 SAM Local API を起動するには:"
echo "  cd /home/user/kaidoki-navi-api"
echo "  sam build"
echo "  sam local start-api --docker-network lambda-local --env-vars env.json --parameter-overrides file://env.json"
echo ""
echo "📌 起動後、APIは http://127.0.0.1:3000 で利用可能になります"
echo ""
echo "🛑 停止するには:"
echo "  docker-compose down"
echo ""
