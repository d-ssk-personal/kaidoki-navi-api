"""
ローカル開発用HTTPサーバー
Lambda関数をHTTPエンドポイントとして公開
"""
from flask import Flask, request, jsonify
import json
import os
import sys

# パスを追加
sys.path.insert(0, os.path.dirname(__file__))

# Lambda関数ハンドラーをインポート
from handlers import products, categories, favorites, notifications, contact

app = Flask(__name__)


def create_lambda_event(method, path, path_params=None, query_params=None, body=None, headers=None):
    """
    Flask RequestからLambdaイベントを生成
    """
    return {
        'httpMethod': method,
        'path': path,
        'pathParameters': path_params or {},
        'queryStringParameters': query_params or {},
        'headers': headers or {},
        'body': body
    }


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({'status': 'ok'})


# 商品API
@app.route('/products', methods=['GET'])
def list_products():
    """商品一覧取得"""
    event = create_lambda_event(
        'GET', 
        '/products',
        query_params=dict(request.args),
        headers=dict(request.headers)
    )
    response = products.list_products(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """商品詳細取得"""
    event = create_lambda_event(
        'GET',
        f'/products/{product_id}',
        path_params={'productId': product_id},
        headers=dict(request.headers)
    )
    response = products.get_product(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/products/<product_id>/price-history', methods=['GET'])
def get_price_history(product_id):
    """価格履歴取得"""
    event = create_lambda_event(
        'GET',
        f'/products/{product_id}/price-history',
        path_params={'productId': product_id},
        query_params=dict(request.args),
        headers=dict(request.headers)
    )
    response = products.get_price_history(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


# カテゴリAPI
@app.route('/categories', methods=['GET'])
def list_categories():
    """カテゴリ一覧取得"""
    event = create_lambda_event('GET', '/categories', headers=dict(request.headers))
    response = categories.list_categories(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


# お気に入りAPI
@app.route('/favorites', methods=['GET'])
def list_favorites():
    """お気に入り一覧取得"""
    event = create_lambda_event('GET', '/favorites', headers=dict(request.headers))
    response = favorites.list_favorites(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/favorites', methods=['POST'])
def add_favorite():
    """お気に入り追加"""
    event = create_lambda_event(
        'POST',
        '/favorites',
        body=request.get_data(as_text=True),
        headers=dict(request.headers)
    )
    response = favorites.add_favorite(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/favorites/<product_id>', methods=['DELETE'])
def remove_favorite(product_id):
    """お気に入り削除"""
    event = create_lambda_event(
        'DELETE',
        f'/favorites/{product_id}',
        path_params={'productId': product_id},
        headers=dict(request.headers)
    )
    response = favorites.remove_favorite(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


# 通知設定API
@app.route('/notifications/settings', methods=['GET'])
def get_notification_settings():
    """通知設定取得"""
    event = create_lambda_event('GET', '/notifications/settings', headers=dict(request.headers))
    response = notifications.get_notification_settings(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/notifications/settings', methods=['PUT'])
def update_notification_settings():
    """通知設定更新"""
    event = create_lambda_event(
        'PUT',
        '/notifications/settings',
        body=request.get_data(as_text=True),
        headers=dict(request.headers)
    )
    response = notifications.update_notification_settings(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/notifications/line/connect', methods=['POST'])
def connect_line():
    """LINE連携"""
    event = create_lambda_event(
        'POST',
        '/notifications/line/connect',
        body=request.get_data(as_text=True),
        headers=dict(request.headers)
    )
    response = notifications.connect_line(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


@app.route('/notifications/line/disconnect', methods=['POST'])
def disconnect_line():
    """LINE連携解除"""
    event = create_lambda_event(
        'POST',
        '/notifications/line/disconnect',
        headers=dict(request.headers)
    )
    response = notifications.disconnect_line(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


# お問い合わせAPI
@app.route('/contact', methods=['POST'])
def submit_contact():
    """お問い合わせ送信"""
    event = create_lambda_event(
        'POST',
        '/contact',
        body=request.get_data(as_text=True),
        headers=dict(request.headers)
    )
    response = contact.submit_contact(event, None)
    return (
        json.loads(response['body']),
        response['statusCode'],
        response['headers']
    )


if __name__ == '__main__':
    # CORS対応
    from flask_cors import CORS
    CORS(app)
    
    # サーバー起動
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)