import sys
from unittest.mock import patch
import uuid

import pytest
import skyfi_modelship as skyfi


def test_app_no_request_id():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference() -> skyfi.FloatOutput:
        return skyfi.FloatOutput(value=42, name="output_num", ref_name="num_poly")

    testargs = [
        "test", "--output_folder", "/tmp/skyfi",
    ]
    with patch.object(sys, 'argv', testargs):
        with pytest.raises(Exception):
            app.start()


def test_app_no_output_folder():
    app = skyfi.SkyfiApp()

    @app.inference
    def inference() -> skyfi.FloatOutput:
        return skyfi.FloatOutput(value=42, name="output_num", ref_name="num_poly")

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test", "--request_id", str(request_id),
    ]
    # output folder is optional
    with patch.object(sys, 'argv', testargs):
        response = app.start()
        assert response, "app responds when using with argv response"
