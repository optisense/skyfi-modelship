from typing import List
from loguru import logger

from geojson_pydantic import Polygon, Feature, FeatureCollection

from rasterio import warp, open as ropen

import skyfi_modelship as skyfi


app = skyfi.SkyfiApp()


@app.bootstrap
def download():
    """Download the model."""
    logger.info("Downloading model...")


@app.inference
def exec(
    tiff_image: skyfi.Image,
) -> [skyfi.ImageOutput, skyfi.GeoJSONOutput, List[skyfi.PolygonOutput]]:
    """Georeferencing example."""
    logger.info(
        "Running georef example on ... " "{tiff}",
        tiff=tiff_image,
    )

    # 2 areas were detected:
    detections = [
        [100, 100, 200, 200, 0.70, "Lake"],
        [300, 300, 400, 400, 0.80, "Tower"],
    ]
    geojson = georeference(tiff_image, detections)

    image_output = skyfi.ImageOutput(
        path=tiff_image.path,
        type=skyfi.ImageType.GEOTIFF,
        name="output",
        ref_name="tiff_image",
        tags=["test1", "test2", str(detections)],
    )

    geometries = [poly.geometry for poly in geojson.features]
    polygons_output = [
        skyfi.PolygonOutput(wkt=g.wkt, name="poly", ref_name="tiff_image")
        for g in geometries
    ]

    geojson_output = skyfi.GeoJSONOutput(geojson, name="geojson", ref_name="tiff_image")

    return image_output, geojson_output, polygons_output


def georeference(geo_tiff: skyfi.Image, detections: List[List[float]]):
    features = []
    logger.info(
        "Opening geotiff {geo_tiff} for geojson generation", geo_tiff=geo_tiff
    )

    with ropen(geo_tiff.path) as src:
        for d in detections:
            nw_x, nw_y, se_x, se_y = d[:4]
            nw = src.transform * (nw_x, nw_y)
            se = src.transform * (se_x, se_y)
            coords = warp.transform(
                src.crs,
                src.crs.from_epsg(4326),
                [nw[0], se[0]],
                [nw[1], se[1]],
            )
            accuracy = d[4]
            name = d[5]
            polygon = Polygon.from_bounds(
                coords[0][0], coords[1][1], coords[0][1], coords[1][0]
            )
            feature = Feature(
                type="Feature",
                geometry=polygon,
                properties={"name": name, "accuracy": accuracy},
            )
            features.append(feature)

    feature_collection = FeatureCollection(type="FeatureCollection", features=features)
    return feature_collection


app.start()
