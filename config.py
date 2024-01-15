import os
from feiticeiro_tec.config.with_dynaconf import TypeEnv
from pydantic import BaseModel


class RabbitMQ(BaseModel):
    HOST: str
    PORT: int
    VIRTUAL_HOST: str
    USER: str
    PASSWORD: str


class Config(TypeEnv):
    RABBITMQ: RabbitMQ
    QTD_CONSUMERS: int


config = Config.load_env(
    default="DEFAULT",
    env=os.environ.get("ENV", "DEV"),
    settings_files=["settings.yml"],
)
