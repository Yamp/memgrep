from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship

# ------------------------------------------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------------------------------------------

# Here we define our tables using SQLAlchemy ORM

class Base(DeclarativeBase):
    """Base class for all tables."""


# A table to store scraped telegram chats
class TgChat(Base):
    """This table stores scraped telegram chats.

    Fields:
    1. chat_id: int - unique chat id
    2. chat_name: str - chat name
    """
    __tablename__ = "tg_chats"
    chat_id = mapped_column(Integer, primary_key=True)
    chat_name = mapped_column(String)

    messages = relationship("TgMessage", back_populates="chat")

    def __repr__(self):
        return f"<TgChat(chat_id={self.chat_id}, chat_name={self.chat_name})>"


# A table to store scraped telegram messages
class TgMessage(Base):
    """This table stores scraped telegram messages.

    It is used to avoid scraping the same message twice.

    Fields:
    1. message_id: str - unique message id
    2. chat_id: int - unique chat id (foreign key)
    3. message_text: str - message text
    4. message_date: datetime - message date
    """

    __tablename__ = "tg_messages"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id = mapped_column(Integer)
    chat_id = mapped_column(Integer, ForeignKey("tg_chats.chat_id"))
    text = mapped_column(String)
    dt = mapped_column(DateTime)

    chat = relationship("TgChat", back_populates="messages")
    images = relationship("TgImage", back_populates="message")

    def __repr__(self):
        return (f"<"
                f"TgMessage(message_id={self.message_id}, "
                f"chat_id={self.chat_id}, "
                f"message_text={self.text}, "
                f"message_date={self.dt}"
                f")>")

    def post_link(self):
        return f"https://t.me/{self.chat.chat_name}/{self.message_id}"


class TgImage(Base):
    """This table stores scraped telegram images.

    Fields:
    1. image_id: str - unique image id
    2. message_id: str - unique message id (foreign key)
    3. image_url: str - image url
    4. image_date: datetime - image date
    """

    __tablename__ = "tg_images"
    image_id = mapped_column(Integer, primary_key=True)
    message_id = mapped_column(Integer, ForeignKey("tg_messages.id"))
    s3_url = mapped_column(String, nullable=True)

    message = relationship("TgMessage", back_populates="images")
    recognitions = relationship("Recognitions", back_populates="image")

    def __repr__(self):
        return (f"<"
                f"TgImage(image_id={self.image_id}, "
                f"message_id={self.message_id}, "
                f"image_url={self.s3_url}, "
                ")>")


class Recognitions(Base):
    """This table stores results of image recognition.

    It has one-to-one relationship with TgImage table.
    It stores extracted information from images.
    Each used extractor has its own column.
    Currently supported extractors:
    1. Tesseract OCR rus
    2. Tesseract OCR eng
    3. Easy OCR
    4. BLIP-extractor
    """

    __tablename__ = "recognitions"
    image_id = mapped_column(Integer, ForeignKey("tg_images.image_id"), primary_key=True)

    tesseract_rus = mapped_column(String, nullable=True)
    tesseract_eng = mapped_column(String, nullable=True)
    easy_ocr = mapped_column(String, nullable=True)
    blip = mapped_column(String, nullable=True)

    image = relationship("TgImage", back_populates="recognitions")

    def __repr__(self):
        return (f"<"
                f"Recognitions(image_id={self.image_id}, "
                f"tesseract_ocr_rus={self.tesseract_rus}, "
                f"tesseract_ocr_eng={self.tesseract_eng}, "
                f"easy_ocr={self.easy_ocr}, blip_text={self.blip})"
                f">")
