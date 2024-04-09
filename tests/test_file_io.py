import sys
from unittest.mock import patch

import uuid
import skyfi_modelship as skyfi


def test_app_file_io(mocker):
    app = skyfi.SkyfiApp()

    @app.inference
    def inference(io_file: skyfi.File) -> skyfi.FileOutput:
        assert io_file.path == "/local-path/input.txt", "io_file.path is correct"
        return skyfi.FileOutput(value=io_file, name="output_file", ref_name="io_file")

    request_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    testargs = [
        "test",
        "--request-id",
        str(request_id),
        "--output-folder",
        "gs://remote-path/skyfi",
        "--io-file.path",
        "gs://home/skyfi/input.txt"
    ]

    mocker.patch("skyfi_modelship.util.model_transformer.download",
                 return_value="/local-path/input.txt")
    mocker.patch("skyfi_modelship.util.model_transformer.upload",
                 return_value="gs://remote-path/skyfi/output.txt")
    with patch.object(sys, "argv", testargs):
        response = app.start()
        assert response.request_id == request_id
        assert response.response.name == "output_file"
        assert response.response.value.path == "gs://remote-path/skyfi/output.txt"
