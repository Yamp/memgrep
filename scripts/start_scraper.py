#!/usr/bin/env python3
"""
Script to start the Telegram scraper.
This script starts the Telegram scraper for scraping memes from Telegram channels.
"""

import os
import sys
from pathlib import Path
import argparse
import asyncio

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
import settings
from scraper.telegram_scraper import TelegramScraper
from data.redis_db import RedisDB
from data.pinecone_db import PineconeDB
from data.minio_storage import MinioStorage


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start the Telegram scraper")
    parser.add_argument(
        "channel",
        type=str,
        help="Telegram channel to scrape",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of messages to scrape",
    )
    parser.add_argument(
        "--use-pinecone",
        action="store_true",
        help="Use Pinecone instead of Redis for vector search",
    )
    parser.add_argument(
        "--use-modern-ocr",
        action="store_true",
        help="Use modern OCR (Google Vision API and Gemini Pro Vision) for text extraction",
    )
    return parser.parse_args()


async def main():
    """Main function to start the Telegram scraper."""
    args = parse_args()
    
    # Initialize storage
    storage = MinioStorage()
    
    # Initialize database
    if args.use_pinecone:
        # Check if Pinecone API key and environment are provided
        if not os.environ.get("PINECONE_API_KEY") or not os.environ.get("PINECONE_ENVIRONMENT"):
            logger.error("Pinecone API key or environment not provided")
            logger.error("Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables")
            sys.exit(1)
        
        # Initialize Pinecone database
        db = PineconeDB()
        logger.info("Using Pinecone for vector search")
    else:
        # Initialize Redis database
        db = RedisDB()
        logger.info("Using Redis for vector search")
    
    # Initialize scraper
    scraper = TelegramScraper(
        storage=storage,
        db=db,
        use_modern_ocr=args.use_modern_ocr,
    )
    
    # Scrape messages
    logger.info(f"Scraping messages from {args.channel}")
    await scraper.scrape_messages(args.channel, limit=args.limit)
    
    logger.info(f"Finished scraping messages from {args.channel}")


if __name__ == "__main__":
    asyncio.run(main())