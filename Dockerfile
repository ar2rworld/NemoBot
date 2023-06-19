# syntax=docker/dockerfile:1
FROM python:3.11.4

WORKDIR /usr/src/app

COPY src ./src
COPY tests ./tests
COPY NemoBot.py NemoBot.py

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml
RUN pip install "poetry==$POETRY_VERSION"
RUN poetry install

CMD ["poetry", "run", "python", "NemoBot.py"]
