#!/usr/bin/env python3
import fire

from data.redis_db import MemDB, SearchRequest


def search(query: str) -> None:
    """Search for memes by text."""
    index = MemDB()
    res = index.search(SearchRequest(query=query))
    for r in res:
        print(r)  # noqa
        print('-' * 80)  # noqa


if __name__ == "__main__":
    fire.Fire(search)
