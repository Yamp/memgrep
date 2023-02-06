FROM python:3.11

WORKDIR /var/www/memgrep

RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng

SHELL ["/bin/bash", "-oeu", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH=/root/.local/bin:$PATH
RUN /root/.local/bin/poetry config virtualenvs.create false

COPY poetry.lock pyproject.toml ./

RUN  /root/.local/bin/poetry install --only main --no-interaction --no-ansi --no-cache

COPY . .

CMD ["python3", "scripts/start_api.py"]
