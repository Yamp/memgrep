#!/usr/bin/env python3
import sys

from fire import Fire

sys.path.extend([".", "..", "../.."])
from data.redis_db import RedisDB


from loguru import logger

from data.pg.postgre_db import PostgresDB


def load():
    logger.info("Initializing redis...")
    redis = RedisDB()
    logger.info("Initializing postgres...")
    pg = PostgresDB()

    recs = pg.get_all_recognitions()
    redis.add_recognitions(recs)

if __name__ == "__main__":
    Fire(load)
