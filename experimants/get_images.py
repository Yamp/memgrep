from loguru import logger

from data.data_storage import DataStorage
from data.pg.postgre_db import PostgresDB
from data.redis_db import RedisDB
from data.s3_db import S3DB

logger.info("Initializing s3...")
s3 = S3DB()
logger.info("Initializing redis...")
redis = RedisDB()
logger.info("Initializing postgres...")
pg = PostgresDB()

logger.info("Creating storage...")
storage = DataStorage(s3, redis, pg)
res = storage.get_all_images()
print(len(res))  # noqa
print(next(iter(res.values())))  # noqa
