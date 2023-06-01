#!/bin/sh

# settings
elasticdump \
  --input=../data/settings_movies.json \
  --output=http://elastic:9200/movies \
  --type=settings

elasticdump \
  --input=../data/settings_person.json \
  --output=http://elastic:9200/person \
  --type=settings

elasticdump \
  --input=../data/settings_genres.json \
  --output=http://elastic:9200/genres \
  --type=settings

# mappings
elasticdump \
  --input=../data/mapping_movies.json \
  --output=http://elastic:9200/movies \
  --type=mapping

elasticdump \
  --input=../data/mapping_person.json \
  --output=http://elastic:9200/person \
  --type=mapping

elasticdump \
  --input=../data/mapping_genres.json \
  --output=http://elastic:9200/genres \
  --type=mapping

# indeces
elasticdump \
  --input=../data/index_movies.json \
  --output=http://elastic:9200/movies \
  --type=data

elasticdump \
  --input=../data/index_person.json \
  --output=http://elastic:9200/person \
  --type=data

elasticdump \
  --input=../data/index_genres.json \
  --output=http://elastic:9200/genres \
  --type=data

# start app
gunicorn main:app --workers 1 --worker-class \
uvicorn.workers.UvicornWorker --bind fastapi:8000
