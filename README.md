Базовый функционал для API кинотеатра.


Инструкция по запуску:
  - подготовьте переменные окружения и расположите их в /env
  - запустите docker compose в Async_API_sprint_1
  - перейдите по адресу swagger-а: http://<хост>:<порт>/api/openapi
  - протестируйте доступное API.
  - основной сайт доступен через nginx по адресам:
      http://127.0.0.1:80/api/v1/movies/?sort=-imdb_rating&page_number=1&page_size=50

      http://127.0.0.1:80/api/v1/genres
      
      и т.д.

  - очистить кэш Redis: docker exec -it redis-7.0 redis-cli FLUSHALL
