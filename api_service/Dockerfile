FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 9000

ARG USER=app
ARG APP_DIR=api

RUN useradd --create-home --no-log-init --system --user-group ${USER}

WORKDIR /home/${USER}/${APP_DIR}

RUN apt update && apt upgrade -y && apt install -y netcat

COPY src/ .

RUN pip install --requirement requirements.txt

COPY docker-entrypoint.sh .

RUN chown -R app:app /home/${USER}/${APP_DIR}

USER ${USER}

ENTRYPOINT ["/home/app/api/docker-entrypoint.sh"]