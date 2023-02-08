import datetime
from typing import Literal

from pydantic import BaseModel
from telethon.tl.types import Message

from data.postgre_db import TgMessage


class PChat(BaseModel):
    id: int
    name: str


class PMessage(BaseModel):
    id: int
    text: str
    date: datetime.datetime
    message_id: int
    chat: PChat

    @classmethod
    def from_tg(cls, message: Message):
        return cls(
            id=message.message_id,
            text=message.text,
            date=message.date,
            message_id=message.message_id,
            chat=message.chat,
        )

    @classmethod
    def from_sa(cls, message: TgMessage):
        return cls(
            id=message.message_id,
            text=message.text,
            date=message.dt,
            message_id=message.message_id,
            chat=PChat(id=message.chat.id, name=message.chat.name),
        )


class PImage(BaseModel):
    id: int
    data: bytes
    extension: Literal["jpg", "png"]
    msg: PMessage | None = None
