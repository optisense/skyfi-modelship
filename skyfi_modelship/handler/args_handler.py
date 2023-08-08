import argparse
import inspect
import sys
from loguru import logger

from skyfi_modelship.util.execution import exec_func
from skyfi_modelship.util.inference_request import convert_request
from skyfi_modelship.skyfi_types import Image, GeoJSON


class ArgsHandler:

    def handle(self, func):

        logger.info("Args Handler for: {args}", args=sys.argv)

        class ThrowingArgumentParser(argparse.ArgumentParser):
            def error(self, message):
                raise ValueError(message)

        parser = ThrowingArgumentParser(
            description='SkyFi ModelShip Args Handler',
            exit_on_error=False
        )

        # add the required arguments
        parser.add_argument("--request_id", type=str)
        parser.add_argument("--output_folder", type=str)

        # add the inference function arguments
        for arg, param in inspect.signature(func).parameters.items():
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(f"Missing type annotation for argument {arg}")

            if param.annotation == Image:
                parser.add_argument(f'--{arg}.path', required=True)
                parser.add_argument(f'--{arg}.type', required=True)
            elif param.annotation == GeoJSON:
                parser.add_argument(f'--{arg}', type=str, required=True)
            else:
                parser.add_argument(f'--{arg}', type=param.annotation, required=True)

        data = vars(parser.parse_args(sys.argv[1:]))
        for arg, param in inspect.signature(func).parameters.items():
            if param.annotation == Image:
                data[arg] = {
                    "path": data.get(f"{arg}.path"),
                    "type": data.get(f"{arg}.type"),
                }
        r = convert_request(data, func)
        logger.info(
            "Calling inference function for request {request_id} => {func}({kwargs})",
            request_id=r.request_id, func=func.__name__, kwargs=r.kwargs
        )
        return exec_func(func, r)
