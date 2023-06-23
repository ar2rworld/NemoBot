# syntax=docker/dockerfile:1
# Install python/pip
FROM alpine:3.18.2
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

WORKDIR /src

COPY src ./src
COPY tests ./tests
COPY NemoBot.py .

COPY poetry.lock .
COPY pyproject.toml .
RUN pip3 install "poetry==1.5.1"
RUN poetry install

CMD ["poetry", "run", "python", "NemoBot.py"]
