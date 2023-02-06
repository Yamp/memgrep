FROM python:3.10-alpine3.16 as base

ARG UID=182
ARG GID=182

WORKDIR /usr/src/memgrep

RUN addgroup --gid ${GID} memgrep \
    && adduser \
    --disabled-password \
    --home "$(pwd)" \
    --no-create-home \
    --ingroup memgrep \
    --uid ${UID} \
    memgrep && \
    chown memgrep:memgrep /usr/src/memgrep

FROM base

RUN pip install pipenv

USER memgrep

ENV PIPENV_VENV_IN_PROJECT=true

COPY --chown=memgrep:memgrep ./Pipfile* .
RUN pipenv install --deploy

COPY . . 

CMD ["pipenv", "run", "python3", "bot_api.py"]
