import inspect
from typing import Optional
import uuid

from pydantic import BaseModel, create_model

from .model_transformer import download_callable, walk_fields


class InferenceRequest(BaseModel):
    """
    Contains all information needed to run an inference function.

    request_id: internal id of the request
    output_folder: upload destination for the output files
    kwargs: the inference function parameters
    """
    request_id: uuid.UUID
    output_folder: Optional[str] = None
    kwargs: BaseModel


def convert_request(data: dict, func) -> InferenceRequest:
    """
    Converts a request dict to InferenceRequest.
    Maps all inference function parameters to skyfi.* types.
    """

    model_args = {}
    for arg, param in inspect.signature(func).parameters.items():
        model_args[arg] = (param.annotation, ...)

    FunctionArguments = create_model(
        'FunctionArguments',
        **model_args
    )
    kwargs = FunctionArguments.model_validate(data)
    walk_fields("request", vars(kwargs), download_callable(data.get("request_id")))
    request = InferenceRequest.model_validate(data | {"kwargs": kwargs})
    return request
