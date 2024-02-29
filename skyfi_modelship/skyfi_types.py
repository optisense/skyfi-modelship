from functools import cached_property
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

    def __init__(self, geo_str: Optional[object] = None, **kwargs) -> FeatureCollection:
        if geo_str:
            logger.info("Validating geo_json ... {geo_str}", geo_str=geo_str)
            geo_json = str(geo_str)
            geo_dict = orjson.loads(geo_json)
            super().__init__(**geo_dict)
        elif len(kwargs):
            super().__init__(**kwargs)
        else:
            raise ValueError('must be a valid geo_json')


@dataclass
class Image:
    """
    Store an image path

    path: will be local temporary path to the image
    """

    path: str


@dataclass
class PNG(Image):
    """
    Store a PNG image path and metadata xml if available

    path: will be local temporary path to the image
    metadata_xml_path: (Optional) metadata xml for the image
    """

    path: str
    metadata_xml_path: Optional[str] = None


@dataclass
class GeoTIFF(Image):
    """
    Store a GeoTIFF image path and metadata xml if available

    path: will be local temporary path to the image
    metadata_xml_path: (Optional) metadata xml for the image
    """

    metadata_xml_path: Optional[str] = None


@dataclass
class ENVI(Image):
    """
    Store an ENVI with path and header file if available

    path: will be local temporary path to the image
    header_path: (Optional) header file for the image
    """

    header_path: Optional[str] = None


@dataclass
class Package():
    path: str


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


class PNGOutput(Output[PNG]):
    pass


class GeoTIFFOutput(Output[GeoTIFF]):
    pass


class ENVIOutput(Output[ENVI]):
    pass


class PackageOutput(Output[Package]):
    pass
