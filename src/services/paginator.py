from typing import List


class Paginator:
    def __init__(self,
                 items: List,
                 page_number: int = 1,
                 page_size: int = 50
                 ):
        self.page_number = page_number
        self.page_size = page_size
        self.items = items

    def paginate(self) -> List:
        # отдать нужную часть ответа в зависимости от page_number и page_size
        if self.page_number * self.page_size < len(self.items):
            return self.items[
                (self.page_number-1) * self.page_size:
                self.page_number * self.page_size
                ]
        else:
            return self.items[
                (self.page_number-1) * self.page_size:
                ]
