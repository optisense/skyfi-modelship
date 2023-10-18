from dataclasses import make_dataclass
import inspect
import sys
from typing import Optional
from loguru import logger
from simple_parsing import (
    ArgumentGenerationMode,
    ArgumentParser,
    DashVariant,
    NestedMode
)
from skyfi_modelship.util.execution import exec_func
from skyfi_modelship.util.inference_request import convert_request


class ArgsHandler:

    def handle(self, func):

        logger.info("Args Handler for: {args}", args=sys.argv)

        class ThrowingArgumentParser(ArgumentParser):
            def error(self, message):
                raise ValueError(message)

        dataclass_fields = [("request_id", str), ("output_folder", Optional[str])]
        for arg, param in inspect.signature(func).parameters.items():
            dataclass_fields.append((arg, param.annotation))

        FunctionArguments = make_dataclass('FunctionArguments', dataclass_fields)

        parser = ThrowingArgumentParser(
            description='SkyFi ModelShip Args Handler',
            exit_on_error=False,
            add_option_string_dash_variants=DashVariant.DASH,
            nested_mode=NestedMode.WITHOUT_ROOT,
            argument_generation_mode=ArgumentGenerationMode.NESTED,
        )
        parser.add_arguments(FunctionArguments, dest="func")
        try:
            args = parser.parse_args()
        except BaseException as e:
            logger.error("Error parsing arguments: {e}", e=e)
            raise e
        kwargs = args.func
        req = convert_request(vars(kwargs), func)
        logger.info(
            "Calling inference function for request {request_id} => {func}({kwargs})",
            request_id=req.request_id, func=func.__name__, kwargs=req.kwargs
        )
        return exec_func(func, req)
