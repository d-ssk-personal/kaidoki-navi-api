"""
バリデーションユーティリティ
"""
import re
from typing import List, Dict, Any, Optional

from common.constants import SortOrder, NotificationFrequency, ContactCategory, PRICE_HISTORY_DAYS
from config.settings import settings


class ValidationError(Exception):
    """バリデーションエラー"""
    def __init__(self, details: List[Dict[str, str]]):
        self.details = details
        super().__init__("Validation error")


def validate_email(email: str) -> bool:
    """
    メールアドレスの形式を検証
    
    Args:
        email: メールアドレス
    
    Returns:
        有効な場合True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_pagination(limit: Optional[int], offset: Optional[int]) -> tuple[int, int]:
    """
    ページネーションパラメータを検証
    
    Args:
        limit: 取得件数
        offset: 取得開始位置
    
    Returns:
        検証済みの(limit, offset)
    
    Raises:
        ValidationError: バリデーションエラー
    """
    errors = []
    
    # デフォルト値の設定
    if limit is None:
        limit = settings.DEFAULT_PAGE_LIMIT
    if offset is None:
        offset = 0
    
    # limit の検証
    try:
        limit = int(limit)
        if limit < 1:
            errors.append({"field": "limit", "message": "1以上の値を指定してください"})
        elif limit > settings.MAX_PAGE_LIMIT:
            errors.append({"field": "limit", "message": f"{settings.MAX_PAGE_LIMIT}以下の値を指定してください"})
    except (ValueError, TypeError):
        errors.append({"field": "limit", "message": "数値を指定してください"})
    
    # offset の検証
    try:
        offset = int(offset)
        if offset < 0:
            errors.append({"field": "offset", "message": "0以上の値を指定してください"})
    except (ValueError, TypeError):
        errors.append({"field": "offset", "message": "数値を指定してください"})
    
    if errors:
        raise ValidationError(errors)
    
    return limit, offset


def validate_sort_order(sort: Optional[str]) -> str:
    """
    ソート順を検証
    
    Args:
        sort: ソート順
    
    Returns:
        検証済みのソート順
    
    Raises:
        ValidationError: バリデーションエラー
    """
    if sort is None:
        return SortOrder.UPDATED_DESC
    
    try:
        return SortOrder(sort)
    except ValueError:
        valid_values = [s.value for s in SortOrder]
        raise ValidationError([{
            "field": "sort",
            "message": f"有効な値: {', '.join(valid_values)}"
        }])


def validate_price_history_days(days: Optional[int]) -> int:
    """
    価格履歴取得日数を検証
    
    Args:
        days: 日数
    
    Returns:
        検証済みの日数
    
    Raises:
        ValidationError: バリデーションエラー
    """
    if days is None:
        return settings.PRICE_HISTORY_DEFAULT_DAYS
    
    try:
        days = int(days)
        if days not in PRICE_HISTORY_DAYS:
            raise ValidationError([{
                "field": "days",
                "message": f"有効な値: {', '.join(map(str, PRICE_HISTORY_DAYS))}"
            }])
        return days
    except ValueError:
        raise ValidationError([{
            "field": "days",
            "message": "数値を指定してください"
        }])


def validate_notification_settings(data: Dict[str, Any]) -> None:
    """
    通知設定を検証
    
    Args:
        data: 通知設定データ
    
    Raises:
        ValidationError: バリデーションエラー
    """
    errors = []
    
    # frequency の検証
    if 'frequency' in data:
        try:
            NotificationFrequency(data['frequency'])
        except ValueError:
            valid_values = [f.value for f in NotificationFrequency]
            errors.append({
                "field": "frequency",
                "message": f"有効な値: {', '.join(valid_values)}"
            })
    
    # priceChangeThreshold の検証
    if 'priceChangeThreshold' in data:
        try:
            threshold = int(data['priceChangeThreshold'])
            if threshold < 1 or threshold > 100:
                errors.append({
                    "field": "priceChangeThreshold",
                    "message": "1〜100の範囲で指定してください"
                })
        except (ValueError, TypeError):
            errors.append({
                "field": "priceChangeThreshold",
                "message": "数値を指定してください"
            })
    
    # categories の検証
    if 'categories' in data:
        if not isinstance(data['categories'], list):
            errors.append({
                "field": "categories",
                "message": "配列で指定してください"
            })
    
    if errors:
        raise ValidationError(errors)


def validate_contact_form(data: Dict[str, Any]) -> None:
    """
    お問い合わせフォームを検証
    
    Args:
        data: お問い合わせデータ
    
    Raises:
        ValidationError: バリデーションエラー
    """
    errors = []
    
    # 必須項目チェック
    required_fields = ['name', 'email', 'category', 'message']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append({
                "field": field,
                "message": "必須項目です"
            })
    
    # メールアドレスの検証
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            errors.append({
                "field": "email",
                "message": "メールアドレスの形式が不正です"
            })
    
    # カテゴリの検証
    if 'category' in data and data['category']:
        try:
            ContactCategory(data['category'])
        except ValueError:
            valid_values = [c.value for c in ContactCategory]
            errors.append({
                "field": "category",
                "message": f"有効な値: {', '.join(valid_values)}"
            })
    
    # メッセージの長さチェック
    if 'message' in data and data['message']:
        if len(data['message']) > 5000:
            errors.append({
                "field": "message",
                "message": "5000文字以内で入力してください"
            })
    
    if errors:
        raise ValidationError(errors)