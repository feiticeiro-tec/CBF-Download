from celery import Celery
from . import CBF
from config import RABBITMQ_BROKER
from loguru import logger

app = Celery("cbf", broker=RABBITMQ_BROKER, backend="rpc://")


@app.task(name="cbf.download")
def download(serie, ano, partida, reply_to):
    try:
        cbf = CBF()
        url = cbf.get_url_sumula_external(serie, ano, partida)
        file = cbf.request_download_file(url)
    except Exception as e:
        logger.error("Error ao baixar arquivo.", exception=e)
        return

    logger.success(f"File sent to {reply_to}")
    return file
