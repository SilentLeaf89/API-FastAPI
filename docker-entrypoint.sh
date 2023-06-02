#!/bin/sh

# settings
elasticdump \
  --input=../data/settings_movies.json \
  --output=http://elastic:9200/movies \
  --type=settings --csvHandleNestedData

elasticdump \
  --input=../data/settings_person.json \
  --output=http://elastic:9200/person \
  --type=settings --csvHandleNestedData

elasticdump \
  --input=../data/settings_genres.json \
  --output=http://elastic:9200/genres \
  --type=settings --csvHandleNestedData

# mappings
elasticdump \
  --input=../data/mapping_movies.json \
  --output=http://elastic:9200/movies \
  --type=mapping --csvHandleNestedData

elasticdump \
  --input=../data/mapping_person.json \
  --output=http://elastic:9200/person \
  --type=mapping --csvHandleNestedData

elasticdump \
  --input=../data/mapping_genres.json \
  --output=http://elastic:9200/genres \
  --type=mapping --csvHandleNestedData

# indeces
elasticdump \
  --input=../data/index_movies.json \
  --output=http://elastic:9200/movies \
  --type=data --csvHandleNestedData

elasticdump \
  --input=../data/index_person.json \
  --output=http://elastic:9200/person \
  --type=data --csvHandleNestedData

elasticdump \
  --input=../data/index_genres.json \
  --output=http://elastic:9200/genres \
  --type=data --csvHandleNestedData

# start app
gunicorn main:app --workers 1 --worker-class \
uvicorn.workers.UvicornWorker --bind fastapi:8000
