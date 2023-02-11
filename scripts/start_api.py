#!/usr/bin/env python3

import sys

from loguru import logger

sys.path.extend([".", "..", "../.."])

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import settings

# from data.minio_db import MinioDB
from data.redis_db import RedisDB, SearchRequest

index = RedisDB()
# storage = MinioDB()


async def search_memes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Search matching memes in the database and return the bot respons text."""
    req = update.message.text.removeprefix("/search ")

    logger.info(f"Looking for {req}")
    msgs = index.search(SearchRequest(
        query=req,
    ))

    res = [m.post_link for m in msgs]

    await update.message.reply_text(f"Hello {res}")


# async def index_memes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Index a chat."""
#     scraper = TelegramScraper(storage, index)
#     await scraper.scrape_messages(update.message.text)
#     await update.message.reply_text(f"Hello {update.effective_user.first_name}")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Hello {update.effective_user.first_name}")


def main():
    app = ApplicationBuilder().token(settings.TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("search", search_memes))
    # app.add_handler(CommandHandler("index", index_memes))
    app.run_polling()


if __name__ == "__main__":
    main()
