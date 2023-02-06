FROM ubuntu:22.04 as base

ARG UID=82
ARG GID=82

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

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update

FROM base

RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get install --no-install-recommends -y python3 python3-requests pipenv curl

USER memgrep

ENV PIPENV_VENV_IN_PROJECT=true

COPY --chown=memgrep:memgrep ./Pipfile* .
RUN pipenv install --deploy

COPY . .

CMD ["pipenv", "run", "python3", "bot_api.py"]
