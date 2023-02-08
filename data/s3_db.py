from io import BytesIO

import boto3
from loguru import logger


class S3DB:
    """S3DB is a class used to access S3 service.

    It provides an interface to upload and download images from our S3 storage using the boto3 library.
    """

    def __init__(
            self,
            endpoint: str,
            region: str,
            bucket: str,
            access_key: str,
            secret_key: str,
    ):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def create_bucket(self) -> bool:
        try:
            self.client.create_bucket(Bucket=self.bucket)
            return True
        except Exception:  # noqa TODO: specify exception
            logger.info(f"Bucket '{self.bucket}' already exists.")
            return False

    def check_file_exists(self, file_name: str) -> bool:
        return self.client.list_objects_v2(Bucket=self.bucket, Prefix=file_name)["KeyCount"] > 0

    def upload_file(
            self,
            name: str,
            data: bytes,
    ):
        self.client.upload_fileobj(
            BytesIO(data),
            self.bucket,
            name,
        )
        logger.info(f"File '{name}' uploaded successfully to '{self.bucket}'.")

    def get_file(self, file_name: str) -> bytes | None:
        try:
            return self.client.get_object(Bucket=self.bucket, Key=file_name)["Body"].read()
        except self.client.exceptions.NoSuchKey:
            logger.info(f"File '{file_name}' not found in '{self.bucket}'.")
            return None


if __name__ == "__main__":
    import settings

    s3_db = S3DB(
        endpoint=settings.S3_ENDPOINT,
        region=settings.S3_REGION,
        bucket=settings.S3_BUCKET,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
    )
    s3_db.create_bucket()
    s3_db.upload_file(
        name="test.txt",
        data=b"test",
    )
    logger.info(s3_db.get_file("test.txt"))
    logger.info(s3_db.check_file_exists("test.txt"))
