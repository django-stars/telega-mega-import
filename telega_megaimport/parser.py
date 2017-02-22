import csv
import time
import django
import os.path

from optparse import make_option
from columns import BaseColumn, EmptyColumn
from collections import OrderedDict
from xlrd import open_workbook
from django.core.management import BaseCommand, CommandError
from django.utils.six import with_metaclass
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from distutils.version import StrictVersion

from utils import UnicodeWriter


class ParserMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['fields'] = OrderedDict()
        built_fields = {}
        for field_name, obj in attrs.items():
            if isinstance(obj, BaseColumn):
                field = attrs[field_name]
                field.title = field_name
                built_fields[field_name] = field
        sorted_built_fields = OrderedDict(sorted(built_fields.items(), key=lambda x: x[1].creation_order))
        attrs['fields'].update(sorted_built_fields)
        return super(ParserMetaclass, cls).__new__(cls, name, bases, attrs)


class BaseParser(with_metaclass(ParserMetaclass, BaseCommand)):
    def __init__(self, *args, **kwargs):
        super(BaseParser, self).__init__(*args, **kwargs)
        # For compatibility with Django 1.7
        self.is_old_django = False
        if StrictVersion(django.get_version()) < StrictVersion('1.8'):
            self.is_old_django = True
            self.args = '<input_file>'
            self.option_list = list(self.option_list) + [
                make_option(
                    '--header',
                    default=True,
                    help='If there is header in the file'
                ),
                make_option(
                    '-s',
                    '--sheet',
                    help='Set exact sheet for xlsx file'
                ),
                make_option(
                    '--progress',
                    default=False,
                    help='Show progress bar? (progressbar package required)'
                ),
                make_option(
                    '--failfast',
                    default=False,
                    help='Break parsing on first error-case?'
                ),
                make_option(
                    '--dryrun',
                    default=False,
                    help='Do parsing without DB changes?'
                ),
                make_option(
                    '--savestats',
                    default=False,
                    help='Do save statistics to file?'
                ),
                make_option(
                    '--google_spreadsheet',
                    default=False,
                    help='Are you parsing Google Spreadsheet directly? Gspread required')
            ]

    help = """
       Parse data
    """

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_file', nargs='?', type=str)

        # Named (optional) arguments
        parser.add_argument(
            '--header',
            default=True,
            help='Is there header in file?',
        )
        parser.add_argument(
            '--sheet',
            default=None,
            help='Set exact sheet for xlsx file',
        )
        parser.add_argument(
            '--progress',
            default=False,
            help='Show progress bar? (progressbar package required)'
        )
        parser.add_argument(
            '--failfast',
            default=False,
            help='Break parsing on first error-case?'
        )
        parser.add_argument(
            '--dryrun',
            default=False,
            help='Do parsing without DB changes?'
        )
        parser.add_argument(
            '--savestats',
            default=False,
            help='Do save statistics to file?'
        )
        parser.add_argument(
            '--google_spreadsheet',
            default=False,
            help='Are you parsing Google Spreadsheet directly? Gspread required'
        )


    def handle(self, *args, **options):
        self.start_time = time.time()
        self.parsed_successfully = 0
        self.parsed_unsuccessfully = 0
        self.skipped = 0
        self.failed_rows = list()
        self.skipped_rows = list()
        self.__set_options(options)
        if self.is_old_django:
            filename = args[0]
        else:
            filename = options['input_file']
        self.__check_and_load_file(filename)
        if self.is_csv:
            self.parsed_object = open(self.filename, 'rb')
        else:
            self.__check_and_load_sheet()
        print 'Parsing file....'
        interim_data, total_rows = self.prepare_interim_data()
        if self.dryrun:
            transaction.set_autocommit(False)
        self.parse_data(interim_data, total_rows)
        self.after_parse_hook()
        self.parse_statistics()
        if self.dryrun:
            transaction.rollback()
            transaction.set_autocommit(True)

    def after_parse_hook(self):
        pass

    def prepare_interim_data(self):
        if self.is_csv:
            # Prepare progress bar data and generator for csv files
            object_generator = csv.reader(self.parsed_object, quotechar='"', delimiter=',')
            total_rows = sum(1 for line in object_generator)
            if self.header:
                self.parsed_object.seek(0)
                object_generator = csv.reader(self.parsed_object, quotechar='"', delimiter=',')
                total_rows -= 1
                next(object_generator)
        else:
            # Prepare progress bar data and generator for non-csv files
            row_offset = 1 if self.header else 0
            if self.google_spreadsheet:
                total_rows = self.parsed_object.row_count
                object_generator = self.__get_iterator_for_gsheet(offset=row_offset)
            else:
                total_rows = self.parsed_object.nrows
                object_generator = self.__get_iterator_for_xls(offset=row_offset)
            total_rows -= 1
        return object_generator, total_rows

    def parse_data(self, object_generator, total_rows):
        if self.progress:
            pbar = self.__initialize_progress_bar(total_rows)
        for index, raw_row in enumerate(object_generator):
            if len(raw_row) != len(self.fields):
                raise CommandError('Incorrect parsed file! Stopping parsing! {} != {}'.format(len(raw_row),len(self.fields)))
            if self.is_csv:
                row = map(lambda s: s.strip(), raw_row)
            else:
                row = raw_row
            # TODO: invent great way to ignore last row when there is header
            if self.header and not self.is_csv and index == total_rows:
                continue
            self.process_row(row, index)
            if self.progress:
                pbar.update(index + 1)

    def process_row(self, row, row_number):
        if self.is_csv:
            row_raw_values = [cell for cell in row]
        else:
            row_raw_values = [cell.value for cell in row]
        if not any(row_raw_values):
            print "Blank line, SKIP"
            return None

        row_values = []
        row_errors = []
        row_values = dict()
        for index, cell in enumerate(row):

            option = self.fields.values()[index]
            if isinstance(option, EmptyColumn):
                continue
            if self.is_csv:
                value = cell
            else:
                value = cell.value

            errors = option.validate(value)
            if errors:
                if self.is_csv:
                    coordinates = index
                elif self.google_spreadsheet:
                    coordinates = (cell.row, cell.col)
                else:
                    coordinates = cell.coordinate
                if self.failfast:
                    raise CommandError('Errors in cell {}: {}'.format(coordinates, errors))
                else:
                    row_errors.append({coordinates: errors})
                continue
            value = option.normalize(value)

            try:
                handler = getattr(self, '{}_handler'.format(option.title))
                value = handler(value)
            except AttributeError:
                # In case we do not define handler at all.
                pass
            row_values[option.title] = value

        if row_errors:
            print "=" * 80
            print row_errors
            print "=" * 80
        try:
            row_handler = getattr(self, 'row')
        except AttributeError:
            # We do not perform any action with row itself.
            # We need to log, that we are skip row process for row, bla, bla.
            pass
        else:
            try:
                res = row_handler(row_values)
                if res is None:
                    res = self.success('Row {} parsed successfully'.format(row_number))
            except BaseException, e:
                res = self.failure('Error during parsing row {}: {}'.format(row_number, e), row)
            self.__process_result(res)

    def success(self, message):
        result_dict = {
            'status': 'Success',
            'message': message
        }
        return result_dict

    def failure(self, message, row):
        result_dict = {
            'status': 'Failure',
            'message': message,
            'row': row,
        }
        return result_dict

    def skip(self, message):
        result_dict = {
            'status': 'Skipped',
            'message': message
        }
        return result_dict

    def parse_statistics(self):
        time_spent = time.time() - self.start_time
        result_string = 'Done!\nSuccessfully parsed {} items.\nFailed to parse {} items.\nSkipped {} items.\nTime spent:{}'.format(
            self.parsed_successfully, self.parsed_unsuccessfully, self.skipped, time_spent)
        print result_string
        if self.savestats:
            output_file_name = 'parse_statistics_' + timezone.now().strftime("%Y%m%d-%H%m") + '.txt'
            failed_csv_output_file = 'failed_rows_' + timezone.now().strftime("%Y%m%d-%H%m") + '.csv'
            result_string += '\n Failed rows saved to {}'.format(failed_csv_output_file)
            print 'Saving extended statistics to file: {}'.format(output_file_name)
            f = open(output_file_name, 'w')
            f.write(result_string)
            f.close()
            with open(failed_csv_output_file, 'wb') as csv_output:
                writer = UnicodeWriter(csv_output, quotechar='"', delimiter=';')
                output_file_name.write('Next rows failed to be parsed\n')
                for r in self.failed_rows:
                    try:
                        for i in xrange(len(r)):  # cleaner way "for x in r" fails to work
                            r[i] = r[i].decode('UTF-8')
                        writer.writerow(r)
                    except BaseException as e:
                        print e
                        print r

    def __get_iterator_for_gsheet(self, offset):
        parsed_object = self.parsed_object
        min_row = offset + 1
        max_row = parsed_object.col_values(1).index('') +1 
        max_col = parsed_object.row_values(1).index('') + 1
        min_col = 1
        for row in range(min_row, max_row):
            yield tuple(parsed_object.cell(row, column)
                        for column in range(min_col, max_col))

    def __get_iterator_for_xls(self, offset):
        parsed_object = self.parsed_object
        min_row = offset
        max_row = parsed_object.nrows
        max_col = parsed_object.ncols
        min_col = 0
        for row in range(min_row, max_row):
            yield tuple(parsed_object.cell(row, column)
                        for column in range(min_col, max_col))

    def __set_options(self, options):
        for key, value in options.items():
            if not key == 'sheet' and not isinstance(value, bool):
                if value == 'True':
                    parsed_value = True
                elif value == 'False':
                    parsed_value = False
                else:
                    parsed_value = value
            else:
                parsed_value = value
            setattr(self, key, parsed_value)


    def __check_and_load_file(self, filename):
        # We check, that file is exists and is valid and corresponding with options
        if self.google_spreadsheet:
            try:
                import gspread
            except ImportError:
                raise CommandError('Please install gspread to parse Google Spreadsheet directly!')
            try:
                credentials = settings.CREDENTIALS
            except AttributeError:
                raise CommandError('Please set credential object in settings')
            gs = gspread.authorize(credentials)
            self.work_book = gs.open(filename)
            self.is_csv = False
        else:
            self.filename = os.path.abspath(filename)
            name, extension = os.path.splitext(filename)
            if extension == '.csv':
                self.is_csv = True
            else:
                self.is_csv = False
            if not os.path.exists(self.filename):
                raise CommandError('Can\'t find given file: {}'.format(self.filename))
            if self.is_csv and self.sheet is not None:
                raise CommandError('Can\'t parse sheet for csv file!')
            elif not self.is_csv:    
                self.work_book = open_workbook(self.filename)
                raise CommandError('Wrong file format. Supported are: .xlsx, .xls')

    def __check_and_load_sheet(self):
        # We will verify and load given sheet if it's exists or use first one.
        sheet_name = self.sheet
        if sheet_name is None:
            # WARNING Explicitly take first sheet.
            if self.google_spreadsheet:
                self.parsed_object = self.work_book.get_worksheet(0)
            else:
                self.parsed_object = self.work_book.sheet_by_index(0)
            return
        elif self.google_spreadsheet:
            try:
                self.parsed_object = self.work_book.get_worksheet(sheet_name)
            except KeyError:
                raise CommandError('Given sheet name `{}` not found.'.format(sheet_name))
        else:
            from xlrd.biffh import XLRDError
            try:
                self.parsed_object = self.work_book.sheet_by_name(sheet_name)
            except XLRDError:
                raise CommandError('Given sheet name `{}` not found.'.format(sheet_name))

    def __initialize_progress_bar(self, total_rows):
        try:
            from progressbar import ProgressBar, Counter, Percentage, Bar
            widgets = ['Processed: ', Counter(), ' ', Percentage(), ' ', Bar()]
            return ProgressBar(widgets=widgets, maxval=total_rows).start()
        except ImportError:
            raise CommandError('No progressbar package found! Please, install it to track progress')

    def __process_result(self, res):
        status = res['status']
        if status == 'Success':
            self.parsed_successfully += 1
        elif status == 'Failure':
            self.parsed_unsuccessfully += 1
            self.failed_rows += res['row']
        elif status == 'Skipped':
            self.skipped += 1
        else:
            raise CommandError('Unexpected result returned')
        print res['message']