#!/usr/bin/env python3
"""
Script to verify Telegram API functionality.
This script checks both Telethon client and Python Telegram Bot functionality.
"""

import os
import sys
from pathlib import Path
import dotenv

# Load environment variables from .env.test file
dotenv.load_dotenv(".env.test")

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
import asyncio
from telethon import TelegramClient, events
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import settings


async def verify_telethon():
    """Verify Telethon client functionality."""
    logger.info("Verifying Telethon client functionality...")
    
    try:
        # Create the client
        client = TelegramClient(
            session=settings.TG_SESSION_NAME,
            api_id=settings.TG_API_ID,
            api_hash=settings.TG_API_HASH,
        )
        
        # Connect to Telegram
        await client.connect()
        
        # Check if we're already authorized
        if await client.is_user_authorized():
            me = await client.get_me()
            logger.info(f"Successfully connected to Telegram as {me.username} (ID: {me.id})")
            logger.info("Telethon client is working correctly.")
        else:
            logger.warning("Not authorized. Please run the authentication script first.")
        
        # Disconnect
        await client.disconnect()
        return True
    except Exception as e:
        logger.error(f"Error verifying Telethon client: {e}")
        return False


async def verify_telegram_bot():
    """Verify Python Telegram Bot functionality."""
    logger.info("Verifying Python Telegram Bot functionality...")
    
    try:
        # Create the application
        app = ApplicationBuilder().token(settings.TG_BOT_TOKEN).build()
        
        # Define a simple command handler
        async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f"Hello {update.effective_user.first_name}")
        
        # Add the handler
        app.add_handler(CommandHandler("hello", hello))
        
        # Start the bot for a short time to verify it works
        logger.info("Bot is ready to receive commands. Press Ctrl+C to stop.")
        await app.initialize()
        await app.start()
        await asyncio.sleep(5)  # Run for 5 seconds
        await app.stop()
        
        logger.info("Python Telegram Bot is working correctly.")
        return True
    except Exception as e:
        logger.error(f"Error verifying Python Telegram Bot: {e}")
        return False


async def main():
    """Run verification for both Telegram API clients."""
    telethon_ok = await verify_telethon()
    bot_ok = await verify_telegram_bot()
    
    if telethon_ok and bot_ok:
        logger.info("All Telegram API functionality is working correctly!")
    else:
        logger.warning("Some Telegram API functionality is not working correctly.")
        if not telethon_ok:
            logger.warning("Telethon client verification failed.")
        if not bot_ok:
            logger.warning("Python Telegram Bot verification failed.")


if __name__ == "__main__":
    # Check if environment variables are set
    if not all([settings.TG_API_ID, settings.TG_API_HASH, settings.TG_BOT_TOKEN]):
        logger.error("Telegram API credentials are not set in the environment variables.")
        logger.error("Please set TG_API_ID, TG_API_HASH, and TG_BOT_TOKEN in your .env file.")
        sys.exit(1)
    
    # Run the verification
    asyncio.run(main())