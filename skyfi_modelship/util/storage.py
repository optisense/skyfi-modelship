from typing import Optional
from google.cloud import storage
import os
from pathlib import Path

from loguru import logger


def download(path: str, folder: str) -> str:
    """ Download a file from a GCS bucket to a local folder. """

    storage_client = storage.Client()
    try:
        Path(folder).mkdir(parents=True, exist_ok=True)
        filename = os.path.basename(path)
        destination = f"{folder}/{filename}"
        blob = storage.Blob.from_string(path, client=storage_client)
        logger.info("Downloading file... {path} to {destination}",
                    path=path, destination=destination)
        blob.download_to_filename(destination)
        return destination
    except Exception as ex:
        raise ValueError(f"Error downloading file: {path}: {ex}")


def upload(path: str, folder: str,
           func_name: str, name: Optional[str], ref_name: Optional[str]) -> str:
    """ Upload a file from a local folder to a GCS bucket. """

    storage_client = storage.Client()
    try:
        dst_path = Path(path)

        # Add function name to the file name
        dst_path = dst_path.with_stem(dst_path.stem + f"_{func_name}")

        # if provided, add the name and the ref_name to the filename
        if name and ref_name:
            name_stem = f"_{name}_for_{ref_name}"
            dst_path = dst_path.with_stem(dst_path.stem + name_stem)
        dst = f"{folder}/{dst_path.name}"

        # upload the file
        logger.info("Uploading file... {path} to {dst}",
                    path=path, dst=dst)
        blob = storage.Blob.from_string(dst, client=storage_client)
        blob.upload_from_filename(path)
        return dst
    except Exception as ex:
        raise ValueError(f"Error uploading file: {path}: {ex}")


def local_folder(*args) -> str:
    # compute local folder path given the args
    str_args = [str(arg) for arg in args]
    folder = "/".join(str_args)
    return f"/tmp/{folder}"
