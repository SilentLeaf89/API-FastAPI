import uuid


def genre_sorted_movie_query(
        order: str,
        sorted_field: str,
        page_number: int,
        page_size: int,
        genre: uuid.UUID):
    return  {
              "from": str((page_number-1) * page_size),
              "size": str(page_size),
              "query": {
                "bool": {
                  "must": [
                    {"nested": {
                        "path": "genre",
                        "query": {
                          "match_phrase": {
                            "genre.id": genre
                          }
                        }
                      }
                    }
                  ]
                }
              },
              "sort": [
                {
                  sorted_field: {
                    "order": order
                  }
                }
              ]
            }
