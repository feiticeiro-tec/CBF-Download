import os

RESULT_EXPIRES = int(os.environ.get("RESULT_EXPIRES", 3600))  # 1 hour
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
REDIS_DB = os.environ["REDIS_DB"]
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"