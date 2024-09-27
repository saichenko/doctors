FROM python:3.11-slim

WORKDIR /app

COPY . /app
COPY pyproject.toml .

RUN apt-get update && apt-get -y install libpq-dev gcc

RUN pip install poetry

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Set PYTHONPATH to ensure Python can find the src package
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python3", "src/main.py"]
