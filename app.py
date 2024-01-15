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

if config.DEMO:
    wk = worker.worker.WorkerCBF(
        connection=worker.get_connection(
            host=config.RABBITMQ.HOST,
            port=config.RABBITMQ.PORT,
            virtual_host=config.RABBITMQ.VIRTUAL_HOST,
            user=config.RABBITMQ.USER,
            password=config.RABBITMQ.PASSWORD,
        )
    )
    for partida in range(config.DEMO.inicio, config.DEMO.fim + 1):
        wk.publish(
            wk.QueryParams.new(
                serie=config.DEMO.serie,
                ano=config.DEMO.ano,
                partida=partida,
            )
        )

start_consuming(now=True)
