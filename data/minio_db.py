import io
from typing import Literal

from minio import Minio

import settings


class MinioDB:
    def __init__(
            self,
            url: str = settings.MINIO_URL,
            access_key: str = settings.MINIO_ACCESS_KEY,
            secret_key: str = settings.MINIO_SECRET_KEY,
    ):
        self.client = Minio(
            endpoint=url,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )

    def save_image(
            self,
            image: bytes,
            chat_id: str,
            message_id: str,
            img_num: int,
            img_type: Literal["jpg", "png"],
    ):
        if not self.client.bucket_exists(chat_id):
            self.client.make_bucket(chat_id)
            # self.client.set_bucket_policy()

        self.client.put_object(
            bucket_name=chat_id,
            object_name=f"{message_id}_{img_num}.{img_type}",
            data=io.BytesIO(image),
            length=len(image),
        )

    def get_image(
            self,
            chat_id: str,
            message_id: str,
            img_num: int,
            img_type: Literal["jpg", "png"],
    ) -> bytes | None:
        response = None
        try:
            response = self.client.get_object(
                bucket_name=chat_id,
                object_name=f"{message_id}_{img_num}.{img_type}",
            )
            return bytes(response.data)
        except Exception:  # noqa
            return None
        finally:
            if response is not None:
                response.close()
                response.release_conn()
