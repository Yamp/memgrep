from typing import Literal

from minio import Minio


class ImageDB:
    def __init__(
            self,
            url: str,
            access_key: str,
            secret_key: str,
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
        self.client.put_object(
            bucket_name=chat_id,
            object_name=f"{message_id}_{img_num}.{img_type}",
            data=image,
            length=len(image),
        )

    def get_image(
            self,
            chat_id: str,
            message_id: str,
            img_num: int,
            img_type: Literal["jpg", "png"],
    ) -> bytes:
        return self.client.get_object(
            bucket_name=chat_id,
            object_name=f"{message_id}_{img_num}.{img_type}",
        ).data
