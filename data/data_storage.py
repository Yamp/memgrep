from loguru import logger

from data.postgre_db import PostgresDB
from data.redis_db import RedisDB
from data.s3_db import S3DB
from entities.message import PImage, PMessage


class DataStorage:
    """Combined data storage.

    This class contains all the baking data engines. It is used to provide public interface for all the data.
    It abstracts out the data storage engines from the rest of the code and provides an effective implementations
    of the most common operations.

    It guarantees that all the data is consistent.
    """

    def __init__(
            self,
            s3: S3DB,
            index: RedisDB,
            pg_db: PostgresDB,
    ):
        self.s3: S3DB = s3
        self.index: RedisDB = index
        self.pg_db: PostgresDB = pg_db

        if self.index.create_db():
            logger.info("Index database created for the first time.")

        if self.pg_db.create_db():
            logger.info("Postgres database created for the first time.")

    def save_messages(self, msgs: list[PMessage]) -> None:
        """Get image from the storage."""
        return self.pg_db.add_messages(msgs)

    def save_images(self, imgs: list[PImage]) -> None:
        """Get image from the storage."""
        return self.pg_db.add_images(imgs)

    def upload_image(self, img: PImage) -> None:
        """Upload image to the storage."""
        self.s3.upload_file(
            f"{img.msg.chat.id}/{img.msg.id}/{img.num}.{img.extension}",
            img.data,
        )

    def download_image(self, img: PImage) -> bytes:
        """Download image from the storage."""
        return self.s3.download_file(f"{img.msg.chat.id}/{img.msg.id}/{img.num}.{img.extension}")

    # def get_unrecognized_images(self) -> list[PImage]:
    #     """Get image from the storage."""
    #     return self.index.get_unrecognized_images()
