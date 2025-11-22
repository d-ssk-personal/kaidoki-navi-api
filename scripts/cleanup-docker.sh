#!/bin/bash

echo "======================================"
echo "Docker環境の完全クリーンアップ"
echo "======================================"
echo ""
echo "⚠️  このスクリプトは以下を削除します:"
echo "  - すべてのDockerコンテナ"
echo "  - すべてのDockerボリューム"
echo "  - すべてのDockerネットワーク"
echo "  - ローカルのDynamoDBデータ"
echo ""
read -p "続行しますか？ (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました。"
    exit 1
fi

echo ""
echo "🧹 クリーンアップを開始します..."
echo ""

# Step 1: コンテナを停止して削除
echo "1️⃣  コンテナを停止中..."
docker-compose down 2>/dev/null || echo "  docker-compose.ymlが見つかりません（OK）"

# Step 2: 関連するコンテナを強制削除
echo ""
echo "2️⃣  関連コンテナを削除中..."
docker rm -f dynamodb-local 2>/dev/null || echo "  dynamodb-localコンテナなし（OK）"
docker rm -f dynamodb-admin 2>/dev/null || echo "  dynamodb-adminコンテナなし（OK）"

# Step 3: ボリュームを削除
echo ""
echo "3️⃣  ボリュームを削除中..."
docker volume rm kaidoki-navi-api_dynamodb-data 2>/dev/null || echo "  ボリュームなし（OK）"
docker volume prune -f

# Step 4: ネットワークを削除
echo ""
echo "4️⃣  ネットワークを削除中..."
docker network rm lambda-local 2>/dev/null || echo "  lambda-localネットワークなし（OK）"

# Step 5: 確認
echo ""
echo "5️⃣  クリーンアップ結果の確認..."
echo "-----------------------------------"
echo "残っているdynamodb関連のコンテナ:"
docker ps -a | grep dynamodb || echo "  なし（OK）"
echo ""
echo "残っているボリューム:"
docker volume ls | grep dynamodb || echo "  なし（OK）"
echo ""
echo "lambda-localネットワーク:"
docker network ls | grep lambda-local || echo "  なし（OK）"

echo ""
echo "======================================"
echo "✅ クリーンアップが完了しました"
echo "======================================"
echo ""
echo "次のステップ:"
echo "  ./scripts/start-local.sh"
echo ""
