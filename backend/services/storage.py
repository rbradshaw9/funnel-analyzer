"""Storage service abstraction for persisting assets to object storage (S3/R2/Supabase)."""

from __future__ import annotations

import asyncio
import base64
import logging
import mimetypes
import uuid
from dataclasses import dataclass
from typing import Optional

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover - optional dependency during local dev
    boto3 = None  # type: ignore[assignment]
    BotoCoreError = ClientError = Exception  # type: ignore[assignment]

from ..utils.config import settings

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    bucket: str
    region: Optional[str]
    endpoint_url: Optional[str]
    base_url: Optional[str]
    public_expiry_seconds: int


class StorageService:
    """Handles uploads of binary assets to an S3-compatible bucket."""

    def __init__(self, config: StorageConfig, access_key: str, secret_key: str) -> None:
        self._config = config
        session_kwargs: dict = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
        }
        if config.region:
            session_kwargs["region_name"] = config.region
        if config.endpoint_url:
            session_kwargs["endpoint_url"] = config.endpoint_url

        self._client = boto3.client("s3", **session_kwargs)

    async def upload_base64_image(
        self,
        *,
        base64_data: str,
        content_type: str = "image/png",
        prefix: str = "screenshots/",
    ) -> Optional[str]:
        """Upload a base64 encoded image and return a public URL if available."""

        if not base64_data:
            return None

        try:
            binary = base64.b64decode(base64_data)
        except Exception as exc:  # noqa: BLE001 - handle decoding issues explicitly
            logger.error("Failed to decode screenshot base64 payload: %s", exc)
            return None

        extension = mimetypes.guess_extension(content_type) or ".png"
        key = f"{prefix}{uuid.uuid4().hex}{extension}"

        loop = asyncio.get_running_loop()

        try:
            await loop.run_in_executor(None, self._put_object_sync, key, binary, content_type)
        except Exception as exc:  # noqa: BLE001 - ensure upload errors are logged
            logger.error("Screenshot upload error: %s", exc)
            return None

        return self._build_public_url(key)

    def _put_object_sync(self, key: str, body: bytes, content_type: str) -> None:
        try:
            self._client.put_object(
                Bucket=self._config.bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
                ACL="public-read",
            )
        except (ClientError, BotoCoreError) as exc:  # noqa: BLE001
            logger.error("S3 sync upload failed for %s: %s", key, exc)
            raise

    def _build_public_url(self, key: str) -> Optional[str]:
        base_url = self._config.base_url
        if base_url:
            return f"{base_url.rstrip('/')}/{key}"

        if self._config.endpoint_url:
            return f"{self._config.endpoint_url.rstrip('/')}/{self._config.bucket}/{key}"

        if self._config.region:
            return f"https://{self._config.bucket}.s3.{self._config.region}.amazonaws.com/{key}"

        # Fallback to standard AWS global endpoint (not recommended for production)
        return f"https://{self._config.bucket}.s3.amazonaws.com/{key}"


_storage_service: Optional[StorageService] = None


def get_storage_service() -> Optional[StorageService]:
    """Return a singleton storage service if S3 credentials are configured."""
    global _storage_service

    if _storage_service is not None:
        return _storage_service

    if boto3 is None:
        logger.info("boto3 not installed. Screenshot uploads disabled.")
        return None

    if not settings.AWS_S3_BUCKET or not settings.AWS_S3_ACCESS_KEY_ID or not settings.AWS_S3_SECRET_ACCESS_KEY:
        logger.info("S3 storage not configured. Screenshot uploads disabled.")
        return None

    config = StorageConfig(
        bucket=settings.AWS_S3_BUCKET,
        region=settings.AWS_S3_REGION,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        base_url=settings.AWS_S3_BASE_URL,
        public_expiry_seconds=settings.AWS_S3_PUBLIC_URL_EXPIRY_SECONDS,
    )

    _storage_service = StorageService(
        config=config,
        access_key=settings.AWS_S3_ACCESS_KEY_ID,
        secret_key=settings.AWS_S3_SECRET_ACCESS_KEY,
    )

    logger.info("Initialized S3 storage service for bucket %s", config.bucket)
    return _storage_service


def cleanup_storage_service() -> None:
    """Reset the singleton (useful for tests)."""
    global _storage_service
    _storage_service = None
