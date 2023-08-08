# Example integration with the SkyFi ModelShip


1. Create an application
```python
import skyfi_modelship as skyfi

app = skyfi.SkyfiApp()
```

2. (Optional) Define a bootstrap function
```python
@app.bootstrap
def download():
    """Download the model."""
    logger.info("Downloading model...")
```

3. Define the inference function
```python
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
    ...
    return image_output, float_output, polygon_output```
```

4. Start the application
```python
app.start()
```

5. Create `requirements.txt`:
```bash
$ poetry export --without-hashes -o requirements.txt
```

6. Create a `Dockerfile`:
```Dockerfile
FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requirements.txt main.py ./
RUN python -m pip install --no-cache-dir -v -r requirements.txt

CMD ["python", "main.py"]
```

7. Build and create a docker
```bash
$ docker build . -t skyfi-modelship-example
```

## You're ready
Now you have the image that can be used at **SkyFi's Insights** infrastructure.

## Execution
To perform a test request using the `fastapi` handler, you can:

1. start the container with:

```bash
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/app/skyfi-service-account.json -e SKYFI_IS_FASTAPI_SERVER=true -e SKYFI_FASTAPI_HOST=0.0.0.0 -e SKYFI_FASTAPI_PORT=8000 -p 8000:8000 -it -v $(pwd)/google_service_account.json:/app/skyfi-service-account.json skyfi-modelship-example
```

N.B. the `GOOGLE_APPLICATION_CREDENTIALS` env variable and the google service account mount are necessary only if there'll be some files to upload/download on **GCS**

2. Run a test request:
```json
POST http://localhost:8000

{
    "request_id": "119e16f9-03f8-4df7-841b-627c5d7838fa",
    "output_folder": "gs://<BUCKET_ID>/output_folder",
    "int_number": 42,
    "tiff_image": {
        "path": "gs://<BUCKET_ID>/<TIFF_FILENAME>", "type": "GEOTIFF"
    },
    "poly": "POLYGON((-99 37,-98 35,-96 35,-96 38,-99 37))"
}
```

3. Example output:
```json
{
  "request_id": "119e16f9-03f8-4df7-841b-627c5d7838fa",
  "output_folder": "gs://<BUCKET_ID>/output_folder",
  "response": [
    {
      "path": "gs://<BUCKET_ID>/output_folder/<TIFF_FILENAME>_exec_output_for_tiff_image.tif",
      "type": "GEOTIFF",
      "name": "output",
      "ref_name": "tiff_image",
      "tags": [
        "test1",
        "test2",
        "45.14"
      ],
      "metadata": null,
      "output_type": "Image"
    },
    {
      "value": 45.14,
      "name": "idx",
      "ref_name": "tiff_image",
      "tags": [
        "test1",
        "test2",
        "45.14"
      ],
      "metadata": null,
      "output_type": "Float"
    },
    {
      "wkt": "POLYGON((-99 37,-98 35,-96 35,-96 38,-99 37))",
      "name": "poly",
      "ref_name": "tiff_image",
      "tags": [
        "test1",
        "test2",
        "45.14"
      ],
      "metadata": null,
      "output_type": "Polygon"
    }
  ]
}
```
