def search_movie_roles(role, person_id):
    return {"query": {
              "nested": {
                "path": role,
                "query": {
                  "term": {
                    role+".id": {
                      "value": person_id
                    }
                  }
                }
              }
            },
            "_source": ["id"]
            }
