from celery import Celery
from . import CBFSession, CBFExtratV1, CBFExtratV2
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
        cbf = CBFSession()
        url = cbf.get_url_sumula_external(serie, ano, partida)
        file = cbf.request_download_file(url)
    except Exception as e:
        logger.error("Error ao baixar arquivo.", exception=e)
        return

    file = gzip.compress(file)
    logger.success(
        "Arquivo baixado com sucesso!",
        params={
            "serie": serie,
            "ano": ano,
            "partida": partida,
        },
    )
    return {
        "serie": serie,
        "ano": ano,
        "partida": partida,
        "file": file.decode("latin-1"),
    }


@app.task(name="cbf.parse")
def parse(file):
    try:
        file_encode = file.encode("latin-1")
        file_bytes = gzip.decompress(file_encode)
    except Exception as e:
        logger.error("Error ao descomprimir arquivo.", exception=e)
        return
    try:
        extract = CBFExtratV1(False)
        text = extract.bytes_pdf_to_text(file_bytes)
    except Exception as e:
        logger.error("Error ao converter arquivo.", exception=e)
        return
    try:
        data = extract.get_data(text)
        logger.success("Dados extraidos com sucesso!")
        return data
    except Exception as e:
        logger.error("Error ao extrair dados.", exception=e)
        return


@app.task(name="cbf.parse.v2")
def parse_v2(file):
    try:
        file_encode = file.encode("latin-1")
        file_bytes = gzip.decompress(file_encode)
    except Exception as e:
        logger.error("Error ao descomprimir arquivo.", exception=e)
        return
    try:
        extract = CBFExtratV2(False)
        text = extract.bytes_pdf_to_text(file_bytes)
    except Exception as e:
        logger.error("Error ao converter arquivo.", exception=e)
        return
    try:
        data = extract.get_coleta(text)
        logger.success("Dados extraidos com sucesso!")
        return data
    except Exception as e:
        logger.error("Error ao extrair dados.", exception=e)
        return
