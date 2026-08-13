FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt main.py ./
RUN python -m pip install --no-cache-dir -v -r requirements.txt

CMD ["python", "main.py"]
