#!/bin/bash

set -e

echo "======================================"
echo "ローカル開発環境を起動します"
echo "======================================"
echo ""

# 環境変数
export ENDPOINT="http://localhost:8000"
export REGION="ap-northeast-1"

# Step 1: Dockerが起動しているか確認
echo "🐳 Step 1: Docker Desktop の確認..."
if ! docker info > /dev/null 2>&1; then
  echo "  ❌ Docker Desktopが起動していません"
  echo "  Docker Desktopを起動してから再度実行してください"
  exit 1
fi
echo "  ✅ Docker Desktop は起動しています"
echo ""

# Step 2: Dockerネットワークを作成（存在しない場合）
echo "📡 Step 2: Dockerネットワークを確認中..."
if ! docker network inspect lambda-local >/dev/null 2>&1; then
  echo "  ネットワークを作成します..."
  docker network create lambda-local
  echo "  ✅ lambda-localネットワークを作成しました"
else
  echo "  ✅ lambda-localネットワークは既に存在します"
fi
echo ""

# Step 3: Docker Composeでサービスを起動
echo "🚀 Step 3: DynamoDB LocalとDynamoDB Adminを起動中..."
docker-compose up -d
echo ""

# Step 4: DynamoDB Localの起動を待つ
echo "⏳ Step 4: DynamoDB Localの起動を待機中..."
echo "  （最大30秒待ちます）"
for i in {1..30}; do
  if aws dynamodb list-tables --endpoint-url $ENDPOINT --region $REGION --no-cli-pager >/dev/null 2>&1; then
    echo "  ✅ DynamoDB Localが起動しました（${i}秒）"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "  ❌ DynamoDB Localの起動がタイムアウトしました"
    echo ""
    echo "  トラブルシューティング:"
    echo "    docker logs dynamodb-local"
    echo ""
    exit 1
  fi
  sleep 1
done
echo ""

# Step 5: DynamoDB Adminの起動を待つ
echo "⏳ Step 5: DynamoDB Adminの起動を待機中..."
for i in {1..20}; do
  if curl -s http://localhost:8002 >/dev/null 2>&1; then
    echo "  ✅ DynamoDB Adminが起動しました（${i}秒）"
    break
  fi
  if [ $i -eq 20 ]; then
    echo "  ⚠️  DynamoDB Adminの起動確認がタイムアウトしました"
    echo "  バックグラウンドで起動中の可能性があります"
  fi
  sleep 1
done
echo ""

# Step 6: テーブルの初期化
echo "🗄️  Step 6: DynamoDBテーブルを確認中..."

# articlesテーブルの存在確認
if aws dynamodb describe-table --table-name chirashi-kitchen-articles --endpoint-url $ENDPOINT --region $REGION --no-cli-pager >/dev/null 2>&1; then
  echo "  ✅ テーブルは既に存在します"
else
  echo "  テーブルを作成します..."
  cd scripts
  sh init-dynamodb.sh
  cd ..
  echo "  ✅ テーブルを作成しました"
fi
echo ""

# Step 7: テストデータの投入
echo "📝 Step 7: テストデータを投入中..."
cd scripts
sh seed-data.sh
cd ..
echo ""

echo "======================================"
echo "✅ ローカル開発環境の起動が完了しました"
echo "======================================"
echo ""
echo "📍 アクセス先:"
echo "  🌐 DynamoDB Admin GUI: http://localhost:8002"
echo "     ブラウザで開いてテーブルを確認できます"
echo ""
echo "  🔌 DynamoDB API: http://localhost:8000"
echo "     （ブラウザで開くと400エラー - これは正常です）"
echo ""
echo "🔍 動作確認コマンド:"
echo "  aws dynamodb list-tables \\"
echo "    --endpoint-url http://localhost:8000 \\"
echo "    --region ap-northeast-1"
echo ""
echo "🚀 次のステップ: SAM Localを起動"
echo "  sam build"
echo "  sam local start-api \\"
echo "    --docker-network lambda-local \\"
echo "    --env-vars env.json"
echo ""
echo "  起動後 http://127.0.0.1:3000 でAPIを利用可能"
echo ""
echo "⚠️  注意:"
echo "  DynamoDBはインメモリモードで動作しています"
echo "  docker-compose downするとデータは失われます"
echo ""
echo "🛑 停止方法:"
echo "  docker-compose down"
echo ""
