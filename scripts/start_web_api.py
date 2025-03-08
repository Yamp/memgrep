#!/usr/bin/env python3
"""
Script to start the web API server.
This script starts the web API server for searching and retrieving memes.
"""

import os
import sys
from pathlib import Path
import argparse

# Add the project root to the Python path
sys.path.extend([".", "..", "../.."])

from loguru import logger
import settings
from api.app import app


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start the web API server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the server to",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the server in debug mode",
    )
    parser.add_argument(
        "--use-pinecone",
        action="store_true",
        help="Use Pinecone instead of Redis for vector search",
    )
    return parser.parse_args()


def main():
    """Main function to start the web API server."""
    args = parse_args()
    
    # Set environment variables
    if args.use_pinecone:
        os.environ["USE_PINECONE"] = "1"
        logger.info("Using Pinecone for vector search")
        
        # Check if Pinecone API key and environment are provided
        if not os.environ.get("PINECONE_API_KEY") or not os.environ.get("PINECONE_ENVIRONMENT"):
            logger.warning("Pinecone API key or environment not provided")
            logger.warning("Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables")
    
    # Start the API server
    logger.info(f"Starting web API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()