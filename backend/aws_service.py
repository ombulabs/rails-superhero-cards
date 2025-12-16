import base64
from datetime import UTC, datetime

import boto3
from botocore.exceptions import ClientError

from .config import settings
from .logging_config import logger


class S3Service:
    def __init__(self, folder_prefix: str = settings.s3_folder_prefix):
        session_kwargs = {"region_name": settings.aws_region}

        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            session_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        # Use LocalStack endpoint in development
        if settings.aws_endpoint_url:
            session_kwargs["endpoint_url"] = settings.aws_endpoint_url
            logger.info(f"Using AWS endpoint: {settings.aws_endpoint_url}")

        self.s3_client = boto3.client("s3", **session_kwargs)
        self.bucket_name = settings.s3_bucket_name
        self.folder_prefix = folder_prefix

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.debug(f"Bucket {self.bucket_name} already exists")
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {create_error!s}")
            else:
                logger.error(f"Error checking bucket {self.bucket_name}: {e!s}")

    def upload_image(self, image_base64: str, session_id: str, content_type: str = "image/png") -> str:
        try:
            image_data = base64.b64decode(image_base64)

            timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
            object_key = f"{self.folder_prefix}/{timestamp}_{session_id}.png"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=image_data,
                ContentType=content_type,
                ACL="private",
            )

            logger.info(f"Successfully uploaded image to S3: s3://{self.bucket_name}/{object_key}")

            return object_key

        except ClientError as e:
            logger.error(f"Failed to upload image to S3: {e!s}", exc_info=True)
            raise

    def get_object_url(self, object_key: str, expiration: int = 3600) -> str:
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            logger.error(
                f"Failed to generate presigned URL for {object_key}: {e!s}",
                exc_info=True,
            )
            raise

    def get_image_base64(self, object_key: str) -> str:
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
            image_data = response["Body"].read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            logger.debug(f"Successfully retrieved image from S3: {object_key}")
            return image_base64
        except ClientError as e:
            logger.error(
                f"Failed to retrieve image from S3: {object_key}: {e!s}",
                exc_info=True,
            )
            raise

    def delete_object(self, object_key: str) -> None:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Successfully deleted object from S3: {object_key}")
        except ClientError as e:
            logger.error(
                f"Failed to delete object {object_key} from S3: {e!s}",
                exc_info=True,
            )
            raise
