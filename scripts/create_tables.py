#!/usr/bin/env python3
"""
DynamoDB Localにテーブルを作成するスクリプト

使用方法:
    python scripts/create_tables.py
"""
import boto3
import sys

# DynamoDB Localに接続
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='ap-northeast-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)


def create_products_table():
    """Productsテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-products-local',
            KeySchema=[
                {'AttributeName': 'productId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'productId', 'AttributeType': 'S'},
                {'AttributeName': 'category', 'AttributeType': 'S'},
                {'AttributeName': 'updatedAt', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'category-updatedAt-index',
                    'KeySchema': [
                        {'AttributeName': 'category', 'KeyType': 'HASH'},
                        {'AttributeName': 'updatedAt', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("✓ Productsテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ Productsテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-products-local')


def create_price_history_table():
    """PriceHistoryテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-price-history-local',
            KeySchema=[
                {'AttributeName': 'productId', 'KeyType': 'HASH'},
                {'AttributeName': 'date', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'productId', 'AttributeType': 'S'},
                {'AttributeName': 'date', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✓ PriceHistoryテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ PriceHistoryテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-price-history-local')


def create_users_table():
    """Usersテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-users-local',
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("✓ Usersテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ Usersテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-users-local')


def create_favorites_table():
    """Favoritesテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-favorites-local',
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'},
                {'AttributeName': 'productId', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'productId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✓ Favoritesテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ Favoritesテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-favorites-local')


def create_notification_settings_table():
    """NotificationSettingsテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-notification-settings-local',
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✓ NotificationSettingsテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ NotificationSettingsテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-notification-settings-local')


def create_categories_table():
    """Categoriesテーブルを作成"""
    try:
        table = dynamodb.create_table(
            TableName='kaidoki-navi-categories-local',
            KeySchema=[
                {'AttributeName': 'categoryId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'categoryId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✓ Categoriesテーブルを作成しました")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("⚠ Categoriesテーブルは既に存在します")
        return dynamodb.Table('kaidoki-navi-categories-local')


def main():
    print("=" * 60)
    print("DynamoDB Localにテーブルを作成します")
    print("=" * 60)
    print()
    
    # 各テーブルを作成
    create_products_table()
    create_price_history_table()
    create_users_table()
    create_favorites_table()
    create_notification_settings_table()
    create_categories_table()
    
    print()
    print("=" * 60)
    print("✅ すべてのテーブルが準備できました！")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("  1. テストデータを投入: python scripts/seed_data.py")
    print("  2. DynamoDB Admin で確認: http://localhost:8001")
    print()


if __name__ == '__main__':
    main()