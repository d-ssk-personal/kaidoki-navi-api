#!/bin/bash

# DynamoDB Admin GUIの問題を修正するクイックフィックススクリプト

echo "======================================"
echo "DynamoDB Admin GUI の修正を開始"
echo "======================================"
echo ""

# Step 1: DynamoDB Adminコンテナのログを確認
echo "📋 Step 1: ログを確認中..."
echo "-----------------------------------"
docker logs dynamodb-admin --tail 10
echo ""

# Step 2: コンテナを再起動
echo "🔄 Step 2: DynamoDB Adminを再起動中..."
echo "-----------------------------------"
docker-compose restart dynamodb-admin
echo ""

# Step 3: 起動を待つ
echo "⏳ Step 3: 起動を待機中（10秒）..."
for i in {10..1}; do
  echo -n "$i... "
  sleep 1
done
echo ""
echo ""

# Step 4: コンテナの状態を確認
echo "✅ Step 4: コンテナの状態を確認"
echo "-----------------------------------"
docker ps | grep -E "(NAMES|dynamodb)"
echo ""

# Step 5: 接続テスト
echo "🔍 Step 5: DynamoDB Local APIへの接続テスト"
echo "-----------------------------------"
if aws dynamodb list-tables --endpoint-url http://localhost:8000 --region ap-northeast-1 --no-cli-pager 2>/dev/null | head -5; then
  echo ""
  echo "✅ DynamoDB Local は正常に動作しています"
else
  echo "❌ DynamoDB Local への接続に失敗しました"
  echo "   docker-compose down && docker-compose up -d を実行してください"
  exit 1
fi
echo ""

echo "======================================"
echo "✅ 修正が完了しました"
echo "======================================"
echo ""
echo "📍 次のURLをブラウザで開いてください:"
echo ""
echo "   http://localhost:8002"
echo ""
echo "💡 ヒント:"
echo "  • ブラウザのキャッシュをクリアしてからアクセスしてください"
echo "  • Chrome の場合: Cmd+Shift+R (Mac) または Ctrl+Shift+R (Windows)"
echo "  • それでも開けない場合は、別のブラウザで試してください"
echo ""
echo "  • ポート8000 (http://localhost:8000) で400エラーが出るのは正常です"
echo "    これはDynamoDB APIエンドポイントであり、Webページではありません"
echo ""
