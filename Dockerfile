FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1 

COPY ./requirements.txt /requirements.txt

RUN apk update \
    && apk add --virtual .tmp gcc musl-dev \
    && apk add nodejs npm curl \
    && npm install elasticdump -g \
    && mkdir -p /opt/fastapi \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .tmp

RUN addgroup -g 1000 app \
    && adduser -u 1000 -G app -s /bin/sh -D app\
    && chown -R app /opt/fastapi

USER app

WORKDIR /opt/fastapi

COPY --chown=app:app . .

WORKDIR /opt/fastapi/src

ENTRYPOINT ["/opt/fastapi/docker-entrypoint.sh"]
