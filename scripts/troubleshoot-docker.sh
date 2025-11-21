#!/bin/bash

# Docker環境トラブルシューティングスクリプト

echo "======================================"
echo "Docker環境の診断を開始します"
echo "======================================"
echo ""

# 1. Dockerコンテナの状態確認
echo "1️⃣  コンテナの状態を確認中..."
echo "-----------------------------------"
docker ps -a | grep -E "(CONTAINER|dynamodb)"
echo ""

# 2. コンテナが起動しているか確認
DYNAMODB_LOCAL_STATUS=$(docker ps --filter "name=dynamodb-local" --format "{{.Status}}")
DYNAMODB_ADMIN_STATUS=$(docker ps --filter "name=dynamodb-admin" --format "{{.Status}}")

if [ -z "$DYNAMODB_LOCAL_STATUS" ]; then
  echo "❌ dynamodb-localコンテナが起動していません"
  echo "   以下のコマンドで起動してください:"
  echo "   docker-compose up -d dynamodb-local"
  echo ""
else
  echo "✅ dynamodb-local: $DYNAMODB_LOCAL_STATUS"
  echo ""
fi

if [ -z "$DYNAMODB_ADMIN_STATUS" ]; then
  echo "❌ dynamodb-adminコンテナが起動していません"
  echo "   以下のコマンドで起動してください:"
  echo "   docker-compose up -d dynamodb-admin"
  echo ""
else
  echo "✅ dynamodb-admin: $DYNAMODB_ADMIN_STATUS"
  echo ""
fi

# 3. ポートバインディングの確認
echo "2️⃣  ポートバインディングを確認中..."
echo "-----------------------------------"
docker ps --filter "name=dynamodb" --format "table {{.Names}}\t{{.Ports}}"
echo ""

# 4. DynamoDB Localのログ確認
echo "3️⃣  DynamoDB Localのログ（最新20行）:"
echo "-----------------------------------"
docker logs dynamodb-local --tail 20
echo ""

# 5. DynamoDB Adminのログ確認
echo "4️⃣  DynamoDB Adminのログ（最新20行）:"
echo "-----------------------------------"
docker logs dynamodb-admin --tail 20
echo ""

# 6. ネットワーク確認
echo "5️⃣  Dockerネットワークを確認中..."
echo "-----------------------------------"
docker network inspect lambda-local --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null || echo "⚠️  lambda-localネットワークが存在しません"
echo ""

# 7. ポートの使用状況確認
echo "6️⃣  ポートの使用状況を確認中..."
echo "-----------------------------------"
echo "Port 8000:"
lsof -i :8000 || echo "  ポート8000は使用されていません"
echo ""
echo "Port 8002:"
lsof -i :8002 || echo "  ポート8002は使用されていません"
echo ""

# 8. DynamoDB LocalへのAPI接続テスト
echo "7️⃣  DynamoDB Local APIへの接続テスト..."
echo "-----------------------------------"
if aws dynamodb list-tables --endpoint-url http://localhost:8000 --region ap-northeast-1 --no-cli-pager 2>/dev/null; then
  echo "✅ DynamoDB Local APIは正常に動作しています"
else
  echo "❌ DynamoDB Local APIへの接続に失敗しました"
fi
echo ""

# 9. 解決策の提案
echo "======================================"
echo "📋 トラブルシューティングの結果"
echo "======================================"
echo ""
echo "💡 重要な情報:"
echo "  • ポート8000でブラウザから400エラーが出るのは正常です"
echo "    （これはDynamoDB APIエンドポイントであり、Webインターフェースではありません）"
echo ""
echo "  • DynamoDB Admin GUIはポート8002で利用できます"
echo "    アクセス先: http://localhost:8002"
echo ""
echo "🔧 問題が解決しない場合の対処法:"
echo ""
echo "  1. コンテナを完全に再起動:"
echo "     docker-compose down"
echo "     docker-compose up -d"
echo "     sleep 5"
echo ""
echo "  2. ログをリアルタイムで確認:"
echo "     docker-compose logs -f"
echo ""
echo "  3. DynamoDB Adminコンテナだけを再起動:"
echo "     docker-compose restart dynamodb-admin"
echo ""
echo "  4. ポート8002でブラウザキャッシュをクリア:"
echo "     ブラウザのキャッシュをクリアして再アクセス"
echo ""
echo "  5. 別のブラウザで試す:"
echo "     Chrome, Firefox, Safariなど別のブラウザでアクセス"
echo ""
