from enum import Enum
import typing
from typing import Any, Dict, Optional
from loguru import logger
import shapely.wkt
from pydantic import validator
from pydantic.dataclasses import dataclass

import geojson
from geojson import GeoJSON as GeoJSONBase


@dataclass
class Integer:
    """ Store an integer value. """

    value: int

    def __int__(self):
        return self.value

    def __repr__(self) -> str:
        return int(self).__repr__()


@dataclass
class Float:
    """ Store a float value. """

    value: float

    def __float__(self):
        return self.value

    def __repr__(self) -> str:
        return float(self).__repr__()


@dataclass
class Polygon:
    """ Store a polygon as a wkt string. """

    wkt: str

    @validator("wkt")
    def validate(cls, wkt):
        logger.info("Validating wkt ... {wkt}", wkt=wkt)
        try:
            shapely.wkt.loads(wkt)
        except Exception:
            raise ValueError('must be a valid wkt')
        return wkt

    def __str__(self) -> str:
        return self.wkt

    def __repr__(self) -> str:
        return str(self).__repr__()


@dataclass
class GeoJSON:
    """ Store a GeoJSON Feature Object. """

    value: GeoJSONBase

    def __str__(self) -> str:
        return geojson.dumps(self.value)

    def __repr__(self) -> str:
        return str(self).__repr__()


class ImageType(Enum):
    """ Supported image types. """

    GEOTIFF = "GEOTIFF"
    PNG = "PNG"


@dataclass
class Image:
    """
    Store an image path and type.

    path: will be local temporary path to the image
    type: type of the image
    """

    path: str
    type: ImageType


@dataclass
class OutputBase:
    """
    Base class for all outputs.

    params:
    _name_: name of the output
    _ref_name_: reference to the input
    _tags_: tags for the output
    _metadata_: additional metadata
    """

    name: str
    ref_name: Optional[str] = None
    tags: Optional[typing.List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IntegerOutput(OutputBase, Integer):
    """ Output class for integers. """

    output_type: str = Integer.__name__


@dataclass
class FloatOutput(OutputBase, Float):
    """ Output class for floats. """

    output_type: str = Float.__name__


@dataclass
class PolygonOutput(OutputBase, Polygon):
    """ Output class for polygons. """

    output_type: str = Polygon.__name__


@dataclass
class GeoJSONOutput(OutputBase, GeoJSON):
    """ Output class for GeoJSON features. """

    output_type: str = GeoJSON.__name__


@dataclass
class ImageOutput(OutputBase, Image):
    """ Output class for images. """

    output_type: str = Image.__name__
