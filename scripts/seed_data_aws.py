#!/usr/bin/env python3
"""
AWS環境用テストデータ投入スクリプト

使用方法:
    export ENVIRONMENT=development
    python scripts/seed_data_aws.py
"""
import boto3
from datetime import datetime, timedelta
import random
import os
import sys

# 環境変数から設定を取得
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'ap-northeast-1')

print(f"環境: {ENVIRONMENT}")
print(f"リージョン: {AWS_REGION}")
print()

# DynamoDBクライアント（AWS環境用）
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# テーブル名
products_table_name = f'kaidoki-navi-products-{ENVIRONMENT}'
price_history_table_name = f'kaidoki-navi-price-history-{ENVIRONMENT}'

try:
    products_table = dynamodb.Table(products_table_name)
    price_history_table = dynamodb.Table(price_history_table_name)
    
    # テーブルが存在するか確認
    products_table.load()
    price_history_table.load()
    
    print(f"✓ テーブル接続成功")
    print(f"  - {products_table_name}")
    print(f"  - {price_history_table_name}")
    print()
except Exception as e:
    print(f"✗ テーブル接続エラー: {str(e)}")
    print()
    print("テーブルが存在しない可能性があります。")
    print("SAMデプロイが完了していることを確認してください。")
    sys.exit(1)

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
    print("商品データを投入中...")
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
            'description': f'{product["name"]}の説明文です。',
            'imageUrl': f'https://example.com/images/{product_id}.jpg',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        try:
            products_table.put_item(Item=item)
            print(f"  ✓ {product['name']} を追加しました")
        except Exception as e:
            print(f"  ✗ {product['name']} の追加に失敗: {str(e)}")

def seed_price_history():
    """価格履歴データを投入"""
    print("\n価格履歴データを投入中...")
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
            
            try:
                price_history_table.put_item(Item=item)
            except Exception as e:
                print(f"  ✗ 価格履歴の追加に失敗: {str(e)}")
                break
        
        print(f"  ✓ {product['name']} の価格履歴（31日分）を追加しました")

def main():
    print("=" * 60)
    print("AWS環境にテストデータを投入します")
    print("=" * 60)
    print()
    
    try:
        seed_products()
        seed_price_history()
        
        print("\n" + "=" * 60)
        print("✅ テストデータの投入が完了しました！")
        print("=" * 60)
        print()
        print("次のステップ:")
        print("  1. AWS ConsoleのDynamoDBで確認")
        print(f"     https://{AWS_REGION}.console.aws.amazon.com/dynamodbv2/home?region={AWS_REGION}#tables")
        print("  2. APIをテスト")
        print()
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()