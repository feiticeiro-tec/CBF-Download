import os
from feiticeiro_tec.config.with_dynaconf import TypeEnv
from pydantic import BaseModel


class RabbitMQ(BaseModel):
    HOST: str
    PORT: int
    VIRTUAL_HOST: str
    USER: str
    PASSWORD: str


class DemoColeta(BaseModel):
    serie: str
    ano: int
    inicio: int = 1
    fim: int = 1


class Config(TypeEnv):
    RABBITMQ: RabbitMQ
    QTD_CONSUMERS: int
    DEMO: DemoColeta = None


config = Config.load_env(
    default="DEFAULT",
    env=os.environ.get("ENV", "DEV"),
    settings_files=["settings.yml"],
)
