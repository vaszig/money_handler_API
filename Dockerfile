FROM python:3.8-alpine

ADD requirements.txt /app/requirements.txt

RUN set -ex\
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

ADD . .

CMD python3 manage.py migrate && gunicorn money_handler.wsgi:application --bind 0.0.0.0:$PORT