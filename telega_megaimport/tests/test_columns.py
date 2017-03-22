from datetime import datetime

from django.test import TestCase

from telega_megaimport import columns
from telega_megaimport.tests.models import BasicModel


class BaseColumnTest(TestCase):
    def setUp(self):
        self.cell_1 = columns.BaseColumn(required=True)
        self.cell_1.title = 'Title'
        self.cell_2 = columns.BaseColumn(required=False)
        self.cell_2.title = 'Title2'

    def test_misdeclaration(self):
        error = None
        try:
            columns.BaseColumn(required=True, default='test')
        except BaseException, e:
            error = e
        self.assertIsInstance(error, ValueError)

    def test_representation(self):

        self.assertEqual(self.cell_1.__repr__(), '<BaseColumn: Title*>')
        self.assertEqual(self.cell_2.__repr__(), '<BaseColumn: Title2 >')

    def test_normalization(self):
        result = self.cell_1.normalize('test')
        self.assertEqual(result, 'test')

    def test_validation(self):
        result = self.cell_1.validate(None)
        self.assertEqual(result, ['Empty value'])
        result = self.cell_1.validate('test')
        self.assertEqual(result, None)


class EmptyColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.EmptyColumn()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('test'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), None)


class StringColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.StringColumn(required=False)
        self.strip_cell = columns.StringColumn(required=False, strip=True)

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('  test     '), '  test     ')
        self.assertEqual(self.strip_cell.normalize('  test     '), 'test')

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), None)
        self.assertEqual(self.cell.validate(11), ['Not convertable to string value'])


class IntegerColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.IntegerColumn()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('111'), 111)
        self.assertEqual(self.cell.normalize('ttt'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('111'), None)
        self.assertEqual(self.cell.validate('ttt'), ['Not convertable to integer'])


class BooleanColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.BooleanColumn()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('+'), True)
        self.assertEqual(self.cell.normalize('-'), False)
        self.assertEqual(self.cell.normalize('test'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), ['Value cannot be parsed as boolean'])
        self.assertEqual(self.cell.validate('+'), None)


class FloatColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.FloatColumn()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('111.111'), 111.111)
        self.assertEqual(self.cell.normalize('ttt'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('111.111'), None)
        self.assertEqual(self.cell.validate('ttt'), ['Not convertable to float'])


class DateTimeColumn(TestCase):
    def setUp(self):
        self.cell = columns.DateTimeColumn(dayfirst=True)
        self.fuzzy_cell = columns.DateTimeColumn(dayfirst=True, fuzzy=True)

    def test_normalize(self):
        fool_day = datetime(day=1, year=2017, month=4)
        self.assertEqual(self.cell.normalize('1/4/2017'), fool_day)
        self.assertRaises(ValueError, self.cell.normalize, 'aaa')
        self.assertEqual(self.fuzzy_cell.normalize('Aprils fools day is 1/4/2017'), fool_day)

    def test_validate(self):
        self.assertEqual(self.cell.validate('1/4/2017'), None)
        self.assertEqual(self.cell.validate('ttt'), ['Unknown string format'])



class ModelColumnTest(TestCase):
    def setUp(self):
        self.cell = columns.ModelColumn(queryset=BasicModel.objects.all())
        self.cell_text = columns.ModelColumn(queryset=BasicModel.objects.all(), lookup_arg='text__contains')
        self.model_1 = BasicModel.objects.create(text='tralala')
        self.model_2 = BasicModel.objects.create(text='trololo')

    def test_misdeclaration(self):
        error = None
        try:
            columns.ModelColumn(required=True)
        except BaseException, e:
            error = e
        self.assertIsInstance(error, ValueError)

    def test_normalize(self):
        self.assertEqual(self.cell.normalize(self.model_1.pk), self.model_1)
        self.assertEqual(self.cell_text.normalize(self.model_2.text), self.model_2)
        self.assertEqual(self.cell.normalize(1010101), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate(self.model_1.pk), None)
        self.assertEqual(self.cell.validate(101010101), ['Object not found'])
