import sys
from unittest.mock import patch
import uuid
import skyfi_modelship as skyfi


def test_app_args():
    app = skyfi.SkyfiApp()

    @app.bootstrap
    def bootstrap():
        pass

    @app.inference
    def inference(num: skyfi.Float, poly: skyfi.Polygon) -> skyfi.FloatOutput:
        return skyfi.FloatOutput(value=num.value * 2, name="output_num", ref_name="num_poly")

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test",
        "--request_id", str(request_id),
        "--output_folder", "/tmp/skyfi",
        "--num", "21",
        "--poly", "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
    ]
    with patch.object(sys, 'argv', testargs):
        response = app.start()
        assert response.request_id == request_id
        assert response.response.name == "output_num"
        assert response.response.value == 42.0


def test_app_no_bootstrap():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference() -> skyfi.FloatOutput:
        return skyfi.FloatOutput(value=42, name="output_num", ref_name="num_poly")

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test",
        "--request_id", str(request_id),
        "--output_folder", "/tmp/skyfi",
    ]
    with patch.object(sys, 'argv', testargs):
        response = app.start()
        assert response.request_id == request_id
        assert response.response.name == "output_num"
        assert response.response.value == 42
