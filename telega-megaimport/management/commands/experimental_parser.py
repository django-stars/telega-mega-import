from megaimport import cells
from megaimport.parser import BaseParser


class Command(BaseParser):
    """
    New skeleton for file parser; please, describe
    fields and logic prior to running
    """
    STRUCTURE = {
        0: cells.CellString(title='first_name'),
        1: cells.CellString(title='last_name'),
        2: cells.CellFloat(title='age', required=False),
        3: cells.CellBoolean(title='is_male', required=False),
        4: cells.CellInteger(title='days_online', required=False),
    }

    def row(self, values):
        print values

