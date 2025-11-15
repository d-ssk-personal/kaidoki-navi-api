"""
共通定数定義
"""
from enum import Enum


class SortOrder(str, Enum):
    """ソート順"""
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    UPDATED_DESC = "updated_desc"


class NotificationFrequency(str, Enum):
    """通知頻度"""
    REALTIME = "realtime"
    MORNING = "morning"
    EVENING = "evening"


class ContactCategory(str, Enum):
    """お問い合わせカテゴリ"""
    SERVICE = "service"
    TECHNICAL = "technical"
    PRIVACY = "privacy"
    OTHER = "other"


class HTTPStatus:
    """HTTPステータスコード"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


class ErrorCode(str, Enum):
    """エラーコード"""
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


# カテゴリ一覧（初期データ）
CATEGORIES = [
    {"id": "cat-1", "name": "飲料", "displayOrder": 1},
    {"id": "cat-2", "name": "お菓子・おつまみ", "displayOrder": 2},
    {"id": "cat-3", "name": "生鮮食品", "displayOrder": 3},
    {"id": "cat-4", "name": "冷蔵・冷凍", "displayOrder": 4},
    {"id": "cat-5", "name": "調味料", "displayOrder": 5},
    {"id": "cat-6", "name": "パン・シリアル", "displayOrder": 6},
    {"id": "cat-7", "name": "日用品", "displayOrder": 7},
    {"id": "cat-8", "name": "その他", "displayOrder": 8},
]

# 価格履歴取得可能日数
PRICE_HISTORY_DAYS = [7, 30, 60, 90, 180]