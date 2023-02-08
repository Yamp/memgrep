import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
)
# reading .env file
environ.Env.read_env()
# False if not in os.environ
DEBUG = env("DEBUG")

# postgres params
PG_URL = env("PG_URL")

# s3 params
S3_ENDPOINT = env("S3_ENDPOINT")
S3_REGION = env("S3_REGION")
S3_BUCKET = env("S3_BUCKET")
S3_ACCESS_KEY = env("S3_ACCESS_KEY")
S3_SECRET_KEY = env("S3_SECRET_KEY")

# telegram params
TG_API_ID = env("TG_API_ID")
TG_API_HASH = env("TG_API_HASH")
TG_SESSION_NAME = env("TG_SESSION_NAME")
TG_BOT_TOKEN = env("TG_BOT_TOKEN")

REDIS_URL = env("REDIS_URL")

MINIO_URL = env("MINIO_URL")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY")

TMP_DIR = env("TMP_DIR", default="/tmp/memgrep")
