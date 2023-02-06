import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
)
# reading .env file
environ.Env.read_env()
# False if not in os.environ
DEBUG = env("DEBUG")

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
API_ID = env("API_ID")
API_HASH = env("API_HASH")
SESSION_NAME = env("SESSION_NAME")
BOT_TOKEN = env("BOT_TOKEN")

REDIS_URL = env("REDIS_URL")

MINIO_URL = env("MINIO_URL")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY")

TMP_DIR = env("TMP_DIR", default="/tmp/memgrep")
