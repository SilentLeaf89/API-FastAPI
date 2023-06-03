# Проектная работа 4 спринта

11 команда:
  - Дмитрий Гусев @SilentLeaf89

Ссылка на репозиторий:
https://github.com/SilentLeaf89/Async_API_sprint_1

Модели и схемы, используемые в API, приведены на рисунке ниже.

![Схема](schema.png)

Инструкция по запуску:
  - подготовьте переменные окружения и раположите их в /env
  - запустите docker compose в Async_API_sprint_1
  - перейдите по адресу swagger-а: http://<хост>:<порт>/api/openapi
  - протестируйте доступное API.
  - основной сайт доступен через nginx по адресам:
      http://127.0.0.1:80/api/v1/movies/?sort=-imdb_rating&page_number=1&page_size=50

      http://127.0.0.1:80/api/v1/genres
      
      и т.д.

  - очистить кэш Redis: docker exec -it redis-7.0 redis-cli FLUSHALL
