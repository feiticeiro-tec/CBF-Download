from config import config
from cbf import worker

start_consuming = worker.init_app(
    host=config.RABBITMQ.HOST,
    port=config.RABBITMQ.PORT,
    virtual_host=config.RABBITMQ.VIRTUAL_HOST,
    user=config.RABBITMQ.USER,
    password=config.RABBITMQ.PASSWORD,
    qtd_consumers=config.QTD_CONSUMERS,
)

start_consuming(now=True)
