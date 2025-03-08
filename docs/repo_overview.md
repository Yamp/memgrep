# MemGrep Repository Overview

## Project Description

MemGrep is a Python project designed for indexing and searching memes using OCR (Optical Character Recognition), fuzzy search, and semantic search capabilities. The system can scrape memes from Telegram channels, extract text from images using OCR, and provide search functionality through a Telegram bot interface.

## Architecture

The project is built with a modular architecture consisting of several key components:

1. **Data Storage Layer**
   - Redis for vector storage and search indexing
   - Minio for image storage
   - PostgreSQL for relational data storage

2. **Extraction Layer**
   - OCR processing using EasyOCR and Tesseract
   - Image captioning using BLIP (Bootstrapping Language-Image Pre-training)

3. **API Layer**
   - Telegram bot interface for searching memes
   - REST API for programmatic access

4. **Scraping Layer**
   - Telegram scraper for collecting memes from channels

## Key Components

### Data Storage

- **Redis DB (`data/redis_db.py`)**: Stores indexed meme data with search capabilities using Redis Stack
- **Minio DB (`data/minio_db.py`)**: Stores the actual image files
- **PostgreSQL DB (`data/pg/postgre_db.py`)**: Stores relational data about messages and images

### Extraction

- **OCR Extractor (`extraction/ocr.py`)**: Extracts text from images using EasyOCR and Tesseract
- **Caption Generator (`extraction/caption.py`)**: Generates image descriptions using BLIP

### API

- **Telegram Bot (`scripts/start_api.py`)**: Provides a Telegram bot interface for searching memes

### Scraping

- **Telegram Scraper (`scraper/tg.py`)**: Scrapes memes from Telegram channels

## Deployment

The project is currently deployed using Docker Compose with three main services:
1. **bot_api**: The main application container
2. **redis**: Redis Stack for search indexing
3. **minio**: Minio for image storage

## Dependencies

The project has several key dependencies:
- **Python 3.10+**
- **Redis Stack** for vector search
- **Minio** for object storage
- **Tesseract OCR** for text extraction
- **EasyOCR** for improved OCR capabilities
- **BLIP** for image captioning
- **Telethon** for Telegram API access
- **Python Telegram Bot** for the bot interface

## Configuration

Configuration is managed through environment variables defined in `.env` file:
- Telegram API credentials
- Redis connection details
- Minio/S3 connection details
- PostgreSQL connection details

## Current Limitations

1. **Complex Setup**: Requires multiple services (Redis, Minio, PostgreSQL)
2. **Dependency Management**: Uses a mix of pip, poetry, and Pipfile
3. **Testing**: Lacks comprehensive test coverage
4. **OCR Quality**: Current OCR implementation could be improved with more modern models
5. **Vector Database**: Redis may not be optimal for large-scale vector search