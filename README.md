A Python project for indexing and searching memes using OCR, fuzzy search and semantic search.

# Installation (ubuntu)
0. Install rust `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
1. Install python 3.10 `sudo apt install python3.10-full`
2. Install pytesseract deps: `sudo apt install libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-rus  tesseract-ocr-eng tesseract-ocr-script-latn tesseract-ocr-script-cyrl`
3. Create new venv and activate it: `python3.10 -m venv venv && source venv/bin/activate`
4. Install requirements: `pip3 install -r requirements.txt`

## Poetry (TBD)
**

## Dependencies

* Redis
* Minio


# Usage

* Activate environment: TBD
* Run the API server: python bot_api.py
* Run the scraping script: python bot_scrape.py _channel_
