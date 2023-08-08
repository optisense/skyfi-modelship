import pytest

import skyfi_modelship as skyfi


@pytest.fixture
def tiff_image():
    return skyfi.Image(
        path="./tests/data/tmp.tif",
        type=skyfi.ImageType.GEOTIFF,
    )
