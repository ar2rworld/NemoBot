# syntax=docker/dockerfile:1
FROM python:3.11.4

WORKDIR /usr/src/app

RUN mkdir src
COPY ./src /src/
RUN mkdir tests
COPY ./tests /tests/
COPY NemoBot.py NemoBot.py

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN pip install "poetry==1.5.1"
RUN poetry install

CMD ["poetry", "run", "python", "NemoBot.py"]
