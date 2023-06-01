def search_person_query(query):
    return {
              "query": {
                  "match": {
                    "full_name": query
                  }
              }
            }
