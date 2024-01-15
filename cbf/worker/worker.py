import pika
from pydantic import BaseModel
from uuid import uuid4
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from pika.channel import Channel
from multiprocessing import Process
from loguru import logger
import gzip
from .. import CBF

blocking_scheduler = BlockingScheduler(
    timezone="America/Sao_Paulo",
    daemon=False,
)


def get_connection(host, port, virtual_host, user, password):
    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=virtual_host,
        credentials=pika.PlainCredentials(user, password),
    )
    connection = pika.BlockingConnection(parameters)
    return connection


class QueryParams(BaseModel):
    id: str
    serie: str
    ano: int
    partida: int

    @classmethod
    def new(cls, serie, ano, partida):
        return cls(id=str(uuid4()), serie=serie, ano=ano, partida=partida)

    def process(self):
        body = self.model_dump()
        body = json.dumps(body)
        return body


class WorkerCBF:
    QUEUE_DOWNLOAD = "cbf.download.pdf"
    SEND_EXCHANGE = "cbf.download.pdf.success"
    BACKUP_SUCCSS = "cbf.download.pdf.backup"

    SEGUNDO = 1000
    MINUTO = SEGUNDO * 60
    HORA = MINUTO * 60
    DIA = HORA * 24
    DIAS = DIA * 1
    qtd_consumers = 0

    BACKUP_SUCCSS_TTL = DIAS * 1

    QueryParams = QueryParams

    def __init__(self, connection, channel: Channel = None, qtd_consumers=0):
        self.connection = connection
        self.channel = channel or connection.channel()
        self.qtd_consumers = qtd_consumers

    class SuccessParams(BaseModel):
        queue_params: QueryParams
        file: bytes

        def process(self):
            body = self.model_dump()
            body["file"] = gzip.compress(self.file).decode("latin1")
            return gzip.compress(body.encode("latin1")).decode("latin1")

    @classmethod
    def _declare_queue(
        cls,
        channel,
        queue,
        create_dql=True,
        args=None,
        delete=False,
    ):
        if not args:
            args = {}
        ch = channel.connection.channel()
        if create_dql:
            queue_dlq = ch.queue_declare(
                queue=f"{queue}.dlq",
                durable=True,
            )
            args.update(
                {
                    "x-dead-letter-exchange": "",
                    "x-dead-letter-routing-key": queue_dlq.method.queue,
                }
            )
        try:
            return ch.queue_declare(
                queue=queue,
                durable=True,
                arguments=args,
            )
        except Exception as e:
            logger.error(e)
            if delete:
                ch = channel.connection.channel()
                channel.queue_delete(queue=queue)
            return ch.queue_declare(
                queue=queue,
                durable=True,
                arguments=args,
            )

    def _declare_exchange(self, channel, exchange):
        return channel.exchange_declare(
            exchange=exchange,
            durable=True,
            exchange_type="fanout",
        )

    @classmethod
    def _publish(cls, channel, queue, body):
        body = body.process()
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )

    def declare(self):
        channel = self.connection.channel()
        queue = self._declare_queue(channel, self.QUEUE_DOWNLOAD)
        self._declare_exchange(channel, self.SEND_EXCHANGE)
        queue_backup = self._declare_queue(
            channel,
            self.BACKUP_SUCCSS,
            create_dql=False,
            args={
                "x-message-ttl": self.BACKUP_SUCCSS_TTL,
            },
            delete=True,
        )
        channel.queue_bind(
            exchange=self.SEND_EXCHANGE,
            queue=queue_backup.method.queue,
        )
        return queue

    def publish(self, body: QueryParams):
        if not isinstance(body, self.QueryParams):
            raise TypeError("body must be a pydantic BaseModel")
        self._publish(self.channel, self.QUEUE_DOWNLOAD, body)

    def heartbeat(self):
        logger.debug("HEARTBEAT")
        queue = self.declare()
        mensagens = queue.method.message_count
        qtd_consumers = queue.method.consumer_count
        diff = self.qtd_consumers - qtd_consumers
        logger.debug(f"mensagens: {mensagens} qtd_consumers: {qtd_consumers}")
        logger.debug(f"diff: {diff}")
        if mensagens > 0 and diff > 0:
            for _ in range(diff):
                self.new_consumer()

    def new_consumer(self):
        Process(target=self.consumer, args=(self.connection,)).start()

    @classmethod
    def consumer(cls, connection):
        worker = cls(connection)
        channel: Channel = worker.channel
        worker.declare()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=worker.QUEUE_DOWNLOAD,
            on_message_callback=worker.callback,
            auto_ack=False,
        )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        try:
            body = json.loads(body)
            params = self.QueryParams(**body)
        except Exception as e:
            logger.error(e)
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

        cbf = CBF()
        url = cbf.get_url_sumula_external(
            params.serie,
            params.ano,
            params.partida,
        )
        file = cbf.request_download_file(url)

        self.send_to_success(ch, params, file)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_to_success(self, ch, query_params: QueryParams, file: bytes):
        body = self.SuccessParams(
            queue_params=query_params,
            file=file,
        )

        ch.basic_publish(
            exchange=self.SEND_EXCHANGE,
            routing_key="",
            body=body.process(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
