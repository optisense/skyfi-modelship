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

1. Import the necessary modules:

```python
import skyfi_modelship as skyfi
```

2. Create a SkyFi application and decorate your functions:

```python
app = skyfi.SkyfiApp()

@app.bootstrap
def download():
    """Download the model, Optional"""
    logger.info("Downloading model...")


@app.inference
def exec(fl: skyfi.Float) -> skyfi.ImageOutput:
    logger.info("Running inference... ")
    return skyfi.ImageOutput(...)

```

3. Create a `Dockerfile` for your project:
```
FROM python:3.9.5-slim-buster

WORKDIR /app

COPY requirements.txt main.py ./
RUN python -m pip install --no-cache-dir -v -r requirements.txt

CMD ["python", "main.py"]

```

4. Send your container image to SkyFi
Please contact bizdev@skyfi.com and discuss how we can privately access the container image.

## Examples

Check out the [example](example) directory to see a working example and get inspired!

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or feedback, feel free to reach out at [bizdev@skyfi.com](mailto:bizdev@skyfi.com).

---

Unlock the true potential of your models with SkyFi Insights - Get started now!
