import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.core.management import call_command


class ParserCreationTest(TestCase):
    def setUp(self):
        if hasattr(settings, "PROJECT_DIR"):
            self.dir = settings.PROJECT_DIR
        else:
            self.dir = settings.BASE_DIR
        self.filepath = os.path.join(self.dir, 'parse_test_dir')
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        self.parser_name = 'test_parser'
        if hasattr(settings, 'NEW_PARSER_NAME'):
            self.NEW_PARSER_NAME = settings.NEW_PARSER_NAME
        else:
            self.NEW_PARSER_NAME = 'new_skeleton_parser'

    def tearDown(self):
        if os.path.exists(self.filepath):
            shutil.rmtree(self.filepath, ignore_errors=True)


    def test_correct_parser_creation(self):
        call_command('create_parser')
        path = os.path.join(self.dir, self.NEW_PARSER_NAME + '.py')
        parser_exists = os.path.exists(path)
        self.assertEqual(parser_exists, True)
        os.remove(path)


    def test_correct_options_work(self):
        call_command('create_parser', appdir=self.filepath, filename=self.parser_name)
        path = os.path.join(self.filepath, 'management/commands/' + self.parser_name + '.py')
        parser_exists = os.path.exists(path)
        self.assertEqual(parser_exists, True)
        os.remove(path)
