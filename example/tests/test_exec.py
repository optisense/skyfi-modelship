from main import exec


def test_exec(tiff_image):
    output = exec(tiff_image)
    assert output.name == "output"
    assert output.path == "./tests/data/tmp_8bit.tif"
