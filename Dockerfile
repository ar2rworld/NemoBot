# syntax=docker/dockerfile:1
FROM python:3.7

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "NemoBot.py"]
