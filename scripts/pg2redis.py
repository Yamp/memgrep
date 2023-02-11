#!/usr/bin/env python3
import sys

sys.path.extend([".", "..", "../.."])

from fire import Fire
from loguru import logger

from data.pg.postgre_db import PostgresDB
from data.redis_db import RedisDB


def load():
    logger.info("Initializing redis...")
    redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    recs = pg.get_all_recognitions()
    print(recs)
    redis.add_recognitions(recs)

if __name__ == "__main__":
    Fire(load)
