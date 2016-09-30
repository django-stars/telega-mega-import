*Telega Megaimport*

Framework for parsing CSV, XSL, Google Spreadsheets into Django.

Install package with pip install telega_megaimport

Add 'telega_megaimport' to your project's INSTALLED_APPS

To create new parser, use ./manage.py create_parser command
Specify --appdir (directory of app, where parser should be created) and --filename (name of parser)

Inside new parser, declare cells as they go in parsed document (exact order matters!)

Every cell has next args:
- required (boolean, if cell is required for row to work correctly)
- default (arbitraty, if cell has some default value)
Available cell types: 
- EmptyColumn (for cells you want to skip)
- StringColumn (for string-containing cells; use arg 'strip' (boolean) to turn on/off strip on parse)
- IntegerColumn
- FloatColumn
- BooleanColumn (will recognize ['yes', 'y', '+', '1', 'true'] as True, ['no', 'n', '-', '0', 'false'] as False)
- ModelColumn (queryset should be declared, lookup_arg by default = 'pk', but can be changed. Returns model (one and only one!) responding by lookup)

In newly created parser:
- Override method row(values) to process result of row-parsing
- Override method *attr_name*_handler to prosess result of single cell parsing

To run new parser, use ./manage.py <parser_name> [way_to_file]
Next options are supported:
--header - Is there header in file? (default - True)
--sheet - specify .xls sheet name. Will use first one if nothing specified
--progress - set 'True' to use progressbar. Default - False. If True, progressbar module is required
--failfast - set 'True' to stop parsing on first error
--dryrun - set 'True' to perform parsing without commiting data into database
--savestats - set 'True' to collect after-parse statistics into file
--google_spreadsheet - set 'True' if you are parsing google-spreadsheet directly (gspread module required) 

Requirements:
- Django >= 1.7
- xlrd (for .xls parse)
- gspread (Optional; for parsing Spreadsheets)
- progressbar (Optional; for ProgressBar generation)

To Be Done:
- Improved test coverage
- Better documentation