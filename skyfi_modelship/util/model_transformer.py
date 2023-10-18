
from typing import Any, Callable, Optional
import uuid

from loguru import logger

from skyfi_modelship import skyfi_types as st
from .storage import download, local_folder, upload


def walk_fields(
    field_key: str, obj: Any, fn: Callable, **kwargs
) -> Any:
    if isinstance(obj, (list, tuple)):
        [walk_fields(f"{field_key}_{idx}", v, fn, **kwargs) for idx, v in enumerate(obj)]
    elif isinstance(obj, dict):
        for field, value in obj.items():
            walk_fields(f"{field_key}_{field}", value, fn, **kwargs)
    else:
        fn(f"{field_key}", obj, **kwargs)


def download_callable(
    request_id: Optional[uuid.UUID] = None
) -> Callable:

    def download_image(field, value, **kwargs):
        if not isinstance(value, st.Image):
            return
        if not request_id:
            logger.warning("No request_id provided, skipping download: {item}", item=value)
            return

        image: st.Image = value
        if not image.path.startswith("gs://"):
            logger.warning("Image is local, skipping download: {item}", item=value)
            return

        folder = local_folder(request_id, field)
        path = download(image.path, folder)
        image.path = path

    return download_image


def upload_callable(
    output_folder: Optional[str] = None, func_name: Optional[str] = None,
) -> Callable:

    def upload_image(field, value, **kwargs):
        if not isinstance(value, st.ImageOutput):
            return
        if not output_folder:
            logger.warning("No output_folder provided, skipping upload: {item}", item=value)
            return
        if not output_folder.startswith("gs://"):
            logger.warning("Output folder is not gs://, skipping upload: {item}", item=value)
            return

        image: st.ImageOutput = value
        path = upload(image.value.path, output_folder,
                      func_name, name=image.name, ref_name=image.ref_name)
        image.value.path = path

    return upload_image
