FROM python:3.11-slim

WORKDIR /code

COPY poetry.lock pyproject.toml /code/

RUN pip install poetry=="1.8.3"

RUN poetry export -f requirements.txt -o requirements.txt

RUN pip install -r requirements.txt

COPY . .