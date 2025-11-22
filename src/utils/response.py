"""
APIレスポンス生成ユーティリティ
"""
import json
from typing import Any, Dict, Optional, List

from common.constants import HTTPStatus, ErrorCode


def success_response(
    status_code: int = HTTPStatus.OK,
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    成功レスポンスを生成
    
    Args:
        status_code: HTTPステータスコード
        body: レスポンスボディ
        headers: 追加のHTTPヘッダー
    
    Returns:
        API Gatewayのレスポンス形式
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body or {}, ensure_ascii=False, default=str)
    }


def error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[List[Dict[str, str]]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    エラーレスポンスを生成
    
    Args:
        status_code: HTTPステータスコード
        error_code: エラーコード
        message: エラーメッセージ
        details: エラー詳細
        headers: 追加のHTTPヘッダー
    
    Returns:
        API Gatewayのレスポンス形式
    """
    body = {
        'error': error_code,
        'message': message
    }
    
    if details:
        body['details'] = details
    
    return success_response(status_code=status_code, body=body, headers=headers)


def bad_request_response(message: str, details: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """400 Bad Requestレスポンス"""
    return error_response(
        status_code=HTTPStatus.BAD_REQUEST,
        error_code=ErrorCode.BAD_REQUEST,
        message=message,
        details=details
    )


def unauthorized_response(message: str = "認証が必要です") -> Dict[str, Any]:
    """401 Unauthorizedレスポンス"""
    return error_response(
        status_code=HTTPStatus.UNAUTHORIZED,
        error_code=ErrorCode.UNAUTHORIZED,
        message=message
    )


def forbidden_response(message: str = "アクセスが拒否されました") -> Dict[str, Any]:
    """403 Forbiddenレスポンス"""
    return error_response(
        status_code=HTTPStatus.FORBIDDEN,
        error_code=ErrorCode.FORBIDDEN,
        message=message
    )


def not_found_response(message: str = "リソースが見つかりません") -> Dict[str, Any]:
    """404 Not Foundレスポンス"""
    return error_response(
        status_code=HTTPStatus.NOT_FOUND,
        error_code=ErrorCode.NOT_FOUND,
        message=message
    )


def conflict_response(message: str = "リソースが既に存在します") -> Dict[str, Any]:
    """409 Conflictレスポンス"""
    return error_response(
        status_code=HTTPStatus.CONFLICT,
        error_code=ErrorCode.CONFLICT,
        message=message
    )


def internal_server_error_response(message: str = "サーバー内部でエラーが発生しました") -> Dict[str, Any]:
    """500 Internal Server Errorレスポンス"""
    return error_response(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message=message
    )


def validation_error_response(details: List[Dict[str, str]]) -> Dict[str, Any]:
    """バリデーションエラーレスポンス"""
    return error_response(
        status_code=HTTPStatus.BAD_REQUEST,
        error_code=ErrorCode.VALIDATION_ERROR,
        message="入力値が不正です",
        details=details
    )