from typing import List
from loguru import logger

import skyfi_modelship as skyfi


app = skyfi.SkyfiApp()


@app.bootstrap
def download():
    """Download the model."""
    logger.info("Downloading model...")


@app.inference
def exec(
    arr: List[skyfi.Float],
    fl_number: skyfi.Float,
    int_number: skyfi.Integer,
    tiff_image: skyfi.Image,
    poly: skyfi.Polygon,
) -> [skyfi.ImageOutput, skyfi.FloatOutput, skyfi.PolygonOutput]:
    """Run inference on the Skyfi data."""
    logger.info(
        "Running Skyfi inference... "
        "{fl_number}, {int_number}, {tiff}, {poly}, {arr}",
        fl_number=fl_number,
        int_number=int_number,
        tiff=tiff_image,
        poly=poly,
        arr=arr,
    )
    my_var = skyfi.Float(fl_number.value + int_number.value)
    image_output = skyfi.ImageOutput(
        path=tiff_image.path,
        type=skyfi.ImageType.GEOTIFF,
        name="output",
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    float_output = skyfi.FloatOutput(
        value=my_var,
        name="idx",
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    polygon_output = skyfi.PolygonOutput(
        wkt=poly.wkt,
        name="poly",
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    return image_output, float_output, polygon_output


app.start()
