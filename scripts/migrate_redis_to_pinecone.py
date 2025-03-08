#!/usr/bin/env python3
"""
Script to migrate data from Redis to Pinecone.
This script helps users migrate their existing meme data from Redis to Pinecone.
"""

import os
import sys
from pathlib import Path
import argparse
from tqdm import tqdm

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
import settings
from data.redis_db import RedisDB, ImageRecord
from data.pinecone_db import PineconeDB


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate data from Redis to Pinecone")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to migrate in each batch",
    )
    parser.add_argument(
        "--redis-host",
        type=str,
        default=settings.REDIS_HOST,
        help="Redis host",
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        default=settings.REDIS_PORT,
        help="Redis port",
    )
    parser.add_argument(
        "--redis-db",
        type=int,
        default=settings.REDIS_DB,
        help="Redis database number",
    )
    parser.add_argument(
        "--pinecone-api-key",
        type=str,
        default=os.environ.get("PINECONE_API_KEY", ""),
        help="Pinecone API key",
    )
    parser.add_argument(
        "--pinecone-environment",
        type=str,
        default=os.environ.get("PINECONE_ENVIRONMENT", ""),
        help="Pinecone environment",
    )
    parser.add_argument(
        "--pinecone-index",
        type=str,
        default=os.environ.get("PINECONE_INDEX", "tg_memes"),
        help="Pinecone index name",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually migrating data",
    )
    return parser.parse_args()


def main():
    """Main function to migrate data from Redis to Pinecone."""
    args = parse_args()
    
    # Check if Pinecone API key and environment are provided
    if not args.pinecone_api_key or not args.pinecone_environment:
        logger.error("Pinecone API key and environment must be provided")
        logger.error("You can set them using the --pinecone-api-key and --pinecone-environment arguments")
        logger.error("Or by setting the PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables")
        sys.exit(1)
    
    # Initialize Redis and Pinecone clients
    redis_db = RedisDB(
        host=args.redis_host,
        port=args.redis_port,
        db=args.redis_db,
    )
    
    pinecone_db = PineconeDB(
        api_key=args.pinecone_api_key,
        environment=args.pinecone_environment,
        index_name=args.pinecone_index,
    )
    
    # Check if Pinecone index exists, create it if it doesn't
    if not args.dry_run:
        pinecone_db.create_db()
    
    # Get all keys from Redis
    all_keys = redis_db.redis.keys("img:*")
    logger.info(f"Found {len(all_keys)} records in Redis")
    
    if args.dry_run:
        logger.info("Dry run mode, not actually migrating data")
        logger.info(f"Would migrate {len(all_keys)} records from Redis to Pinecone")
        return
    
    # Migrate data in batches
    batch_size = args.batch_size
    num_batches = (len(all_keys) + batch_size - 1) // batch_size
    
    for batch_idx in tqdm(range(num_batches), desc="Migrating batches"):
        batch_start = batch_idx * batch_size
        batch_end = min(batch_start + batch_size, len(all_keys))
        batch_keys = all_keys[batch_start:batch_end]
        
        # Get records from Redis
        records = []
        for key in batch_keys:
            try:
                record_data = redis_db.redis.hgetall(key)
                if not record_data:
                    logger.warning(f"Empty record for key {key}")
                    continue
                
                # Convert Redis record to ImageRecord
                record = redis_db._decode_record(record_data)
                records.append(record)
            except Exception as e:
                logger.error(f"Error getting record for key {key}: {e}")
        
        # Add records to Pinecone
        for record in records:
            try:
                pinecone_db.add_record(record)
            except Exception as e:
                logger.error(f"Error adding record {record.id} to Pinecone: {e}")
        
        logger.info(f"Migrated batch {batch_idx + 1}/{num_batches} ({len(records)} records)")
    
    logger.info(f"Migration complete! Migrated {len(all_keys)} records from Redis to Pinecone")


if __name__ == "__main__":
    main()