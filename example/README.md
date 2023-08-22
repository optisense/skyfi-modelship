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
Now there's an image that can be used at **SkyFi's Insights** infrastructure.

## Local execution

Provide the parameters as arguments, e.g.:
```bash
python main.py --int_number 42 --fl_number 4.2 --tiff_image.path=/tmp/tmp.tiff --tiff_image.type=GEOTIFF
```

## Start a fastapi service
To perform a test request using the `fastapi` handler:

1. Start the container with:

```bash
docker run -e SKYFI_IS_FASTAPI_SERVER=true -e SKYFI_FASTAPI_HOST=0.0.0.0 -e SKYFI_FASTAPI_PORT=8000 -p 8000:8000 -it skyfi-modelship-example
```

1. Run a test request:
```json
POST http://localhost:8000

{
    "request_id": "119e16f9-03f8-4df7-841b-627c5d7838fa",
    "int_number": 42,
    "tiff_image": {
        "path": "/tmp/<TIFF_FILENAME>", "type": "GEOTIFF"
    },
    "poly": "POLYGON((-99 37,-98 35,-96 35,-96 38,-99 37))"
}
```

3. Example output:
```json
{
  "request_id": "119e16f9-03f8-4df7-841b-627c5d7838fa",
  "response": [
    {
      "path": "/tmp/<TIFF_FILENAME>_exec_output_for_tiff_image.tif",
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

3. Automatic downloads from GCS
When the reguest contains an `Image` with a `path` that's gsutil url (`gs://...`), then ModelShip will try to download it locally and substitute the `path` with the local one.

4. Automatic uploads to GCS
You can add an `output_folder` parameter to the request. Then all returned images will be uploaded to that specific folder and their `path` will be updated with the `gs://...` of the uploaded resource. e.g.:

```json
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

and output (path starts with `gs://...`):
```json

{
  "request_id": "119e16f9-03f8-4df7-841b-627c5d7838fa",
  "response": [
    {
      "path": "gs://<BUCKET_ID>/output_folder/<TIFF_FILENAME>_exec_output_for_tiff_image.tif",
      "type": "GEOTIFF",
      ...
```

5. Google Storage Credentials
When using automatic downloads or uploads to GCS, please specify a Google Storage credentials that can read/write the required resources:

```bash
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/app/skyfi-service-account.json -e SKYFI_IS_FASTAPI_SERVER=true -e SKYFI_FASTAPI_HOST=0.0.0.0 -e SKYFI_FASTAPI_PORT=8000 -p 8000:8000 -it -v $(pwd)/google_service_account.json:/app/skyfi-service-account.json skyfi-modelship-example
```

N.B. the `GOOGLE_APPLICATION_CREDENTIALS` env variable and the google service account mount are necessary only if there'll be some files to upload/download on **GCS**

