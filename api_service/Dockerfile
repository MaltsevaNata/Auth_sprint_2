FROM python:3.9.1

ENV PYTHONDONTWRITEBYTECODE=1

ARG USER=app
ARG APP_DIR=api

RUN useradd --create-home --no-log-init --system --user-group ${USER}

WORKDIR /home/${USER}/${APP_DIR}

RUN apt update && apt upgrade -y && apt install -y netcat

ADD src/ .

RUN pip install --requirement requirements.txt

ADD docker-entrypoint.sh .

EXPOSE 8000

RUN chown -R app:app /home/${USER}/${APP_DIR}

USER ${USER}

ENTRYPOINT ["/home/app/api/docker-entrypoint.sh"]