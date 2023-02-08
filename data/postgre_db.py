from __future__ import annotations

from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, relationship

import settings
from entities.message import PChat, PImage, PMessage


class PostgresDB:
    """A class to work with Postgres database.

    This class stores the sqlalchemy engine and provides methods to work with it.

    In postgres we store scraped telegram chats and messages as well as a results of image information extractors..
    """

    def __init__(
            self,
            url: str = settings.PG_URL,
    ):
        self.engine = create_engine(
            url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
        )

    def create_db(self):
        """Create all the tables in the database."""
        Base.metadata.create_all(self.engine)

    def add_message(self, message: PMessage):
        """Save a message to the database."""
        with Session(self.engine) as session:
            session.execute(
                TgMessage.__table__.insert().values(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=message.text,
                    date=message.date,
                ),
            )

    def add_messages(self, messages: list[PMessage]):
        """Save a list of messages to the database."""
        with Session(self.engine) as session:
            session.execute(
                TgMessage.__table__.insert().values(
                    [
                        {
                            "chat_id": message.chat.id,
                            "message_id": message.message_id,
                            "text": message.text,
                            "date": message.date,
                        }
                        for message in messages
                    ],
                ),
            )

    def add_chats(self, chats: list[PChat]):
        """Add a list of chats to the database."""
        with Session(self.engine) as session:
            session.execute(
                TgChat.__table__.insert().values(
                    [
                        {
                            "chat_id": chat.id,
                            "chat_name": chat.name,
                        }
                        for chat in chats
                    ],
                ),
            )

    def add_images(self, images: list[PImage]):
        """Add a list of images to the database."""
        with Session(self.engine) as session:
            session.execute(
                TgImage.__table__.insert().values(
                    [
                        {
                            "message_id": image.msg.id,
                            "image_id": image.image_id,
                            "image_url": image.s3_url,
                        }
                        for image in images
                    ],
                ),
            )

    def get_unrecognized_images(
            self,
            extractor: Literal["tesseract_rus", "tesseract_eng", "easy_ocr", "blip"],
    ) -> list[TgImage]:
        """Return a list of images that have not been recognized by the specified extractor."""
        f_dict = {
            "tesseract_rus": Recognitions.tesseract_rus,
            "tesseract_eng": Recognitions.tesseract_eng,
            "easy_ocr": Recognitions.easy_ocr,
            "blip": Recognitions.blip,
        }

        with Session(self.engine) as session:
            recognitions = select(Recognitions).where(
                f_dict[extractor].is_(None),
            )
            # getting images from received recognitions
            images = select(TgImage).where(
                TgImage.image_id.in_(recognitions),
            )
            return list(session.execute(images).scalars().all())

    def get_unsaved_images(self) -> list[TgImage]:
        """Return a list of images that have not been saved to S3."""
        with Session(self.engine) as session:
            images = select(TgImage).where(
                TgImage.s3_url.is_(None),
            )
            return list(session.execute(images).scalars().all())

    def add_recognition(
            self,
            image_id: int,
            extractor: Literal["tesseract_rus", "tesseract_eng", "easy_ocr", "blip"],
            text: str,
    ):
        """Add a recognition to the database."""
        with Session(self.engine) as session:
            session.execute(
                Recognitions.__table__.insert().values(
                    {
                        "image_id": image_id,
                        extractor: text,
                    },
                ),
            )


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
    message_id = mapped_column(String, primary_key=True)
    chat_id = mapped_column(Integer, ForeignKey("tg_chats.chat_id"))
    text = mapped_column(String)
    dt = mapped_column(DateTime)

    chat = relationship("TgChat", back_populates="messages")

    def __repr__(self):
        return (f"<"
                f"TgMessage(message_id={self.message_id}, "
                f"chat_id={self.chat_id}, "
                f"message_text={self.text}, "
                f"message_date={self.dt}"
                f")>")


class TgImage(Base):
    """This table stores scraped telegram images.

    Fields:
    1. image_id: str - unique image id
    2. message_id: str - unique message id (foreign key)
    3. image_url: str - image url
    4. image_date: datetime - image date
    """

    __tablename__ = "tg_images"
    image_id = mapped_column(String, primary_key=True)
    message_id = mapped_column(String, ForeignKey("tg_messages.message_id"))
    s3_url = mapped_column(String, nullable=True)

    message = relationship("TgMessage", back_populates="images")

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
    image_id = mapped_column(String, ForeignKey("tg_images.image_id"), primary_key=True)

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


if __name__ == "__main__":
    db = PostgresDB(
        url=settings.PG_URL,
    )
    db.create_db()
    # db.add_chats(
    #     chat_id=123,
    #     chat_name="test_chat",
    # )
