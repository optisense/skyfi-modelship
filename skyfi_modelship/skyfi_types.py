from functools import cached_property
import os
import typing
from typing import Any, Dict, Generic, Optional, TypeVar
from loguru import logger
import orjson

import shapely.wkt
from pydantic import BaseModel, computed_field, field_validator
from pydantic.dataclasses import dataclass
from geojson_pydantic import FeatureCollection


@dataclass
class Polygon:
    wkt: str

    @field_validator("wkt")
    @classmethod
    def valid_wkt(cls, wkt: str):
        logger.info("Validating wkt ... {wkt}", wkt=wkt)
        try:
            shapely.wkt.loads(wkt)
        except Exception:
            raise ValueError('must be a valid wkt')
        return wkt


class GeoJSON(FeatureCollection):
    """ Store a GeoJSON Feature Object. """

    def __init__(self, geo_str: Optional[object] = None, **kwargs):
        if geo_str:
            logger.info("Validating geo_json ... {geo_str}", geo_str=geo_str)
            geo_json = str(geo_str)
            geo_dict = orjson.loads(geo_json)
            super().__init__(**geo_dict)
        elif len(kwargs):
            super().__init__(**kwargs)
        else:
            raise ValueError('must be a valid geo_json')


def make_ext_validator(extensions: typing.List[str]):
    def validate_extension(path: Optional[str]):
        if path:
            ext = os.path.splitext(path)[1]
            if ext.lower() not in extensions:
                raise ValueError(f"File extension must be one of {extensions}")
        return path

    return validate_extension


def validate_not_empty_string(value: str):
    if not value:
        raise ValueError("String must not be empty")
    return value


@dataclass
class File:
    """
    Store an file path

    path: will be local temporary path to the file
    """

    path: str

    _path_not_empty = field_validator("path")(validate_not_empty_string)


@dataclass
class PNG(File):
    """
    Store a PNG image path and metadata xml if available

    path: will be local temporary path to the image
    metadata_path: (Optional) metadata xml for the image
    """

    metadata_path: Optional[str] = None

    _validate_image_ext = field_validator("path")(make_ext_validator([".png"]))
    _validate_metadata_xml_ext = field_validator("metadata_xml_path")(make_ext_validator([".xml"]))


@dataclass
class GeoTIFF(File):
    """
    Store a GeoTIFF image path and metadata xml if available

    path: will be local temporary path to the image
    metadata_path: (Optional) metadata xml for the image
    """

    metadata_xml_path: Optional[str] = None

    _validate_image_ext = field_validator("path")(make_ext_validator([".tiff", ".tif"]))
    _validate_metadata_xml_ext = field_validator("metadata_xml_path")(make_ext_validator([".xml"]))


@dataclass
class ENVI(File):
    """
    Store an ENVI with path and header file if available

    path: will be local temporary path to the image
    header_path: (Optional) header file for the image
    """

    header_path: Optional[str] = None

    _validate_image_ext = field_validator("path")(make_ext_validator(["", ".dat", ".img", ".bil"]))
    _validate_header_ext = field_validator("header_path")(make_ext_validator([".hdr"]))


@dataclass
class Package(File):
    """
    Store a package file

    path: will be local temporary path to archive
    """

    _validate_pkg_ext = field_validator("path")(make_ext_validator([".zip", ".tar.gz"]))


T = TypeVar("T", int, float, str, Polygon, GeoJSON, PNG, GeoTIFF, ENVI, Package)


class Output(BaseModel, Generic[T]):
    """
    Base class for all outputs.

    params:
    _name_: name of the output
    _value_: the value representing the output
    _ref_name_: (Optional) reference to the input
    _tags_: (Optional) tags for the output
    _metadata_: (Optional) additional metadata
    """

    name: str
    value: T

    ref_name: Optional[str] = None
    tags: Optional[typing.List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @computed_field
    @cached_property
    def output_type(self) -> str:
        return type(self.value).__name__


class IntOutput(Output[int]):
    pass


class FloatOutput(Output[float]):
    pass


class StrOutput(Output[str]):
    pass


class PolygonOutput(Output[Polygon]):
    pass


class GeoJSONOutput(Output[GeoJSON]):
    path: Optional[str] = None


class FileOutput(Output[File]):
    pass


class PNGOutput(Output[PNG]):
    pass


class GeoTIFFOutput(Output[GeoTIFF]):
    pass


class ENVIOutput(Output[ENVI]):
    pass


class PackageOutput(Output[Package]):
    pass
