#!/usr/bin/env python3
import sys

import fire

sys.path.extend([".", "..", "../.."])

from data.redis_db import RedisDB, SearchRequest


def search(query: str) -> None:
    """Search for memes by text."""
    index = RedisDB()
    res = index.search(SearchRequest(query=query))
    for r in res:
        print(r)  # noqa
        print('-' * 80)  # noqa


if __name__ == "__main__":
    fire.Fire(search)
