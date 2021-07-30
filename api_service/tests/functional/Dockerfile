FROM python:3.9.1

WORKDIR tests

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

ADD . .

ENTRYPOINT ["/bin/sh", "-c", "python3 ./utils/ping.py && pytest src"]
