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
       Create parser skeleton for selected kind of files
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

        with open('megaimport/skeleton_template', 'rb') as template_file:
            content = template_file.read()

        content = content.decode('utf-8')
        template = Template(content)
        content = template.render(Context())
        content = content.encode('utf-8')
        fobj.write(content)
        fobj.close()
        print 'Skeleton parser created at {}'.format(filepath)
