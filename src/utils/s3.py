"""
S3画像アップロードユーティリティ
"""
import boto3
import base64
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# S3クライアントの初期化
s3_client = boto3.client('s3')


def upload_image(image_data: str, folder: str, file_extension: str = 'jpg') -> str:
    """
    Base64エンコードされた画像をS3にアップロード

    Args:
        image_data: Base64エンコードされた画像データ
        folder: S3内のフォルダ（例: 'flyers', 'articles'）
        file_extension: ファイル拡張子（デフォルト: 'jpg'）

    Returns:
        アップロードされた画像のURL

    Raises:
        ValueError: 画像データが不正な場合
        Exception: S3アップロードに失敗した場合
    """
    try:
        # Base64データをデコード
        if ',' in image_data:
            # data:image/jpeg;base64,... 形式の場合
            image_data = image_data.split(',')[1]

        image_binary = base64.b64decode(image_data)

        # ユニークなファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{folder}/{timestamp}_{unique_id}.{file_extension}"

        # S3にアップロード
        bucket_name = settings.S3_BUCKET_NAME

        content_type = f'image/{file_extension}'
        if file_extension == 'jpg':
            content_type = 'image/jpeg'

        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_binary,
            ContentType=content_type,
            CacheControl='max-age=31536000'  # 1年間キャッシュ
        )

        # URLを生成
        image_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"

        logger.info(f"Image uploaded successfully: {image_url}")
        return image_url

    except base64.binascii.Error as e:
        logger.error(f"Invalid base64 image data: {str(e)}")
        raise ValueError("Invalid image data")
    except Exception as e:
        logger.error(f"Failed to upload image to S3: {str(e)}")
        raise


def upload_multipart_image(file_content: bytes, content_type: str, folder: str) -> str:
    """
    マルチパートフォームデータの画像をS3にアップロード

    Args:
        file_content: 画像のバイトデータ
        content_type: Content-Type（例: 'image/jpeg'）
        folder: S3内のフォルダ（例: 'flyers', 'articles'）

    Returns:
        アップロードされた画像のURL

    Raises:
        Exception: S3アップロードに失敗した場合
    """
    try:
        # 拡張子を決定
        extension_map = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp'
        }
        file_extension = extension_map.get(content_type, 'jpg')

        # ユニークなファイル名を生成
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_name = f"{folder}/{timestamp}_{unique_id}.{file_extension}"

        # S3にアップロード
        bucket_name = settings.S3_BUCKET_NAME

        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content,
            ContentType=content_type,
            CacheControl='max-age=31536000'  # 1年間キャッシュ
        )

        # URLを生成
        image_url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"

        logger.info(f"Image uploaded successfully: {image_url}")
        return image_url

    except Exception as e:
        logger.error(f"Failed to upload image to S3: {str(e)}")
        raise


def delete_image(image_url: str) -> bool:
    """
    S3から画像を削除

    Args:
        image_url: 削除する画像のURL

    Returns:
        削除に成功した場合True
    """
    try:
        # URLからキーを抽出
        bucket_name = settings.S3_BUCKET_NAME

        # https://bucket-name.s3.region.amazonaws.com/path/to/file.jpg
        # から path/to/file.jpg を抽出
        if bucket_name in image_url:
            key = image_url.split(f"{bucket_name}.s3.")[1].split('/', 1)[1]
        else:
            logger.warning(f"Image URL does not match bucket: {image_url}")
            return False

        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )

        logger.info(f"Image deleted successfully: {image_url}")
        return True

    except Exception as e:
        logger.error(f"Failed to delete image from S3: {str(e)}")
        return False


def get_presigned_url(file_key: str, expiration: int = 3600) -> str:
    """
    S3オブジェクトの署名付きURLを生成

    Args:
        file_key: S3オブジェクトのキー
        expiration: URL有効期限（秒、デフォルト: 3600秒＝1時間）

    Returns:
        署名付きURL
    """
    try:
        bucket_name = settings.S3_BUCKET_NAME

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=expiration
        )

        return url

    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise
