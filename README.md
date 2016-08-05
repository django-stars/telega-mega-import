*Telega Megaimport*

Framework for parsing CSV, XSL, Google Spreadsheets into Django.

To create new parser, use ./manage.py create_parser --path=path/to/file, --filename=parser_name
Inside new parser, declare cells as they go in parsed document (exact order matters!)

Every cell has next args:
- required (boolean, if cell is required for row to work correctly)
- default (arbitraty, if cell has some default value)
Available cell types: 
- CellEmpty (for cells you want to skip)
- CellString (for string-containing cells; use arg 'strip' (boolean) to turn on/off strip on parse)
- CellInteger
- CellFloat
- CellBoolean (will recognize ['yes', 'y', '+', '1', 'true'] as True, ['no', 'n', '-', '0', 'false'] as False)
- CellModel (queryset should be declared, lookup_arg by default = 'pk', but can be changed. Returns model (one and only one!) responding by lookup)

In newly created parser:
- Override method row(values) to process result of row-parsing
- Override method *attr_name*_handler to prosess result of single cell parsing

Requirements:
- Django > 1.7
- openpyxl (for .xls parse)
- gspread (Optional; for parsing Spreadsheets)
- progressbar (Optional; for ProgressBar generation)

To Be Done:
- Improved test coverage
- Better documentation