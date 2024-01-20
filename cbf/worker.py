from celery import Celery
from . import CBF
from config import RABBITMQ_BROKER, RESULT_EXPIRES
from loguru import logger
import gzip

app = Celery("cbf", broker=RABBITMQ_BROKER, backend="rpc://")
app.conf.update(
    result_expires=RESULT_EXPIRES,  # 1 hour
)


@app.task(name="cbf.download")
def download(serie, ano, partida):
    try:
        cbf = CBF()
        url = cbf.get_url_sumula_external(serie, ano, partida)
        file = cbf.request_download_file(url)
    except Exception as e:
        logger.error("Error ao baixar arquivo.", exception=e)
        return

    logger.success(
        "Arquivo baixado com sucesso!",
        params={
            "serie": serie,
            "ano": ano,
            "partida": partida,
        },
    )

    file = gzip.compress(file)
    return {
        "serie": serie,
        "ano": ano,
        "partida": partida,
        "file": file.decode("latin-1"),
    }
