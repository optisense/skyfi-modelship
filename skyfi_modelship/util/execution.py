import shutil
from typing import Any, Optional
import uuid

from pydantic.dataclasses import dataclass

from .storage import local_folder

from .model_transformer import walk_fields, upload_callable

from .inference_request import InferenceRequest


@dataclass
class InferenceResponse:
    """
    Contains the result of the inference. request_id and output_folder are the service parameters,
    the response is the output of the inference function
    """

    request_id: uuid.UUID
    output_folder: Optional[str]
    response: Any


def exec_func(func, r: InferenceRequest) -> InferenceResponse:
    """
    Executes the inference function.
    Will post process the response, e.g. upload any output files to the output_folder.
    Will cleanup the local folder.
    """

    # call the function
    response = func(**vars(r.kwargs))
    # post process the response
    walk_fields("", response, upload_callable(r.output_folder, func.__name__, r.request_id))
    request_folder = local_folder(r.request_id)
    shutil.rmtree(request_folder, ignore_errors=True)
    return InferenceResponse(
        request_id=r.request_id, output_folder=r.output_folder, response=response
    )
