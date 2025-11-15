# デプロイガイド

## 📋 前提条件

- AWS CLI がインストール済み
- AWS SAM CLI がインストール済み
- AWSアカウントの設定済み（`aws configure`）
- Python 3.12 がインストール済み

## 🚀 初回デプロイ

### 1. 依存パッケージのインストール

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. SAM ビルド

```bash
sam build
```

### 3. デプロイ（ガイド付き）

```bash
sam deploy --guided
```

以下の質問に答えます：

```
Stack Name: kaidoki-navi-api
AWS Region: ap-northeast-1
Parameter Environment: development
Parameter JWTSecretKey: [your-secret-key]  # 安全なランダム文字列を入力
Confirm changes before deploy: Y
Allow SAM CLI IAM role creation: Y
Disable rollback: N
Save arguments to configuration file: Y
SAM configuration file: samconfig.toml
SAM configuration environment: default
```

### 4. デプロイ完了

デプロイが完了すると、API エンドポイントURLが表示されます：

```
Outputs
--------
Key: ApiEndpoint
Value: https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/v1
```

このURLを控えておいてください。

## 🔄 更新デプロイ

コードを修正した後の再デプロイ：

```bash
sam build && sam deploy
```

## 🧪 テストデータの投入

### Python スクリプトで投入

`scripts/seed_data.py` を作成：

```python
import boto3
from datetime import datetime, timedelta
import random

# DynamoDBクライアント
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')

# テーブル名（環境に応じて変更）
ENVIRONMENT = 'development'
products_table = dynamodb.Table(f'kaidoki-navi-products-{ENVIRONMENT}')
price_history_table = dynamodb.Table(f'kaidoki-navi-price-history-{ENVIRONMENT}')

# テスト商品データ
products = [
    {"name": "牛乳", "category": "飲料", "basePrice": 250},
    {"name": "卵", "category": "生鮮食品", "basePrice": 200},
    {"name": "食用油", "category": "調味料", "basePrice": 350},
    {"name": "食パン", "category": "パン・シリアル", "basePrice": 180},
    {"name": "トイレットペーパー", "category": "日用品", "basePrice": 500},
    {"name": "コーラ", "category": "飲料", "basePrice": 150},
    {"name": "ポテトチップス", "category": "お菓子・おつまみ", "basePrice": 120},
    {"name": "冷凍餃子", "category": "冷蔵・冷凍", "basePrice": 280},
    {"name": "醤油", "category": "調味料", "basePrice": 200},
    {"name": "チョコレート", "category": "お菓子・おつまみ", "basePrice": 180},
]

def seed_products():
    """商品データを投入"""
    for i, product in enumerate(products):
        product_id = f"item-{i + 1}"
        current_price = int(product['basePrice'] * (0.9 + random.random() * 0.2))
        previous_price = product['basePrice']
        
        item = {
            'productId': product_id,
            'name': product['name'],
            'category': product['category'],
            'currentPrice': current_price,
            'previousPrice': previous_price,
            'shop': random.choice(['スーパーA', 'ドラッグストアB', 'コンビニC']),
            'description': f'{product["name"]}の説明',
            'imageUrl': f'https://example.com/images/{product_id}.jpg',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        products_table.put_item(Item=item)
        print(f"✓ {product['name']} を追加しました")

def seed_price_history():
    """価格履歴データを投入"""
    for i, product in enumerate(products):
        product_id = f"item-{i + 1}"
        base_price = product['basePrice']
        
        # 過去30日分の価格履歴を生成
        for days_ago in range(30, -1, -1):
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            price = int(base_price * (0.85 + random.random() * 0.3))
            
            item = {
                'productId': product_id,
                'date': date,
                'price': price,
                'shop': random.choice(['スーパーA', 'ドラッグストアB', 'コンビニC']),
                'timestamp': (datetime.now() - timedelta(days=days_ago)).isoformat()
            }
            
            price_history_table.put_item(Item=item)
        
        print(f"✓ {product['name']} の価格履歴を追加しました")

if __name__ == '__main__':
    print("テストデータを投入します...")
    seed_products()
    print("\n価格履歴を投入します...")
    seed_price_history()
    print("\n✅ テストデータの投入が完了しました！")
```

実行：

```bash
python scripts/seed_data.py
```

## 🧹 クリーンアップ

リソースを削除する場合：

```bash
sam delete
```

## 📊 動作確認

### 1. 商品一覧を取得

```bash
curl https://your-api-endpoint.amazonaws.com/v1/products
```

### 2. 商品詳細を取得

```bash
curl https://your-api-endpoint.amazonaws.com/v1/products/item-1
```

### 3. カテゴリ一覧を取得

```bash
curl https://your-api-endpoint.amazonaws.com/v1/categories
```

## 🔐 認証が必要なエンドポイントのテスト

### 1. JWTトークンを生成

Pythonで一時的なトークンを生成：

```python
import jwt
from datetime import datetime, timedelta

secret_key = "your-secret-key"  # デプロイ時に設定したキー
payload = {
    'user_id': 'test-user-1',
    'exp': datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, secret_key, algorithm='HS256')
print(token)
```

### 2. トークンを使用してAPIを呼び出し

```bash
TOKEN="your-generated-token"

# お気に入り一覧を取得
curl -H "Authorization: Bearer $TOKEN" \
  https://your-api-endpoint.amazonaws.com/v1/favorites

# お気に入りに追加
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"productId": "item-1"}' \
  https://your-api-endpoint.amazonaws.com/v1/favorites
```

## 📝 トラブルシューティング

### Lambda関数のログを確認

```bash
sam logs -n ProductsListFunction --tail
```

### DynamoDBテーブルの確認

```bash
aws dynamodb scan --table-name kaidoki-navi-products-development
```

### スタックの状態を確認

```bash
aws cloudformation describe-stacks --stack-name kaidoki-navi-api
```

## 🌐 フロントエンドとの接続

フロントエンドの `src/services/api.js` で、API_BASE_URLを更新：

```javascript
const API_BASE_URL = 'https://your-api-endpoint.amazonaws.com/v1'
```

## 📈 監視とログ

CloudWatch Logs で各Lambda関数のログを確認できます：

1. AWS Console → CloudWatch → Log groups
2. `/aws/lambda/` で始まるロググループを確認

## 💰 コスト見積もり

開発環境での想定コスト（月額）：

- Lambda: $0.20（無料枠内）
- DynamoDB: $1.25（読み取り/書き込みキャパシティ）
- API Gateway: $3.50（100万リクエスト）

**合計: 約$5/月**