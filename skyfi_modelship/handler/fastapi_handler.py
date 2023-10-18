from loguru import logger
import uvicorn

from starlette import status

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from skyfi_modelship.config import load_config

from skyfi_modelship.util.inference_request import convert_request
from skyfi_modelship.util.execution import exec_func


class FastApiHandler:

    def listen(self, func):
        logger.info("Starting fastapi for: {func}", func=func)

        config = load_config()

        fastapi = FastAPI()
        fastapi.post("/")(self.handle(func))
        uvicorn.run(fastapi, host=config.fastapi_host, port=config.fastapi_port)

    def handle(self, func):
        async def post_handler(req: Request):
            data = await req.json()
            try:
                r = convert_request(data, func)
            except ValidationError as ve:
                raise RequestValidationError(errors=ve.errors(), body=data)

            logger.info("Calling inference function for request {request_id} => {func}({kwargs})",
                        request_id=r.request_id, func=func.__name__, kwargs=r.kwargs)
            try:
                return exec_func(func, r)
            except Exception as ex:
                logger.error("Error executing function: {func}({kwargs}) => {exception}",
                             func=func.__name__, kwargs=r.kwargs, exception=ex)
                detail = f"{type(ex).__name__}: {ex}"
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
        return post_handler
