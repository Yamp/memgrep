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
    message_id: int
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
    """ The meme database.

    The table name is tg_memes.
    We use redis-stack as engine.
    """

    def __init__(
            self,
            redis_url: str = "redis://redis:6379",
    ):
        self.pool = redis.ConnectionPool.from_url(redis_url, db=0)
        self.redis = redis.Redis(connection_pool=self.pool)

    def create_db(self) -> bool:
        """Create a redis table to store image records.

        Table should allow search filtering fields and fuzzy full text search for text fields.
        Table is created with FT.CREATE command.
        """
        # check if table exists
        if self.redis.exists("tg_memes"):
            return False

        # create table
        self.redis.execute_command("""
        FT.CREATE tg_memes
        ON HASH
        PREFIX 1 tg_memes:
        SCHEMA
            id NUMERIC SORTABLE
            message_id NUMERIC SORTABLE
            chat TEXT SORTABLE
            sender_id NUMERIC SORTABLE
            dt NUMERIC SORTABLE
            msg_text TEXT SORTABLE
            ocr_rus TEXT SORTABLE
            ocr_eng TEXT SORTABLE
            semantic_data TEXT SORTABLE
            semantic_vector NUMERIC SORTABLE
            comments TEXT SORTABLE
            reactions TEXT SORTABLE
            data_link TEXT SORTABLE
            post_link TEXT SORTABLE
        """)
        return None

    def add_record(self, record: ImageRecord) -> bool:
        """Add a record to the table.

        if record is already in the table, return False.
        Existence is checked by id field.
        """
        if self.redis.exists(f"tg_memes:{record.id}"):
            return False

        self.redis.execute_command(
            "HSET",
            f"tg_memes:{record.id}",
            "id", record.id,
            "message_id", record.message_id,
            "chat", record.chat,
            "sender_id", record.sender_id,
            "dt", record.dt.timestamp(),
            "msg_text", record.msg_text,
            "ocr_rus", record.ocr_rus,
            "ocr_eng", record.ocr_eng,
            "semantic_data", record.semantic_data,
            "semantic_vector", *record.semantic_vector,
            "comments", *record.comments,
            "reactions", *record.reactions,
            "data_link", record.data_link,
            "post_link", record.post_link,
        )
        return True

    def search(self, request: SearchRequest) -> list[ImageRecord]:
        """Search memes in the table.

        Our request requires filtering messages by fields (if not None)
        1. dt_start
        2. dt_end
        3. chats
        4. senders

        Fuzzy matching by fields
        1. ocr_rus
        2. ocr_eng
        3. semantic_data

        The results are sorted by the fuzzy match quality

        """
        self.redis.execute_command(
            "FT.SEARCH tg_memes"
            f"@ocr_rus:{request.query}"
            f"@ocr_eng:{request.query}"
            f"@semantic_data:{request.query}"
            f"@dt:[{request.dt_start.timestamp()} {request.dt_end.timestamp()}]"
            f"@chat:{request.chats}"
            f"@sender_id:{request.senders}"
            f"LIMIT 0 {request.max_results}"
            f"SORTBY 1 @dt DESC",
        )
