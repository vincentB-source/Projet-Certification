# Image officielle Python
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["cd", "streamlit_app"]
CMD ["streamlit", "run", "app.py"]
