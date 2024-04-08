import sys
from typing import Optional, Tuple
from unittest.mock import patch
import uuid

import skyfi_modelship as skyfi


def test_app_optional():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference(provider: Optional[skyfi.str]) -> Optional[skyfi.FloatOutput]:
        assert provider is None, "provider is None"
        return None

    testargs = ["test", "--request-id", str(uuid.uuid4())]
    with patch.object(sys, 'argv', testargs):
        response = app.start()
        assert response.response is None, "app responds when using with argv response"


def test_app_optional_list():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference(provider: Optional[skyfi.list[skyfi.str]]) -> Optional[skyfi.FloatOutput]:
        assert provider is None, "provider is None"
        return None

    testargs = ["test", "--request-id", str(uuid.uuid4())]
    with patch.object(sys, 'argv', testargs):
        response = app.start()
        assert response.response is None, "app responds when using with argv response"


def test_app_optional_images_and_output():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference(
        in_tiff: Optional[skyfi.GeoTIFF], in_envi: Optional[skyfi.ENVI]
    ) -> Tuple[Optional[skyfi.GeoTIFFOutput], Optional[skyfi.ENVIOutput]]:
        tiff_output = None
        if in_tiff:
            tiff_output = skyfi.GeoTIFFOutput(
                name="output",
                value=in_tiff,
                ref_name="in_tiff",
            )

        envi_output = None
        if in_envi:
            envi_output = skyfi.ENVIOutput(
                name="output",
                value=in_envi,
                ref_name="in_envi",
            )

        return tiff_output, envi_output

    none_testargs = ["test", "--request-id", str(uuid.uuid4())]
    with patch.object(sys, 'argv', none_testargs):
        response = app.start()
        assert response.response == (None, None), "app responds when using with argv response"

    tiff_testargs = ["test", "--request-id", str(uuid.uuid4()), "--in-tiff.path", "test.tif"]
    with patch.object(sys, 'argv', tiff_testargs):
        response = app.start()
        assert response.response[0], "tiff output exists"
        assert response.response[1] is None, "envi output is None"
        assert response.response[0].value.path == "test.tif", "tiff output path is correct"

    envi_testargs = ["test", "--request-id", str(uuid.uuid4()), "--in-envi.path", "test.img"]
    with patch.object(sys, 'argv', envi_testargs):
        response = app.start()
        assert response.response[0] is None, "tiff output is None"
        assert response.response[1], "envi output exists"
        assert response.response[1].value.path == "test.img", "envi output path is correct"

    both_testargs = [
        "test", "--request-id", str(uuid.uuid4()),
        "--in-tiff.path", "test.tif",
        "--in-envi.path", "test.img"
    ]
    with patch.object(sys, 'argv', both_testargs):
        response = app.start()
        assert response.response[0], "tiff output exists"
        assert response.response[1], "envi output exists"
        assert response.response[0].value.path == "test.tif", "tiff output path is correct"
        assert response.response[1].value.path == "test.img", "envi output path is correct"
