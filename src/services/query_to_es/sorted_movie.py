def sorted_movie_query(order: str, sorted_field: str):
    return {
            "sort": [
              {
                sorted_field: {
                  "order": order
                }
              }
            ],
            "_source": ["id"]
          }
