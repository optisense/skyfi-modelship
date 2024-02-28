from typing import Any, Callable, Optional
import uuid

from loguru import logger

from skyfi_modelship import skyfi_types as st
from .storage import download, local_folder, save_local_file, upload


def walk_fields(field_key: str, obj: Any, fn: Callable, **kwargs) -> Any:
    if isinstance(obj, (list, tuple)):
        [walk_fields(f"{field_key}_{idx}", v, fn, **kwargs) for idx, v in enumerate(obj)]
    elif isinstance(obj, dict):
        for field, value in obj.items():
            walk_fields(f"{field_key}_{field}", value, fn, **kwargs)
    else:
        fn(f"{field_key}", obj, **kwargs)


def download_callable(request_id: Optional[uuid.UUID] = None) -> Callable:

    def download_asset(field: str, asset: Any, **kwargs):
        if not isinstance(asset, (st.Image, st.Package)):
            return

        if not request_id:
            logger.warning("No request_id provided, skipping download: {item}", item=asset)
            return

        if not asset.path.startswith("gs://"):
            logger.warning("Image is local, skipping download: {item}", item=asset)
            return

        folder = local_folder(request_id, field)
        asset.path = download(asset.path, folder)
        if isinstance(asset, (st.PNG, st.GeoTIFF)) and asset.metadata_xml_path:
            asset.metadata_xml_path = download(asset.metadata_xml_path, folder)
        if isinstance(asset, st.ENVI) and asset.header_path:
            asset.header_path = download(asset.header_path, folder)

    return download_asset


def upload_callable(
    output_folder: Optional[str] = None,
    func_name: Optional[str] = None,
    request_id: Optional[uuid.UUID] = None,
) -> Callable:

    def upload_asset(field, asset, **kwargs):
        if not isinstance(asset, st.Output):
            return
        if not output_folder:
            logger.warning("No output_folder provided, skipping upload: {item}", item=asset)
            return
        if not output_folder.startswith("gs://"):
            logger.warning("Output folder is not gs://, skipping upload: {item}", item=asset)
            return

        value = asset.value
        if isinstance(value, (st.Image, st.Package)):
            value.path = upload(
                value.path, output_folder,
                func_name, name=asset.name, ref_name=asset.ref_name,
            )
            if isinstance(value, (st.PNG, st.GeoTIFF)) and value.metadata_xml_path:
                value.metadata_xml_path = upload(
                    value.metadata_xml_path, output_folder,
                    func_name, name=asset.name, ref_name=asset.ref_name,
                )
            if isinstance(value, st.ENVI) and value.header_path:
                value.header_path = upload(
                    value.header_path, output_folder,
                    func_name, name=asset.name, ref_name=asset.ref_name,
                )
        elif isinstance(asset, st.GeoJSONOutput):
            # dump the geojson to a local file
            geojson_value: st.GeoJSON = asset.value
            asset.path = save_local_file(
                request_id, field, asset.name, geojson_value.model_dump_json()
            )
            asset.path = upload(
                    asset.path, output_folder,
                    func_name, name=asset.name, ref_name=asset.ref_name,
                )

    return upload_asset
