def search_movie_query(query):
    return {"size": 100,
              "query": {
                "multi_match": {
                  "query": query,
                    # где ищем и чему уделяем бОльшее внимание
                    "fields": [
                      "title.raw^1000",
                      "title^100",
                      "description^10"
                    ],
                    # допускаем одну опечатку
                    "fuzziness": 1
                }
              },
              # забираем только _id фильмов
              "_source": ["id"]
            }
