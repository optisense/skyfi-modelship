FROM python:3.14-slim

RUN useradd --create-home --uid 10001 app

WORKDIR /app

COPY requirements.txt main.py ./
RUN python -m pip install --no-cache-dir -v -r requirements.txt

USER app

CMD ["python", "main.py"]
