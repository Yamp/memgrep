from __future__ import annotations

import json
from datetime import datetime

import redis
from loguru import logger
from pydantic import BaseModel
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.query import Query

import settings
from data.pg.models import Recognitions


class SearchRequest(BaseModel):
    query: str
    dt_start: datetime  = None
    dt_end: datetime  = None
    chats: list[str]  = None
    senders: list[str] = None

    # search options
    max_results: int = 5


class ImageRecord(BaseModel):
    id: int

    # basic info
    message_id: int
    chat: str
    sender_id: int = None
    dt: datetime = None
    msg_text: str = None

    # deep features
    ocr_rus: str = None
    ocr_eng: str = None
    semantic_data: str = None
    # semantic_vector: list[float] = None

    # additional info
    comments: list[str] = []
    reactions: list[str] = []

    # links
    data_link: str = None
    post_link: str


class RedisDB:
    """ The meme database.

    The table name is tg_memes.
    We use redis-stack as engine.
    """

    def __init__(
            self,
            redis_url: str = settings.REDIS_URL,
    ):
        self.pool = redis.ConnectionPool.from_url(redis_url, decode_responses=True)
        self.redis = redis.Redis(connection_pool=self.pool, encoding="utf-8", decode_responses=True)

    def create_db(self) -> bool:
        """Create a redis table to store image records.

        Table should allow search filtering fields and fuzzy full text search for text fields.
        Table is created with FT.CREATE command.
        """
        # check if table exists
        try:
            self.redis.execute_command("FT.INFO tg_memes")
            return False
        except redis.ResponseError:
            logger.info("Index database created for the first time.")

        # self.redis.execute_command("""
        # FT.CREATE myIdx
        # ON HASH
        # PREFIX 1 doc:
        # SCHEMA
        #  title TEXT WEIGHT 5.0
        #   body TEXT url TEXT
        # """)

        # create table
        # self.redis.execute_command("""
        self.redis.ft("tg_memes").create_index(
            fields=[
                NumericField("id", sortable=True),
                NumericField("message_id", sortable=True),
                NumericField("sender_id", sortable=True),
                NumericField("dt", sortable=True),
                TextField("chat", sortable=True),
                TextField("msg_text", sortable=True),
                TextField("blip", sortable=True),
                TextField("easy_ocr", sortable=True),
            ],
        )
        # FT.CREATE tg_memes
        # ON HASH
        # PREFIX 1 doc:
        # SCHEMA
        #     message_id NUMERIC SORTABLE
        #     chat TEXT SORTABLE
        #     sender_id NUMERIC SORTABLE
        #     dt NUMERIC SORTABLE
        #     msg_text TEXT SORTABLE
        #     ocr_rus TEXT SORTABLE
        # """)

        #             ocr_eng TEXT SORTABLE
        #             semantic_data TEXT SORTABLE
        #             semantic_vector NUMERIC SORTABLE
        #             comments TEXT SORTABLE
        #             reactions TEXT SORTABLE
        #             data_link TEXT SORTABLE
        #             post_link TEXT SORTABLE

        return None

    def add_record(self, record: ImageRecord) -> bool:
        """Add a record to the table.

        if record is already in the table, return False.
        Existence is checked by id field.
        """
        if self.redis.exists(f"tg_memes:{record.id}"):
            return False

        d = record.dict()
        d["dt"] = d["dt"].timestamp()
        # d["semantic_vector"] = ",".join(map(str, d["semantic_vector"]))
        d["comments"] = ",".join(d["comments"])
        d["reactions"] = ",".join(d["reactions"])
        d["msg_text"] = d["msg_text"] or "None"
        self.redis.hset(
            f"doc:{record.id}",
            mapping=d,
        )

        # cmd = f"""
        # HSET doc:{record.id}
        #     message_id {record.message_id}
        #     chat {record.chat}
        #     sender_id {record.sender_id}
        #     dt {record.dt.timestamp()}
        #     msg_text "{record.msg_text or 'None'}"
        #     ocr_rus "{record.ocr_rus}"
        #     ocr_eng "{record.ocr_eng}"
        #     semantic_data "{record.semantic_data}"
        #     semantic_vector "{record.semantic_vector}"
        #     comments "{record.comments}"
        #     reactions "{record.reactions}"
        #     data_link "{record.data_link}"
        #     post_link "{record.post_link}"
        # """
        # logger.info(cmd)
        # try:
        #     self.redis.execute_command(cmd)
        # except redis.ResponseError as e:
        #
        #     logger.error(e)
        #     logger.error(record)
        #     logger.error(cmd)
        #     return False
        #             dt {record.dt.timestamp()}
        #             msg_text {record.msg_text}
        #             ocr_rus {record.ocr_rus}
        #             ocr_eng {record.ocr_eng}
        #             semantic_data {record.semantic_data}
        #             semantic_vector {record.semantic_vector}
        #             comments {record.comments}
        #             reactions {record.reactions}
        #             data_link {record.data_link}
        #             post_link {record.post_link}
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
        res = self.redis.ft("tg_memes").search(Query(
            f"@easy_ocr:{request.query} | @blip:{request.query}",
        ))

        # res = self.redis.execute_command(
        #     "FT.SEARCH tg_memes\n"  # noqa
        #     + f"@ocr_rus:'{request.query}'\n"
        #     # + f"@ocr_eng:'{request.query}'\n"
        #     # + f"@semantic_data:'{request.query}'\n"
        #     # + f"@dt:[{request.dt_start.timestamp()} {request.dt_end.timestamp()}]\n"
        #     # + f"@chat:{request.chats}\n"
        #     # + f"@sender_id:{request.senders}\n"
        #     + f"LIMIT 0 {request.max_results}\n",
        #     # f"SORTBY 1 @dt DESC",
        # )

        # assert res[0] == (len(res) - 1) / 2

        records = []
        for doc in res.docs:
            d = doc.__dict__  # noqa
            # d["semantic_vector"] = parse_list(getattr(d, "semantic_vector", [])) ,
            d["reactions"] = parse_list(getattr(d, "reactions", []))
            d["comments"] = parse_list(getattr(d, "comments", []))
            d["id"] = int(d["id"].removeprefix("doc:"))
            records += [ImageRecord(**d)]

        return records

    def add_recognitions(self, recs: list[Recognitions]):
        """Add recognitions to the table."""
        for rec in recs:
            img = rec.image
            self.redis.hset(f"doc:{rec.image_id}", mapping={
                "message_id": img.message_id,
                "chat": img.message.chat.chat_id,
                "post_link": img.message.post_link(),
                # "ocr_rus": rec.tesseract_rus,
                # "ocr_eng": rec.tesseract_eng,
                "easy_ocr": rec.easy_ocr,
                "blip": rec.blip,
            })
        return

def parse_list(s: str):
    return json.loads(s) if s else []
