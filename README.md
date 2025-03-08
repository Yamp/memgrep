# MemGrep

A Python project for indexing and searching memes using OCR, fuzzy search, and semantic search. This project allows you to scrape memes from Telegram channels, extract text using OCR, and search for memes using text queries or semantic search.

## Features

- Scrape memes from Telegram channels
- Extract text from memes using OCR (EasyOCR, Google Vision API, or Gemini Pro Vision)
- Store memes and metadata in a vector database (Redis or Pinecone)
- Search for memes using text queries or semantic search
- API server for searching and retrieving memes

## Installation

### Using Makefile (Recommended)

The project includes a Makefile to simplify common development tasks:

```bash
# Install production dependencies
make setup

# Install development dependencies
make setup-dev

# Run the API server
make run

# Run tests
make test

# Build Docker image
make build

# Verify Telegram API functionality
make verify-telegram
```

### Using UV (Modern Python Package Manager)

The project supports UV for faster and more reliable package management:

```bash
# Install UV and set up the project
./scripts/setup_uv.sh

# Activate the virtual environment
source .venv/bin/activate
```

### Manual Installation (Ubuntu)

1. Install Rust:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. Install Python 3.10:
   ```bash
   sudo apt install python3.10-full
   ```

3. Install Tesseract OCR dependencies:
   ```bash
   sudo apt install libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-rus tesseract-ocr-eng tesseract-ocr-script-latn tesseract-ocr-script-cyrl
   ```

4. Create and activate a virtual environment:
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   ```

5. Install requirements:
   ```bash
   pip install -r requirements-uv.txt
   ```

### Using Docker

Build and run the Docker image:

```bash
# Build the Docker image
docker build -t memgrep:latest -f Dockerfile.new .

# Run the Docker container
docker run -p 5000:5000 memgrep:latest
```

## Dependencies

* Redis or Pinecone (for vector database)
* Minio (for object storage)
* Telegram API credentials (for scraping)
* Google Cloud Vision API and/or Gemini Pro Vision API keys (optional, for improved OCR)

## Configuration

Create a `.env` file in the project root with the following variables:

```
# Telegram API credentials
TG_API_ID=your_api_id
TG_API_HASH=your_api_hash
TG_BOT_TOKEN=your_bot_token
TG_SESSION_NAME=your_session_name

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Pinecone configuration (optional)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX=tg_memes

# Google API keys (optional)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json

# Minio configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_SECURE=False
```

## Usage

1. Verify Telegram API functionality:
   ```bash
   python scripts/verify_telegram_api.py
   ```

2. Run the API server:
   ```bash
   python scripts/start_api.py
   ```

3. Run the scraping script:
   ```bash
   python scripts/start_scraper.py <channel_name>
   ```

4. Migrate from Redis to Pinecone (if needed):
   ```bash
   python scripts/migrate_redis_to_pinecone.py
   ```

## Modern OCR and Vector Database

The project now supports modern OCR solutions and vector databases:

- **Modern OCR**: Uses Google Cloud Vision API and Gemini Pro Vision for improved OCR accuracy
- **Pinecone Vector Database**: Provides better vector search performance compared to Redis

To use these features, make sure to set the appropriate environment variables in your `.env` file.

## Testing

Run the tests using pytest:

```bash
pytest
```

Or using the Makefile:

```bash
make test
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
