#!/bin/bash

# SAM Local API起動スクリプト

echo "======================================"
echo "SAM Local API を起動します"
echo "======================================"
echo ""
echo "このスクリプトは以下を実行します:"
echo "  - SAM Local APIをポート3000で起動"
echo "  - DynamoDBコンテナと接続"
echo ""
echo "前提条件:"
echo "  ✓ Dockerコンテナが起動していること (./scripts/start-local.sh)"
echo "  ✓ DynamoDBテーブルが初期化されていること (./scripts/init-dynamodb.sh)"
echo ""
echo "停止するには Ctrl+C を押してください"
echo ""
echo "APIエンドポイント: http://localhost:3000"
echo ""
echo "--------------------------------------"
echo ""

# SAM Localを起動
sam local start-api --env-vars env.json --docker-network lambda-local
