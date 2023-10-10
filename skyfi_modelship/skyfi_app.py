from loguru import logger
import orjson
from fastapi.encoders import jsonable_encoder

from .config import load_config


class SkyfiApp:
    """
    The main SkyFi integration class.
    Using this class and its decorators will be all that is required
    for the integration of a model with the infrastructure.
    """

    bootstrap_func = None
    inference_func = None

    def start(self):
        """
        Start the Skyfi application.
        Execute this once all the decorators have been applied.
        """

        if self.inference_func is None:
            raise ValueError("Inference function required.")

        if self.bootstrap_func:
            logger.info("Calling the bootstrap function...")
            self.bootstrap_func()

        config = load_config()

        # if rabbitmq is enabled, import and call the handler
        if config.is_rabbitmq_worker:
            from .handler.rabbitmq_handler import RabbitMQHandler
            handler = RabbitMQHandler()
            handler.listen(self.inference_func)

        # if fastapi is enabled, import and call the handler
        elif config.is_fastapi_server:
            from .handler.fastapi_handler import FastApiHandler
            handler = FastApiHandler()
            handler.listen(self.inference_func)

        # use args
        else:
            from .handler.args_handler import ArgsHandler
            handler = ArgsHandler()
            result = handler.handle(self.inference_func)
            logger.info("Printing inference to stdout")

            print(orjson.dumps(jsonable_encoder(result)))
            return result

    def bootstrap(self, func):
        """
        Decorator to be used on a function that handles bootstrap tasks.
        These may include checking and downloading new weights, sanity checks, etc
        """

        if self.bootstrap_func is not None:
            raise ValueError("Single bootstrap function allowed.")

        self.bootstrap_func = func
        return func

    def inference(self, func):
        """
        Decorator to be used on a function that will do the model inference.
        All parameters of the functions, including the return type(s) must be
        part of the skyfi_modelship.types module. Only exception is that we allow
        iterables
        """

        if self.inference_func is not None:
            raise ValueError("Single inference function allowed.")

        self.inference_func = func
        return func
