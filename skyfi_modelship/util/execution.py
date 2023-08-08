import shutil
from typing import Any, Optional
import uuid

from loguru import logger

from pydantic.dataclasses import dataclass

from skyfi_modelship import skyfi_types as st

from .inference_request import InferenceRequest
from .storage import local_folder, upload


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
    response = func(**r.kwargs)
    # post process the response
    response = post_process(response, r.request_id, r.output_folder, func.__name__)
    request_folder = local_folder(r.request_id)
    shutil.rmtree(request_folder, ignore_errors=True)
    return InferenceResponse(
        request_id=r.request_id, output_folder=r.output_folder, response=response
    )


def post_process(
    response: Any, request_id: uuid.UUID, output_folder: Optional[str], func_name: str
) -> Any:
    """ Loops through all elements of the response and post processes them """
    try:
        processed_items = []
        response_iter = iter(response)
        for item in response_iter:
            processed_item = post_process_item(item, output_folder, func_name)
            processed_items.append(processed_item)
        return processed_items
    except TypeError:
        return post_process_item(response, output_folder, func_name)


def post_process_item(
    item: Any, output_folder: Optional[str], func_name: str
) -> Any:
    """ Post processes a single item, e.g. upload an image to the output folder """

    logger.info("Post processing item: {item}", item=item)

    if isinstance(item, st.Image):
        if output_folder is None:
            logger.warning("Skipping upload of image, no output folder specified")
            return item

        # upload the image to the output folder
        name = None
        ref_name = None
        if isinstance(item, st.OutputBase):
            name = item.name
            ref_name = item.ref_name
        path = upload(item.path, output_folder, func_name, name, ref_name)
        item.path = path

    return item
