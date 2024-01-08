from loguru import logger
import orjson
import pika
from pika.channel import Channel
from pika.spec import Basic

from fastapi.encoders import jsonable_encoder

from skyfi_modelship.config import load_config
from skyfi_modelship.util.inference_request import convert_request
from skyfi_modelship.util.execution import exec_func


class RabbitMQHandler:

    def listen(self, func):
        config = load_config()

        connection = pika.BlockingConnection(
            pika.URLParameters(config.rabbitmq_host)
        )
        channel = connection.channel()

        channel.basic_qos(prefetch_count=1)  # process 1 message at a time
        channel.basic_consume(
            queue=config.rabbitmq_req_queue, on_message_callback=self.handle(func)
        )
        logger.info("Waiting for messages...")
        channel.start_consuming()
        logger.info("Closing listener...")
        connection.close()

    def handle(self, func):
        def message_handler(
            ch: Channel,
            method: Basic.Deliver,
            properties: pika.BasicProperties,
            payload: bytes,
        ):
            logger.info(
                "Got RabbitMQ message ({properties}): {payload}",
                properties=properties,
                payload=payload,
            )
            data = orjson.loads(payload)

            try:
                r = convert_request(data, func)
            except Exception as ex:
                logger.error("Rejecting request {data}: {exc_info}", data=data, exc_info=ex)
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                return

            try:
                logger.info(
                    "Calling inference function for request {request_id} => {func}({kwargs})",
                    request_id=r.request_id,
                    func=func.__name__,
                    kwargs=r.kwargs,
                )
                response = exec_func(func, r)
                config = load_config()
                logger.info(
                    "Publishing {response} to {exchange}/{queue}",
                    response=response,
                    exchange=config.rabbitmq_exchange,
                    queue=config.rabbitmq_resp_queue,
                )
                ch.basic_publish(
                    exchange=config.rabbitmq_exchange,
                    routing_key=config.rabbitmq_resp_queue,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id,
                        content_type="application/json",
                    ),
                    body=orjson.dumps(jsonable_encoder(response)),
                )
                logger.info(
                    "Acking request {request_id}: {delivery_tag}",
                    request_id=r.request_id,
                    delivery_tag=method.delivery_tag,
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as ex:
                logger.warning(
                    "Requeing request {request_id}, {delivery_tag}: {ex}",
                    request_id=r.request_id,
                    delivery_tag=method.delivery_tag,
                    ex=ex,
                    exc_info=ex
                )
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

        return message_handler
