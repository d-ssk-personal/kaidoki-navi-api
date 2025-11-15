#!/usr/bin/env python3
"""
開発用JWTトークン生成スクリプト

使用方法:
    python scripts/generate_token.py
    python scripts/generate_token.py --user-id test-user-123 --hours 48
"""
import sys
import os
import argparse
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# PyJWTをインポート
try:
    import jwt
except ImportError:
    print("エラー: PyJWT がインストールされていません")
    print("以下のコマンドでインストールしてください:")
    print("  pip install PyJWT")
    sys.exit(1)


def generate_token(user_id: str, secret_key: str, hours: int = 24) -> str:
    """
    JWTトークンを生成
    
    Args:
        user_id: ユーザーID
        secret_key: JWT署名用シークレットキー
        hours: トークンの有効期間（時間）
    
    Returns:
        JWTトークン文字列
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=hours),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def main():
    parser = argparse.ArgumentParser(
        description='開発用JWTトークンを生成します'
    )
    parser.add_argument(
        '--user-id',
        default='test-user-1',
        help='ユーザーID (デフォルト: test-user-1)'
    )
    parser.add_argument(
        '--secret',
        default='your-secret-key-change-in-production',
        help='JWT署名用シークレットキー'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='トークンの有効期間（時間、デフォルト: 24）'
    )
    
    args = parser.parse_args()
    
    # トークンを生成
    token = generate_token(args.user_id, args.secret, args.hours)
    
    print("=" * 80)
    print("🔑 JWT トークンを生成しました")
    print("=" * 80)
    print()
    print(f"ユーザーID: {args.user_id}")
    print(f"有効期間: {args.hours}時間")
    print()
    print("トークン:")
    print("-" * 80)
    print(token)
    print("-" * 80)
    print()
    print("使用例:")
    print()
    print("  # curlでAPIを呼び出す")
    print(f"  curl -H 'Authorization: Bearer {token}' \\")
    print("    http://localhost:3000/favorites")
    print()
    print("  # HTTPieでAPIを呼び出す")
    print(f"  http GET http://localhost:3000/favorites \\")
    print(f"    'Authorization: Bearer {token}'")
    print()


if __name__ == '__main__':
    main()