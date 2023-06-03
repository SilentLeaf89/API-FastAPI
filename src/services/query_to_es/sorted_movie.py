def sorted_movie_query(
        order: str,
        sorted_field: str,
        page_number: int,
        page_size: int
        ):
    return \
        { "from": str((page_number-1) * page_size),
          "size": str(page_size),
          "sort": [
            {
              sorted_field: {
                "order": order
              }
            }
          ]
        }
