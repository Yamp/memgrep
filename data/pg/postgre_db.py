from __future__ import annotations

from typing import Literal

from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import settings
from data.pg.models import Base, Recognitions, TgChat, TgImage, TgMessage
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

    def use_or_create_session(
            self,
            session: Session = None,
    ) -> Session:
        """Create a session or use an existing one."""
        return session or Session(self.engine)

    def create_db(self):
        """Create all the tables in the database."""
        Base.metadata.create_all(self.engine)

    def add_messages(
            self,
            messages: list[PMessage],
            session: Session = None,
    ):
        """Add messages to the database."""
        logger.info("Adding chats and messages to the database.")
        with self.use_or_create_session(session) as session:
            chats = {}
            for message in messages:
                chat = message.chat
                if chat.id in chats:
                    continue
                chat_obj = session.query(TgChat).get(chat.id)
                if not chat_obj:
                    chat_obj = TgChat(chat_id=chat.id, chat_name=chat.name)
                    session.add(chat_obj)
                    session.flush()
                chats[chat.id] = chat_obj

            logger.info("Getting all messages in db...")
            existing_messages = session.query(TgMessage).all()
            existing_messages_ids = {message.message_id for message in existing_messages}

            logger.info("Adding messages to the database...")
            messages_to_add = [
                TgMessage(
                    message_id=message.message_id,
                    chat_id=message.chat.id,
                    text=message.text,
                    dt=message.date,
                )
                for message in messages
                if message.message_id not in existing_messages_ids
            ]
            logger.info("Bulk saving...")
            session.bulk_save_objects(messages_to_add)
            logger.info("Committing...")
            session.commit()

    def get_or_create_message(self, message: PMessage):
        with Session(self.engine) as session:
            existing_message = session.query(TgMessage).filter_by(message_id=message.message_id).first()

            if existing_message is None:
                chat = session.query(TgChat).filter_by(chat_id=message.chat.id).first()
                if chat is None:
                    chat = TgChat(chat_id=message.chat.id, chat_name=message.chat.name)
                    session.add(chat)

                tg_message = TgMessage(
                    message_id=message.message_id,
                    chat_id=message.chat.id,
                    text=message.text,
                    dt=message.date,
                )

                session.add(tg_message)
                session.commit()

    def get_or_create_chat(
            self,
            chat: PChat,
            session: Session = None,
    ):
        """Add a chat to the database if it does not exist."""
        with Session(self.engine) as session:
            session.add(TgChat(chat_id=chat.id, chat_name=chat.name))
            session.commit()

    def get_messages(self, chat_id: int) -> list[PMessage]:
        """Return a list of messages from the database."""
        logger.info("Getting messages from the database...")
        with Session(self.engine) as session:
            return [
                PMessage.from_sa(m)
                for m in session.query(TgMessage).filter(TgMessage.chat_id == chat_id).all()
            ]

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

    def add_image(self, img: PImage, url: str):
        """Add a list of images to the database."""
        with Session(self.engine) as session:
            o = TgImage(
                message_id=4000,
                image_id=img.id,
                s3_url=url,
            )
            session.add(o)
            session.commit()

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

    # def add_recognition(
    #         self,
    #         image_id: int,
    #         extractor: Literal["tesseract_rus", "tesseract_eng", "easy_ocr", "blip"],
    #         text: str,
    # ):
    #     """Add a recognition to the database."""
    #     with Session(self.engine) as session:
    #         session.execute(
    #             Recognitions.__table__.insert().values(
    #                 {
    #                     "image_id": image_id,
    #                     extractor: text,
    #                 },
    #             ),
    #         )

    def image_ids(self) -> list[int]:
        """Return a list of all images from the database."""
        with Session(self.engine) as session:
            ti = list(session.execute(select(TgImage)).scalars().all())
            return [t.image_id for t in ti]

    def add_recognition(self, img_id: int, recognition: str) -> None:
        """Add a recognition to the database."""
        with Session(self.engine) as session:
            session.add(
                Recognitions(
                    image_id=img_id,
                    blip=recognition,
                ),
            )
            session.commit()


if __name__ == "__main__":
    db = PostgresDB(
        url=settings.PG_URL,
    )
    db.create_db()
    # db.add_chats(
    #     chat_id=123,
    #     chat_name="test_chat",
    # )
