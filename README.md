A Python project for indexing and searching memes using OCR, fuzzy search and semantic search.

# Installation

**Install Pipenv**
1. Clone this repository: `git clone https://github.com/Yamp/memgrep`
2. Navigate to the cloned repository: `cd memgrep`
3. Install dependencies from lockfile: `pipenv sync`

# Dependencies

* Redis
* Minio

# Usage

* Activate the Pipenv environment: pipenv shell
* Run the API server: python bot_api.py
* Run the scraping script: python bot_scrape.py _channel_
