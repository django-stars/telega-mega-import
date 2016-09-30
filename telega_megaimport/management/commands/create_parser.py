import os

from optparse import make_option
from django.conf import settings
from django.template import Template, Context
from django.core.management.base import BaseCommand

if hasattr(settings, 'NEW_PARSER_NAME'):
    NEW_PARSER_NAME = settings.NEW_PARSER_NAME
else:
    NEW_PARSER_NAME = 'new_skeleton_parser'


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--path',
            default='',
            help='Where to create new parser skeleton'
        ),
        make_option(
            '--filename',
            default=NEW_PARSER_NAME,
            help='How to name new parser skeleton file'
        ),
    )
    help = """
       Create skeleton for further parser declaring.
       --path: specify path, where parser skeleton should be created
       --filename: specify parser name
    """

    def handle(self, *args, **options):
        path = options.get('path')
        filename = options.get('filename') + '.py'
        if hasattr(settings, "PROJECT_DIR"):
            filepath = os.path.join(settings.PROJECT_DIR, path)
        else:
            filepath = os.path.join(settings.BASE_DIR, path)
        filepath = os.path.join(filepath, filename)
        fobj = open(filepath, 'wb')

        content = self.PARSER_SKELETON

        content = content.decode('utf-8')
        template = Template(content)
        content = template.render(Context())
        content = content.encode('utf-8')
        fobj.write(content)
        fobj.close()
        print 'Skeleton parser created at {}'.format(filepath)

    PARSER_SKELETON = """
    from megaimport import cells
    from megaimport.parser import BaseParser
    from django.core.management import BaseCommand


    class Command(BaseParser):
        \"\"\"
        New skeleton for file parser; please, describe
        fields and logic prior to running.
        WARNING: please, declare field in the same order
        they are declared in document you are wanting
        to parse; use CellEmpty to skip cells.
        Override row(values) method to process row parsing
        results, override attr_name_handler(value) to
        process exact field parsing results
        \"\"\"
        pass
    """
