FROM python:3.10

WORKDIR /var/www/memgrep

RUN apt-get update && apt-get install -y libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-rus  tesseract-ocr-eng tesseract-ocr-script-latn tesseract-ocr-script-cyrl

RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "scripts/start_api.py"]
