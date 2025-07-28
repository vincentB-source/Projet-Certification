# Image officielle Python
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["cd", "fastapi_app"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
