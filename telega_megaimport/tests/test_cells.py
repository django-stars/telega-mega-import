from django.conf import settings
from django.test import TestCase

from telega_megaimport import cells
from telega_megaimport.tests.models import BasicModel


class CellBaseTest(TestCase):
    def setUp(self):
        self.cell_1 = cells.CellBase(required=True)
        self.cell_1.title = 'Title'
        self.cell_2 = cells.CellBase(required=False)
        self.cell_2.title = 'Title2'

    def test_misdeclaration(self):
        error = None
        try:
            cells.CellBase(required=True, default='test')
        except BaseException, e:
            error = e
        self.assertIsInstance(error, ValueError)

    def test_representation(self):

        self.assertEqual(self.cell_1.__repr__(), '<CellBase: Title*>')
        self.assertEqual(self.cell_2.__repr__(), '<CellBase: Title2 >')

    def test_normalization(self):
        result = self.cell_1.normalize('test')
        self.assertEqual(result, 'test')

    def test_validation(self):
        result = self.cell_1.validate(None)
        self.assertEqual(result, ['Empty value'])
        result = self.cell_1.validate('test')
        self.assertEqual(result, None)

class CellEmptyTest(TestCase):
    def setUp(self):
        self.cell = cells.CellEmpty()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('test'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), None)

class CellStringTest(TestCase):
    def setUp(self):
        self.cell = cells.CellString(required=False)
        self.strip_cell = cells.CellString(required=False, strip=True)

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('  test     '), '  test     ')
        self.assertEqual(self.strip_cell.normalize('  test     '), 'test')

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), None)
        self.assertEqual(self.cell.validate(11), ['Not convertable to string value'])


class CellIntegerTest(TestCase):
    def setUp(self):
        self.cell = cells.CellInteger()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('111'), 111)
        self.assertEqual(self.cell.normalize('ttt'), 'ttt')

    def test_validate(self):
        self.assertEqual(self.cell.validate('111'), None)
        self.assertEqual(self.cell.validate('ttt'), ['Not convertable to integer'])


class CellBooleanTest(TestCase):
    def setUp(self):
        self.cell = cells.CellBoolean()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('+'), True)
        self.assertEqual(self.cell.normalize('-'), False)
        self.assertEqual(self.cell.normalize('test'), None)

    def test_validate(self):
        self.assertEqual(self.cell.validate('test'), ['Value cannot be parsed as boolean'])
        self.assertEqual(self.cell.validate('+'), None)

class CellFloatTest(TestCase):
    def setUp(self):
        self.cell = cells.CellFloat()

    def test_normalize(self):
        self.assertEqual(self.cell.normalize('111.111'), 111.111)
        self.assertEqual(self.cell.normalize('ttt'), 'ttt')

    def test_validate(self):
        self.assertEqual(self.cell.validate('111.111'), None)
        self.assertEqual(self.cell.validate('ttt'), ['Not convertable to float'])

class CellModelTest(TestCase):
    def setUp(self):
        self.cell = cells.CellModel(queryset=BasicModel.objects.all())
        self.cell_text = cells.CellModel(queryset=BasicModel.objects.all(), lookup_arg='text__contains')
        self.model_1 = BasicModel.objects.create(text='tralala')
        self.model_2 = BasicModel.objects.create(text='trololo')

    def test_misdeclaration(self):
        error = None
        try:
            cells.CellModel(required=True)
        except BaseException, e:
            error = e
        self.assertIsInstance(error, ValueError)

    def test_normalize(self):
        self.assertEqual(self.cell.normalize(self.model_1.pk), self.model_1)
        self.assertEqual(self.cell_text.normalize(self.model_2.text), self.model_2)
        self.assertEqual(self.cell.normalize(1010101), 1010101)

    def test_validate(self):
        self.assertEqual(self.cell.validate(self.model_1.pk), self.model_1)
        self.assertEqual(self.cell.validate(101010101), ['Object not found'])
