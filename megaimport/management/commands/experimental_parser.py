from megaimport import cells
from megaimport.parser import BaseParser


class Command(BaseParser):

    """
    New skeleton for file parser; please, describe
    fields and logic prior to running
    """
    first_name = cells.CellString()
    last_name = cells.CellString()
    age = cells.CellFloat(required=False)
    is_male = cells.CellBoolean(required=False)
    blanch = cells.EmptyCell()
    days_online = cells.CellInteger(required=False)


    def row(self, values):
        print values
