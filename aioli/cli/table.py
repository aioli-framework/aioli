import texttable


class BaseTable(texttable.Texttable):
    def __init__(self, columns, items, *args, **kwargs):
        super(BaseTable, self).__init__(*args, **kwargs)
        self.columns = columns
        self.add_row(columns)

        for item in items:
            row = list(self.get_row(item))
            self.add_row(row)

    def get_row(self, item):
        raise NotImplementedError
