from typing import Any, Callable, Optional, Union
import uuid

from loguru import logger

from skyfi_modelship import skyfi_types as st
from .storage import download, local_folder, save_local_file, upload


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

    def download_asset(field: str, asset: Any, **kwargs):
        if not isinstance(asset, (st.Image, st.MetadataXml)):
            return

        if not request_id:
            logger.warning("No request_id provided, skipping download: {item}", item=asset)
            return

        if not asset.path.startswith("gs://"):
            logger.warning("Image is local, skipping download: {item}", item=asset)
            return

        asset: Union[st.Image, st.MetadataXml] = asset
        folder = local_folder(request_id, field)
        path = download(asset.path, folder)
        asset.path = path

    return download_asset


def upload_callable(
    output_folder: Optional[str] = None,
    func_name: Optional[str] = None,
    request_id: Optional[uuid.UUID] = None
) -> Callable:

    def upload_asset(field, asset, **kwargs):
        if isinstance(asset, st.ImageOutput):
            asset_path = asset.value.path
        elif isinstance(asset, st.GeoJSONOutput):
            # dump the geojson to a local file
            geojson_value: st.GeoJSON = asset.value
            asset_path = save_local_file(
                request_id, field, asset.name, geojson_value.model_dump_json()
            )
            asset.path = asset_path
        else:
            # we support uploading only images and geojsons
            return

        if not output_folder:
            logger.warning("No output_folder provided, skipping upload: {item}", item=asset)
            return
        if not output_folder.startswith("gs://"):
            logger.warning("Output folder is not gs://, skipping upload: {item}", item=asset)
            return

        # upload the file to GCS
        gcs_path = upload(asset_path, output_folder,
                          func_name, name=asset.name, ref_name=asset.ref_name)

        # update the path of the objects to the GCS path
        if isinstance(asset, st.ImageOutput):
            asset.value.path = gcs_path
        elif isinstance(asset, st.GeoJSONOutput):
            asset.path = gcs_path

    return upload_asset
