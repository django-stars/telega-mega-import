from django.core.exceptions import ObjectDoesNotExist


class BaseColumn(object):
    """
    Base class for inheritance for Cell creation

    Don't forget to override kls.normalize(value) and
    kls.validate(value) if required
    """
    # Counter is added for ordering of field-declaration
    creation_counter = 0

    def __init__(self, required=True, default=None):
        if default and required:
            raise ValueError('Default value and required value can\'t be combined!')
        # Hack, is used for sorting in parser-creator
        self.creation_order = BaseColumn.creation_counter
        BaseColumn.creation_counter += 1
        self.title = None
        self.required = required
        self.default = default

    def __repr__(self):
        return "<{}: {}{}>".format(
            self.__class__.__name__,
            self.title,
            [" ","*"][int(self.required)],
        )

    def normalize(self, value):
        return value

    def validate(self, value):
        # Return None if all is OK,
        # Return list of strings with error description in other case.
        if self.required and value is None:
            return ['Empty value']
        return None


class EmptyColumn(BaseColumn):
    """
    EmptyColumn: use it for declaration of empty columns in yor file
    """
    def normalize(self, value):
        return None

    def validate(self, value):
        return None


class StringColumn(BaseColumn):
    """
    Use for parsing string values; converts parse results to
    string.
    """
    def __init__(self, strip=False, *args, **kwargs):
        self.strip = strip
        super(StringColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        return value.strip() if self.strip and value else value

    def validate(self, value):
        error = super(StringColumn, self).validate(value) or []
        if not isinstance(value, basestring):
            error += ['Not convertable to string value']
        if error:
            return error
        else:
            return None


class BooleanColumn(BaseColumn):
    """
    Use for parsing boolean values;
    True = 'yes', 'y', '+', '1', 'true'
    False = 'no', 'n', '-', '0', 'false'
    Returns boolean value.
    """
    true_values = ['yes', 'y', '+', '1', 'true']
    false_values = ['no', 'n', '-', '0', 'false']

    def normalize(self, value):
        value = value.lower() if not isinstance(value, bool) else value
        if value in self.true_values:
            return True
        elif value in self.false_values:
            return False

    def validate(self, value):
        error = super(BooleanColumn, self).validate(value) or []
        value = value.lower() if not isinstance(value, bool) else value
        if value not in self.true_values + self.false_values:
            error += ['Value cannot be parsed as boolean']
        if error:
            return error
        else:
            return None


class IntegerColumn(BaseColumn):
    """
    Use for parsing integer values;
    Retunrns integer
    """

    def normalize(self, value):
        try:
            return int(value)
        except ValueError:
            return value

    def validate(self, value):
        error = super(IntegerColumn, self).validate(value) or []
        try:
            int(value)
        except ValueError:
            error += ['Not convertable to integer']
        if error:
            return error
        else:
            return None


class FloatColumn(BaseColumn):
    """
    Use for parsing float values;
    Retunrns float
    """

    def normalize(self, value):
        try:
            return float(value)
        except ValueError:
            return value

    def validate(self, value):
        error = super(FloatColumn, self).validate(value) or []
        try:
            float(value)
        except ValueError:
            error += ['Not convertable to float']
        if error:
            return error
        else:
            return None


class ModelColumn(BaseColumn):
    """
    Use for parsing direct model association. Always set queryset;
    default lookup argument - primary key.
    Returns model instance.
    """
    def __init__(self, queryset=None, lookup_arg='pk', *args, **kwargs):
        self.queryset = queryset
        if queryset is None:
            raise ValueError('Queryset is required!')
        self.lookup_arg = lookup_arg
        super(ModelColumn, self).__init__(*args, **kwargs)

    def normalize(self, value):
        try:
            return self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            return value

    def validate(self, value):
        error = super(ModelColumn, self).validate(value) or []
        try:
            return self.queryset.get(**{self.lookup_arg: value})
        except ObjectDoesNotExist:
            error += ['Object not found']
        if error:
            return error
        else:
            return None
