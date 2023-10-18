from loguru import logger

import skyfi_modelship as s


app = s.SkyfiApp()


@app.bootstrap
def download():
    """Download the model."""
    logger.info("Downloading model...")


@app.inference
def exec(
    in_arr: s.list[s.float],
    in_fl_number: s.float,
    in_int_number: s.int,
    in_tiff_image: s.Image,
    in_poly: s.Polygon,
    in_geojson: s.GeoJSON,
) -> [s.ImageOutput,
      s.FloatOutput,
      s.list[s.FloatOutput],
      s.PolygonOutput,
      s.GeoJSONOutput]:

    """Run inference on the Skyfi data."""
    logger.info(
        "Running Skyfi inference... "
        "{in_arr}, {in_fl_number}, {in_int_number}, {in_tiff_image}, {in_poly}, {in_geojson}",
        in_arr=in_arr,
        in_fl_number=in_fl_number,
        in_int_number=in_int_number,
        in_tiff_image=in_tiff_image,
        in_poly=in_poly,
        in_geojson=in_geojson,
    )
    my_var = in_fl_number + in_int_number
    image_output = s.ImageOutput(
        name="output",
        value=in_tiff_image,
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    float_output = s.FloatOutput(
        name="idx",
        value=my_var,
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    polygon_output = s.PolygonOutput(
        name="poly",
        value=in_poly,
        ref_name="tiff_image",
        tags=["test1", "test2", str(my_var)],
    )

    geojson_output = s.GeoJSONOutput(
        name="geojson",
        value=in_geojson,
        ref_name="in_geojson",
        tags=["test1", "test2", str(my_var)],
    )
    return image_output, float_output, [float_output], polygon_output, geojson_output


app.start()
