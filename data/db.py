from __future__ import annotations

from datetime import datetime

import redis
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    dt_start: datetime | None = None
    dt_end: datetime | None = None
    chats: list[str] | None = None
    senders: list[str] | None = None

    # search options
    max_results: int = 5


class ImageRecord(BaseModel):
    id: int

    # basic info
    chat: str
    sender_id: int
    dt: datetime
    msg_text: str

    # deep features
    ocr_rus: str
    ocr_eng: str
    semantic_data: str
    semantic_vector: list[float]

    # additional info
    comments: list[str]
    reactions: list[str]

    # links
    data_link: str
    post_link: str


class MemDB:
    def __init__(
            self,
            redis_url: str = "redis://redis:6379",
    ):
        self.pool = redis.ConnectionPool.from_url(redis_url, db=0)
        self.redis = redis.Redis(connection_pool=self.pool)

    def create_db(self) -> None:
        """Create a redis table to store image records.

        Table should allow search filtering fields and fuzzy full text search for text fields.
        The table name is tg_memes.
        """
        self.re

    def add_record(self, record: ImageRecord) -> None:
        pass

    def search(self, request: SearchRequest) -> list[ImageRecord]:
        pass
