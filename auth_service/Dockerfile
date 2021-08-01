FROM python:3.9-slim

ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./src .

COPY ./utils ./utils
COPY ./entrypoint.sh .

RUN mkdir -p /usr/local/var/log/gunicorn/

ENTRYPOINT [ "./entrypoint.sh" ]
