import inspect
import json
from typing import Any, Optional
import uuid

from loguru import logger

from pydantic import ValidationError

from pydantic.dataclasses import dataclass as py_dataclass

from geojson_pydantic import FeatureCollection
from pydantic_core import InitErrorDetails

from skyfi_modelship import skyfi_types as st

from .storage import download, local_folder


@py_dataclass
class InferenceRequest:
    """
    Contains all information needed to run an inference function.

    request_id: internal id of the request
    output_folder: upload destination for the output files
    kwargs: the inference function parameters
    """
    request_id: uuid.UUID
    output_folder: Optional[str]
    kwargs: dict


def convert_request(data: dict, func) -> InferenceRequest:
    """
    Converts a request dict to InferenceRequest.
    Maps all inference function parameters to skyfi.* types.
    """

    # get the required request_id and output_folder
    request_id = convert_parameter(data.get("request_id"), uuid.UUID)
    output_folder = convert_parameter(data.get("output_folder"), str)

    kwargs = {}
    errors = []
    # loop the inference function signature and map the parameters to skyfi.* types
    for arg, param in inspect.signature(func).parameters.items():
        try:
            data_arg = data[arg]
            # pre-process the parameter if needed, e.g. download an image to a local folder
            data_arg = pre_process(param.annotation, arg, data_arg, request_id)

            # convert the parameter to the skyfi.* type
            kwargs[arg] = convert_parameter(data_arg, param.annotation)

        except Exception as ex:
            error = InitErrorDetails(type(ex).__name__, loc=(arg,), input=data.get(arg))
            errors.append(error)

    # raise ValidationError if there are any errors during the conversion
    if errors:
        raise ValidationError.from_exception_data(
            "InferenceRequest Validation error",
            line_errors=errors)

    return InferenceRequest(request_id=request_id, output_folder=output_folder, kwargs=kwargs)


def convert_parameter(data: Any, param_type: type):
    logger.info("Converting parameter... {data} to {param_type}", data=data, param_type=param_type)

    if not data:
        return None
    elif type(data) == param_type:
        # already converted
        return data
    elif param_type == st.GeoJSON and isinstance(data, dict):
        # special case for GeoJSON when we already parsed a dict
        value = FeatureCollection(data)
        return st.GeoJSON(value)
    elif param_type == st.GeoJSON and isinstance(data, str):
        # special case for GeoJSON when we have a string
        data_dict = json.loads(data)
        value = FeatureCollection(data_dict)
        return st.GeoJSON(value)
    if isinstance(data, dict):
        # complex types init, e.g. Image
        return param_type(**data)
    elif isinstance(data, list):
        # recursive conversion for lists
        values = []
        for value in data:
            values.append(convert_parameter(value, param_type.__args__[0]))
        return values
    else:
        # simple types init
        return param_type(data)


def pre_process(anno: type, arg: str, data: Any, request_id: Optional[uuid.UUID]) -> Any:
    if anno == st.Image:

        # skip if no request to tie to
        if not request_id:
            logger.warning(
                "Skipping downloading of image {arg} because request_id is not set",
                arg=arg
            )
            return data

        # download the image to a local folder
        folder = local_folder(request_id, arg)
        if not isinstance(data, dict) or "path" not in data:
            raise ValueError("Image must be a dict with a `path` attribute")

        # skip if not gs file, e.g. local file
        if not data["path"].startswith("gs://"):
            logger.warning(
                "Skipping downloading of image {arg}, url is not gs://",
                arg=arg
            )
            return data
        path = download(data["path"], folder)
        data["path"] = path

    return data
