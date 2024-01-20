from celery import Celery
from celery.exceptions import Reject
from . import CBFSession, CBFExtratV1, CBFExtratV2
from config import (
    REDIS_URL,
    RESULT_EXPIRES,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
)
from loguru import logger
import gzip
from redis import Redis
from .utils import string_to_dict, dict_to_string

db = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
)


app = Celery("cbf", broker=REDIS_URL, backend="rpc://")
app.conf.update(
    result_expires=RESULT_EXPIRES,  # 1 hour
)


def get_response_from_serie(serie, ano, partida):
    data = db.get(f"{ano}-{serie}-{partida}")
    if data:
        return string_to_dict(data)


@app.task(name="cbf.download", max_workers=3, bind=True)
def download(self, serie, ano, partida):
    if partida > 380:
        logger.error(
            "Partida não existe!",
            params={
                "serie": serie,
                "ano": ano,
                "partida": partida,
            },
        )
        raise Reject("Partida não existe!", requeue=False)
    response = get_response_from_serie(serie, ano, partida)
    if response:
        logger.success(
            "Arquivo já baixado!",
            params={
                "serie": serie,
                "ano": ano,
                "partida": partida,
            },
        )
        return response
    try:
        cbf = CBFSession()
        url = cbf.get_url_sumula_external(serie, ano, partida)
        file = cbf.request_download_file(url)
    except Exception as e:
        logger.error("Error ao baixar arquivo.", exception=e)
        raise Reject(e, requeue=False)

    file = gzip.compress(file)
    logger.success(
        "Arquivo baixado com sucesso!",
        params={
            "serie": serie,
            "ano": ano,
            "partida": partida,
        },
    )

    response = {
        "serie": serie,
        "ano": ano,
        "partida": partida,
        "file": file.decode("latin-1"),
    }

    db.set(f"{ano}-{serie}-{partida}", dict_to_string(response))
    return response


@app.task(name="cbf.parse", bind=True)
def parse(self, file):
    try:
        file_encode = file.encode("latin-1")
        file_bytes = gzip.decompress(file_encode)
    except Exception as e:
        logger.error("Error ao descomprimir arquivo.", exception=e)
        raise Reject(e, requeue=False)
    try:
        extract = CBFExtratV1(False)
        text = extract.bytes_pdf_to_text(file_bytes)
    except Exception as e:
        logger.error("Error ao converter arquivo.", exception=e)
        raise Reject(e, requeue=False)
    try:
        data = extract.get_data(text)
        logger.success("Dados extraidos com sucesso!")
        return data
    except Exception as e:
        logger.error("Error ao extrair dados.", exception=e)
        raise Reject(e, requeue=False)


@app.task(name="cbf.parse.v2", bind=True)
def parse_v2(self, file):
    try:
        file_encode = file.encode("latin-1")
        file_bytes = gzip.decompress(file_encode)
    except Exception as e:
        logger.error("Error ao descomprimir arquivo.", exception=e)
        raise Reject(e, requeue=False)
    try:
        extract = CBFExtratV2(False)
        text = extract.bytes_pdf_to_text(file_bytes)
    except Exception as e:
        logger.error("Error ao converter arquivo.", exception=e)
        raise Reject(e, requeue=False)
    try:
        data = extract.get_coleta(text)
        logger.success("Dados extraidos com sucesso!")
        return data
    except Exception as e:
        logger.error("Error ao extrair dados.", exception=e)
        raise Reject(e, requeue=False)
