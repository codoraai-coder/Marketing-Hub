import boto3
import os
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket_name = os.getenv("AWS_S3_BUCKET", "mcp-hub-storage")
        
        self.s3_client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    async def upload_text(self, key: str, content: str) -> str:
        """Upload text content to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType="text/plain",
            )
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            logger.info(f"Uploaded text to S3: {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise

    async def upload_buffer(self, key: str, buffer: bytes, content_type: str) -> str:
        """Upload buffer (image, file) to S3"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer,
                ContentType=content_type,
            )
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            logger.info(f"Uploaded buffer to S3: {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise

    async def get_object(self, key: str) -> bytes:
        """Get object from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to get object from S3: {str(e)}")
            raise


# Singleton instance
s3_service = S3Service()
