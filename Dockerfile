FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src/ ./src/

COPY data/ ./data/

CMD ["python", "src/main.py"]