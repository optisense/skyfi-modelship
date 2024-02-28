import pytest

import skyfi_modelship as skyfi


@pytest.fixture
def tiff_image():
    return skyfi.GeoTIFF(
        path="./tests/data/tmp.tif",
    )
