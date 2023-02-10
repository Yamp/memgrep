from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel
from telethon.tl.types import Channel, Message

if TYPE_CHECKING:
    from data.pg.postgre_db import TgMessage


class PChat(BaseModel):
    id: int
    name: str


class PMessage(BaseModel):
    id: int
    text: str | None
    date: datetime.datetime
    message_id: int
    chat: PChat | None

    @classmethod
    def from_tg(
            cls,
            message: Message,
            channel: Channel,
    ):
        chat = PChat(id=channel.id, name=channel.username)

        return cls(
            id=message.id,
            text=message.text,
            date=message.date,
            message_id=message.id,
            chat=chat,
        )

    @classmethod
    def from_sa(cls, message: TgMessage):
        return cls(
            id=message.message_id,
            text=message.text,
            date=message.dt,
            message_id=message.message_id,
            chat=PChat(id=message.chat.chat_id, name=message.chat.chat_name),
        )


class PImage(BaseModel):
    id: int
    data: bytes
    extension: Literal["jpg", "png"]
    msg: PMessage | None = None
    num: int = 0
