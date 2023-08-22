import sys
from typing import List
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
        return skyfi.FloatOutput(
            value=num.value * 2, name="output_num", ref_name="num_poly"
        )

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test",
        "--request_id",
        str(request_id),
        "--output_folder",
        "/tmp/skyfi",
        "--num",
        "21",
        "--poly",
        "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))",
    ]
    with patch.object(sys, "argv", testargs):
        response = app.start()
        assert response.request_id == request_id
        assert response.response.name == "output_num"
        assert response.response.value == 42.0


def test_app_list_args():
    app = skyfi.SkyfiApp()

    @app.bootstrap
    def bootstrap():
        pass

    @app.inference
    def inference(
        int_list: List[skyfi.Integer]
    ) -> List[skyfi.FloatOutput]:
        return [
            skyfi.IntegerOutput(
                value=num.value * 2, name="output_ints", ref_name="int_list"
            )
            for num in int_list
        ]

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    ints = [21, 42]
    ints_args = [f"--int_list={i}" for i in ints]
    testargs = [
        "test",
        "--request_id",
        str(request_id),
        *ints_args
    ]
    with patch.object(sys, "argv", testargs):
        response = app.start()
        assert response.request_id == request_id
        for i, output in enumerate(response.response):
            assert output.name == "output_ints"
            assert output.value == ints[i] * 2


def test_app_no_bootstrap():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference() -> skyfi.FloatOutput:
        return skyfi.FloatOutput(value=42, name="output_num", ref_name="num_poly")

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test",
        "--request_id",
        str(request_id),
        "--output_folder",
        "/tmp/skyfi",
    ]
    with patch.object(sys, "argv", testargs):
        response = app.start()
        assert response.request_id == request_id
        assert response.response.name == "output_num"
        assert response.response.value == 42
