import uuid


def genre_sorted_movie_query(
        order: str,
        sorted_field: str,
        genre: uuid.UUID):
    return  {
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
              ],
              "_source": ["id"]
            }
