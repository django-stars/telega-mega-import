import os
import django

from distutils.version import StrictVersion
from optparse import make_option
from django.conf import settings
from django.template import Template, Context
from django.core.management.base import BaseCommand, CommandError

if hasattr(settings, 'NEW_PARSER_NAME'):
    NEW_PARSER_NAME = settings.NEW_PARSER_NAME
else:
    NEW_PARSER_NAME = 'new_skeleton_parser'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        # We keep this for backwards-compatibility with 1.7
        if StrictVersion(django.get_version()) < StrictVersion('1.8'):
            newoptions = tuple(list(self.option_list) + [
                    make_option(
                        '--appdir',
                        default='',
                        help='Name of directory, where parser should be created'
                    ),
                    make_option(
                        '--filename',
                        default=NEW_PARSER_NAME,
                        help='How to name new parser skeleton file'
                    ),
                ]
            )
            self.option_list = newoptions
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--appdir',
            default='',
            help='Name of directory, where parser should be created'
        )
        parser.add_argument(
            '--filename',
            default=NEW_PARSER_NAME,
            help='How to name new parser skeleton file'
        )

    help = """
       Create skeleton for further parser declaring.
       --appdir: specify directory of app, where parser skeleton should be created
       --filename: specify parser name
    """

    def handle(self, *args, **options):
        path = options.get('appdir')
        filename = options.get('filename') + '.py'
        new_path = self.management_path(path)
        filepath = os.path.join(new_path, filename)

        fobj = open(filepath, 'wb')

        content = self.PARSER_SKELETON

        content = content.decode('utf-8')
        template = Template(content)
        content = template.render(Context())
        content = content.encode('utf-8')
        fobj.write(content)
        fobj.close()
        print 'Skeleton parser created at {}'.format(filepath)

    def management_path(self, path):
        if path == '':
            quick_terminate = True
        else:
            quick_terminate = False
        if hasattr(settings, "PROJECT_DIR"):
            path = os.path.join(settings.PROJECT_DIR, path)
        else:
            path = os.path.join(settings.BASE_DIR, path)
        if quick_terminate:
            return path
        if not os.path.exists(path):
            raise CommandError('No such app directory was found')
        path = os.path.join(path, 'management')
        if not os.path.exists(path):
            os.makedirs(path)
            file = open(os.path.join(path, '__init__.py'), 'w')
            file.close()
        path = os.path.join(path, 'commands')
        if not os.path.exists(path):
            os.makedirs(path)
            file = open(os.path.join(path, '__init__.py'), 'w')
            file.close()
        return path

    PARSER_SKELETON = """from telega_megaimport import columns
from telega_megaimport.parser import BaseParser


class Command(BaseParser):
    \"\"\"
    New skeleton for file parser; please, describe
    fields and logic prior to running.
    WARNING: please, declare field in the same order
    they are declared in document you are wanting
    to parse; use EmptyColumn to skip columns.
    Override row(values) method to process row parsing
    results, override {attr_name}_handler(value) to
    process exact field parsing results
    \"\"\"
    pass
"""
