def search_movie_query(
        query: str,
        page_number: int,
        page_size: int
        ):
    return \
        {
          "from": str((page_number-1) * page_size),
          "size": str(page_size),
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
          }
        }
