FROM python:3.8.3-alpine
WORKDIR /usr/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add postgresql-dev gcc python3-dev musl-dev && \
    pip install --upgrade pip

COPY ./requirements ./requirements
RUN pip install -r requirements/production.txt

COPY ./entrypoint.sh .

COPY . .

EXPOSE 8000

# run entrypoint.sh
ENTRYPOINT ["/usr/app/entrypoint.sh"]

CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000 -p 8000 --reload



