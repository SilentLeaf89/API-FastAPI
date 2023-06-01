from typing import Tuple


def sorting(sort) -> Tuple[str, str]:
    if sort[0] == "-":
        order = "desc"
        sorted_field = sort[1:]
        return (order, sorted_field)
    elif sort[0] == "+":
        order = "asc"
        sorted_field = sort[1:]
        return (order, sorted_field)
    else:
        order = "desc"
        sorted_field = 'imdb_rating'
        return (order, sorted_field)
