from telethon.tl.types import Message


class TgMessage:
    def __init__(self, message: Message):
        self.message: Message = message
