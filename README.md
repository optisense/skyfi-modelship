# SkyFi ModelShip library

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/skyfi-modelship.svg)](https://badge.fury.io/py/skyfi-modelship)

## Introduction

**SkyFi ModelShip** is a Python library designed to help **Skyfi Insights** partners integrate privately and securely their ML models into SkyFi's infrastructure. It will simplify and optimize the service communication and provide standard input and output parameters to speed up the model development and shorten the time to market for our **Insights** partners. Become a partner for our **Insights** solution on bizdev@skyfi.com

## Key Features

- **Easy Integration:** SkyFi ModelShip will help you integrate your machine learning model into SkyFi's infrastructure using common application structure and input/output parameter types.

- **Model Versioning:** The integration can call an optional bootstrap method, where each integration can decide to check for new versions, download new weights or take other model preparation steps.


## Installation

You can install SkyFi ModelShip from PyPI using pip:

```bash
pip install skyfi-modelship
```

## Getting Started
Create a SkyFi application and decorate your functions:

```python
import skyfi_modelship as skyfi

app = skyfi.SkyfiApp()

@app.bootstrap
def download():
    """Download the model, Optional"""
    logger.info("Downloading model...")


@app.inference
def exec(image: skyfi.GeoTIFF) -> skyfi.GeoTIFFOutput:
    logger.info("Running inference... ")
    return skyfi.GeoTIFFOutput(...)

```


## ModelShip Types
The inference function should adhere to `PEP-484` and declare type hints. All types of the parameters and return types should be members of the `skyfi_modelship` package or lists of them.

### Input types
The inference decorated function will receive parameters only from the ModelShip supported input types, or lists of them. They're exported in the `skyfi_modelship` package:

- skyfi_modelship.`int` - Store an integer value.
- skyfi_modelship.`float` - Store a float value.
- skyfi_modelship.`str` - Store a str value.
- skyfi_modelship.`Polygon` - Store a polygon as a wkt string.
- skyfi_modelship.`GeoJSON` - Store a GeoJSON Feature Object.
- skyfi_modelship.`PNG` - Store a PNG image path and metadata xml.
- skyfi_modelship.`GeoTIFF` - Store a GeoTIFF image path and metadata xml.
- skyfi_modelship.`ENVI` - Store an ENVI path and header.

### Output types
The inference decorated function should return objects that are from the ModelShip output types or lists of them. They're exported in the `skyfi_modelship` package:

- skyfi_modelship.`IntOutput` - Output class for integers.
- skyfi_modelship.`FloatOutput` - Output class for floats.
- skyfi_modelship.`StrOutput` - Output class for strings.
- skyfi_modelship.`PolygonOutput` - Output class for polygons.
- skyfi_modelship.`GeoJSONOutput` - Output class for GeoJSON features.
- skyfi_modelship.`PNGOutput` - Output class for images.
- skyfi_modelship.`GeoTIFFOutput` - Output class for images.
- skyfi_modelship.`ENVIOutput` - Output class for images.

## Distribution
1. Create a `Dockerfile` for your project, e.g.:
```
FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requirements.txt main.py ./
RUN python -m pip install --no-cache-dir -v -r requirements.txt

CMD ["python", "main.py"]

```

2. Send your container image to SkyFi
Please contact bizdev@skyfi.com and discuss how we can privately access the container image.

## Examples

Check out the [example](https://github.com/optisense/skyfi-modelship/tree/main/example) directory to see a working example and get inspired!

## License

This project is licensed under the [MIT License](https://github.com/optisense/skyfi-modelship/tree/main/LICENSE).

## Contact

If you have any questions or feedback, feel free to reach out at [bizdev@skyfi.com](mailto:bizdev@skyfi.com).

---

Unlock the true potential of your models with SkyFi Insights - Get started now!
