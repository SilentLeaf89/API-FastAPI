def search_roles_from_movie(person_id):
    return \
{
"query": {
  "bool": {
    "should": [
    {
      "nested": {
        "path": "actors",
        "query": {
          "term": {
            "actors.id": {
              "value": person_id
            }
          }
        }
      }
    },
    {
      "nested": {
        "path": "directors",
        "query": {
          "term": {
            "directors.id": {
              "value": person_id
            }
          }
        }
      }
    },
    {
      "nested": {
        "path": "writers",
        "query": {
          "term": {
            "writers.id": {
              "value": person_id
            }
          }
        }
      }
    }
    ],
    "minimum_should_match":1
    }
  },
  "_source": ["actors.id", "directors.id", "writers.id"]
}
