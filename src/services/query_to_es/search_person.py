def search_person_query(
        query: str,
        page_number: int,
        page_size: int
        ):
    return {
              "from": str((page_number-1) * page_size),
              "size": str(page_size),
              "query": {
                  "match": {
                    "full_name": query
                  }
              }
            }
